# JM Optimizer

JM Optimizer is a Python-based desktop application that optimizes a Bill of Materials (BoM) against available stock to generate efficient production plans. It helps reduce manual planning effort and errors by automatically calculating how many final products can be made from current inventory.

## Features

- **BoM optimization**: Calculates feasible production quantities based on BoM and stock data.
- **Simple UI**: Tkinter-based interface for selecting input files and running the optimizer.
- **CSV-based inputs**: Uses CSV files for BoM, program (demand), and stock.
- **Exportable results**: Saves optimized results to CSV for further analysis or reporting.
- **Packaged app**: Can be run as a Python script or as a packaged `.exe` (if provided).

## Tech Stack

- **Language**: Python
- **Libraries**:
  - `tkinter` for the desktop GUI  
  - `pandas` for data handling  
  - `PuLP` (or similar) for optimization  
- **Packaging**: PyInstaller (for building the executable)

## Project Structure

- `app.py` – Main GUI entry point.
- `optimizer.py` – Core optimization logic.
- `requirements.txt` – Python dependencies.
- `Material List/` – Example or default CSV input files:
  - `bom.csv` – Bill of Materials.
  - `program.csv` – Program/demand.
  - `stock.csv` – Available stock.
- `jm_optimizer.ico` – Application icon.

## Installation (from source)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Moni-King-Dev/JM-Optimizer.git
   cd JM-Optimizer
