# 🚆 JM Optimizer

**JM Optimizer** is a Python-based desktop application that optimizes a **Bill of Materials (BoM)** against available stock to generate efficient production plans.
It helps reduce manual planning effort and errors by automatically calculating how many final products can be produced from current inventory.

---

## ✨ Features

* 📊 **BoM Optimization**
  Calculates feasible production quantities using BoM and available stock.

* 🖥️ **Simple Desktop UI**
  Clean and lightweight **Tkinter-based interface** for loading files and running the optimizer.

* 📁 **CSV-Based Inputs**
  Uses structured CSV files for **BoM, program (demand), and stock data**.

* 📤 **Exportable Results**
  Generates optimized results that can be exported as CSV for reporting or analysis.

* 📦 **Packaged Application**
  Can run as a **Python script** or as a packaged **`.exe` application**.

---

## 🛠 Tech Stack

**Language**

* Python

**Libraries**

* `tkinter` – Desktop GUI
* `pandas` – Data processing
* `PuLP` – Linear programming optimization

**Packaging**

* PyInstaller – Convert the project into a standalone executable

---

## 📂 Project Structure

```
JM-Optimizer
│
├── app.py                # Main GUI application
├── optimizer.py          # Optimization logic
├── requirements.txt      # Python dependencies
│
├── Material List
│   ├── bom.csv           # Bill of Materials
│   ├── program.csv       # Production program
│   └── stock.csv         # Available stock
│
└── jm_optimizer.ico      # Application icon
```

---

## ⚙️ Installation (From Source)

### 1. Clone the repository

```
git clone https://github.com/Moni-King-Dev/JM-Optimizer.git
cd JM-Optimizer
```

### 2. Create a virtual environment (optional)

Windows

```
python -m venv venv
venv\Scripts\activate
```

Mac / Linux

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Run the Python application:

```
python app.py
```

Using the GUI you can:

1. Select **BoM**, **Program**, and **Stock** CSV files
2. Run the optimization process
3. Export the optimized production results

---

## 🧾 Input File Overview

| File            | Description                                      |
| --------------- | ------------------------------------------------ |
| **bom.csv**     | Defines components required per finished product |
| **program.csv** | Defines production targets or demand             |
| **stock.csv**   | Contains current inventory levels                |

Refer to the sample files inside **Material List/** for the expected format.

---

## 🧪 Development

Contributions are welcome. Possible improvements include:

* Performance optimization
* Advanced reporting features
* Additional optimization constraints
* Multi-factory production support

Feel free to open **issues** or submit **pull requests**.

---

## 📜 License

This project is currently unlicensed.
If you plan to reuse or distribute it, consider adding a license such as **MIT** or **Apache 2.0**.
