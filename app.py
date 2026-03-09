import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from optimizer import run_optimizer

APP_TITLE = "JM-Optimizer"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x700")

        try:
            self.iconbitmap("jm_optimizer.ico")
        except Exception:
            pass

        # Input file paths
        self.bom_file = tk.StringVar()
        self.stock_file = tk.StringVar()
        self.program_file = tk.StringVar()

        # Input selectors
        self._make_file_picker("BOM file:", self.bom_file).pack(fill="x", pady=4, padx=12)
        self._make_file_picker("Stock file:", self.stock_file).pack(fill="x", pady=4, padx=12)
        self._make_file_picker("Program file:", self.program_file).pack(fill="x", pady=4, padx=12)

        # Run button
        action = ttk.Frame(self, padding=14)
        action.pack(fill="x")
        self.run_btn = ttk.Button(action, text="Run Optimization", command=self.run_optimization)
        self.run_btn.pack(side="left")
        self.status_lbl = ttk.Label(action, text="")
        self.status_lbl.pack(side="left", padx=12)

        # Output text area
        self.output_text = tk.Text(self, wrap="none", font=("Courier", 10))
        self.output_text.pack(fill="both", expand=True, padx=12, pady=12)

        # Add scrollbars
        y_scroll = tk.Scrollbar(self, orient="vertical", command=self.output_text.yview)
        y_scroll.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=y_scroll.set)

        x_scroll = tk.Scrollbar(self, orient="horizontal", command=self.output_text.xview)
        x_scroll.pack(side="bottom", fill="x")
        self.output_text.config(xscrollcommand=x_scroll.set)

    def _make_file_picker(self, label, var):
        frame = ttk.Frame(self)
        ttk.Label(frame, text=label).pack(side="left")
        ttk.Entry(frame, textvariable=var, width=80).pack(side="left", padx=8)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_file(var)).pack(side="left")
        return frame

    def _browse_file(self, var):
        f = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if f:
            var.set(f)

    def run_optimization(self):
        try:
            # Clear output area
            self.output_text.delete(1.0, tk.END)

            # Load files into DataFrames
            bom = pd.read_csv(self.bom_file.get())
            stock = pd.read_csv(self.stock_file.get())
            program = pd.read_csv(self.program_file.get())

            # Run optimizer
            from optimizer import solve_with_pulp, solve_with_fallback
            try:
                status, sol_df, util_df = solve_with_pulp(bom, stock, program)[0], solve_with_pulp(bom, stock, program)[1], solve_with_pulp(bom, stock, program)[2]
            except Exception:
                status, sol_df, util_df = solve_with_fallback(bom, stock, program)
                status = "Fallback"

            # Display result in GUI
            self.status_lbl.config(text=f"Status: {status}")

            self.output_text.insert(tk.END, f"=== Build Plan (Solution) ===\n")
            self.output_text.insert(tk.END, sol_df.to_string(index=False))
            self.output_text.insert(tk.END, f"\n\n=== Top Constrained Materials ===\n")
            self.output_text.insert(tk.END, util_df.to_string(index=False))

        except Exception as e:
            messagebox.showerror(APP_TITLE, str(e))

if __name__ == "__main__":
    App().mainloop()
