import os
import pandas as pd

def load_csv(path, required_cols):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {os.path.basename(path)} (expected at: {path})")
    df = pd.read_csv(path)
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"{os.path.basename(path)} missing columns: {missing}")
    return df

def solve_with_pulp(bom, stock, program, res_req=None, res_lim=None, data_dir="."):
    import pulp
    coach_types = sorted(program["coach_type"].unique())
    items = sorted(stock["item_code"].astype(str).unique())

    bom = bom.copy()
    bom["item_code"] = bom["item_code"].astype(str)
    bom_pivot = bom.pivot_table(index="item_code", columns="coach_type",
                                values="qty_per_coach", aggfunc="sum").fillna(0.0)
    for ct in coach_types:
        if ct not in bom_pivot.columns:
            bom_pivot[ct] = 0.0
    for it in items:
        if it not in bom_pivot.index:
            bom_pivot.loc[it, :] = 0.0
    bom_pivot = bom_pivot.loc[items, coach_types]

    stock_dict = dict(zip(stock["item_code"].astype(str), stock["on_hand_qty"].astype(float)))
    min_target = dict(zip(program["coach_type"], program["min_target"]))
    max_target = dict(zip(program["coach_type"], program["max_target"]))
    value = dict(zip(program["coach_type"], program["value_per_coach"]))

    model = pulp.LpProblem("Coach_Production_Mix", pulp.LpMaximize)
    x = {ct: pulp.LpVariable(f"x_{ct}", lowBound=0, cat=pulp.LpInteger) for ct in coach_types}

    for ct in coach_types:
        if pd.notna(min_target[ct]):
            model += x[ct] >= float(min_target[ct])
        if pd.notna(max_target[ct]) and float(max_target[ct]) >= 0:
            model += x[ct] <= float(max_target[ct])

    for it in items:
        usage = pulp.lpSum(bom_pivot.loc[it, ct] * x[ct] for ct in coach_types)
        model += usage <= float(stock_dict.get(it, 0.0))

    if res_req is not None and res_lim is not None:
        for _, row in res_lim.iterrows():
            res = row["resource"]
            lim = float(row["limit"])
            req_vec = res_req[res_req["resource"] == res].set_index("coach_type")["units_per_coach"].to_dict()
            model += pulp.lpSum(req_vec.get(ct, 0.0) * x[ct] for ct in coach_types) <= lim

    model += pulp.lpSum(value[ct] * x[ct] for ct in coach_types)
    status = model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_txt = pulp.LpStatus[status]

    sol = pd.DataFrame({
        "coach_type": coach_types,
        "qty_to_build": [int(pulp.value(x[ct]) or 0) for ct in coach_types],
        "value_per_coach": [value[ct] for ct in coach_types],
        "min_target": [min_target[ct] for ct in coach_types],
        "max_target": [max_target[ct] for ct in coach_types],
    })
    sol["total_value"] = sol["qty_to_build"] * sol["value_per_coach"]

    util_rows = []
    sol_ix = sol.set_index("coach_type")["qty_to_build"].to_dict()
    for it in items:
        used = sum(bom_pivot.loc[it, ct] * sol_ix.get(ct, 0) for ct in coach_types)
        cap = float(stock_dict.get(it, 0.0))
        util = used / cap * 100 if cap > 0 else 0.0
        util_rows.append({"item_code": it, "used_qty": used, "on_hand_qty": cap, "utilization_pct": round(util, 2)})
    util_df = pd.DataFrame(util_rows).sort_values("utilization_pct", ascending=False)

    return status_txt, sol, util_df

def solve_with_fallback(bom, stock, program):
    # Capacity-based deterministic plan (no ILP): find max per coach type s.t. stock allows
    bom = bom.copy()
    bom["item_code"] = bom["item_code"].astype(str)
    stock_dict = dict(zip(stock["item_code"].astype(str), stock["on_hand_qty"].astype(float)))
    coach_types = list(program["coach_type"])
    min_target = dict(zip(program["coach_type"], program["min_target"]))
    max_target = dict(zip(program["coach_type"], program["max_target"]))
    value = dict(zip(program["coach_type"], program["value_per_coach"]))

    req = bom.groupby(["coach_type","item_code"], as_index=False)["qty_per_coach"].sum()

    def max_by_stock(ct):
        sub = req[req["coach_type"]==ct]
        if sub.empty: return 10**9
        limits=[]
        for _, r in sub.iterrows():
            need = float(r["qty_per_coach"])
            have = float(stock_dict.get(r["item_code"], 0.0))
            if need>0: limits.append(have//need)
        return int(min(limits)) if limits else 10**9

    rows=[]
    for ct in coach_types:
        lo = int(min_target.get(ct,0))
        hi = int(max_target.get(ct,10**9))
        cap = max_by_stock(ct)
        qty = min(cap, hi)
        rows.append({
            "coach_type": ct,
            "qty_to_build": int(qty),
            "value_per_coach": value.get(ct,0.0),
            "min_target": lo,
            "max_target": (None if hi>=10**8 else hi)
        })

    sol = pd.DataFrame(rows)
    sol["total_value"] = sol["qty_to_build"]*sol["value_per_coach"]

    util_rows = []
    sol_ix = dict(zip(sol["coach_type"], sol["qty_to_build"]))
    items = stock["item_code"].astype(str).tolist()
    for it in items:
        used=0.0
        for ct in coach_types:
            need = req[(req["coach_type"]==ct)&(req["item_code"]==it)]["qty_per_coach"].sum()
            used += need*sol_ix.get(ct,0)
        cap = float(stock_dict.get(it,0.0))
        util = (used/cap*100.0) if cap>0 else 0.0
        util_rows.append({"item_code": it,"used_qty":used,"on_hand_qty":cap,"utilization_pct":round(util,2)})
    util_df = pd.DataFrame(util_rows).sort_values("utilization_pct", ascending=False)
    return "Fallback", sol, util_df

def run_optimizer(data_dir="."):
    bom = load_csv(os.path.join(data_dir,"bom.csv"), ["coach_type","item_code","qty_per_coach"])
    stock = load_csv(os.path.join(data_dir,"stock.csv"), ["item_code","on_hand_qty"])
    program = load_csv(os.path.join(data_dir,"program.csv"), ["coach_type","min_target","max_target","value_per_coach"])

    # Optional capacity files
    res_req = res_lim = None
    rr = os.path.join(data_dir, "resource_requirements.csv")
    rl = os.path.join(data_dir, "resource_limits.csv")
    if os.path.exists(rr) and os.path.exists(rl):
        res_req = pd.read_csv(rr)
        res_lim = pd.read_csv(rl)

    try:
        status, sol, util = solve_with_pulp(bom, stock, program, res_req, res_lim, data_dir)
    except Exception:
        status, sol, util = solve_with_fallback(bom, stock, program)

    # Save outputs
    sol_path = os.path.join(data_dir, "solution.csv")
    util_path = os.path.join(data_dir, "material_utilization.csv")
    sol.to_csv(sol_path, index=False)
    util.to_csv(util_path, index=False)
    return status, sol_path, util_path, sol, util
