# Fulfillment Hub

A Streamlit prototype for XYZ's e-commerce fulfillment workflow.

## Problem focus

The prototype focuses on the highest-impact operational problems described in the assignment:

1. Poor order-status visibility
2. Priority orders being mixed with regular orders
3. Delays going unnoticed
4. Inventory discrepancies and stock in a secondary warehouse
5. Courier pickup visibility

## Features

- Operations dashboard
- Priority and risk classification
- Order filtering and detail view
- Order workflow progression
- Main/secondary warehouse inventory view
- Stock-transfer demonstration
- Courier/staging dashboard
- Synthetic sample data

## Tech stack

- Python
- Streamlit
- Pandas
- NumPy

## Run locally

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

## Project structure

```text
fulfillment-hub/
├── app.py
├── app-link.txt
├── requirements.txt
├── README.md
├── data/
│   ├── orders.csv
│   ├── products.csv
│   ├── inventory.csv
│   └── shipments.csv
└── .streamlit/
    └── config.toml
```

## Important demo note

All data is synthetic. The prototype is intentionally not connected to a real store, warehouse, or courier system.

## Deployment

The intended deployment target is Streamlit Community Cloud. Keep `requirements.txt` in the repository root and use `app.py` as the entrypoint.
