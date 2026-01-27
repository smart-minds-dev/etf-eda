# 📊 ETF Exploratory Data Analysis (US & Canada)

This project focuses on **exploratory data analysis (EDA)** of selected **US and Canadian Exchange-Traded Funds (ETFs)**.
The goal is to understand **historical performance, volatility, and risk–return characteristics** using Python-based analysis and visualization.

This work serves as a foundation for further analysis, such as correlation studies or predictive modeling.

---

## 📁 Project Structure

```
ETF_EDA/
│
├── data/
│   ├── raw/
│   │   └── etf_price_data.csv
│   │
│   └── processed/
│       ├── etf_returns.csv
│       ├── etf_volatility.csv
│       └── etf_correlation_matrix.csv
│
├── scripts/
│   ├── fetch_etf_data.py
│   ├── eda_returns.py
│   ├── eda_volatility.py
│   └── eda_correlation.py
│
├── notebooks/
│   └── etf_eda.ipynb
│
├── docs/
│   ├── README.md
│   └── EDA_NOTES.md
│
├── requirements.txt
├── .gitignore
└── venv/
```

---

## 📌 Data Overview

* **Raw data**:
  Daily adjusted closing prices for selected US and Canadian ETFs, fetched using `yfinance`.

* **Processed data**:

  * `etf_returns.csv`: daily and cumulative returns per ETF
  * `etf_volatility.csv`: annualized volatility metrics
  * `etf_correlation_matrix.csv`: correlation between ETF returns

---

## 🧠 Analysis Performed

The project currently includes:

* **Cumulative return analysis**
  Understanding how each ETF performed over time.

* **Volatility analysis**
  Measuring annualized volatility to assess relative risk.

* **Risk vs return comparison**
  Comparing cumulative return against volatility to identify performance clusters.

* **Correlation analysis**
  Exploring relationships between ETF returns.

Visualizations are implemented using **matplotlib** and **Jupyter notebooks** for transparency and reproducibility.

---

## ▶️ How to Run the Project

### 1️⃣ Create and activate a virtual environment

#### **Windows (PowerShell / CMD)**

```bash
python -m venv venv
venv\Scripts\activate
```

#### **macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal once activated.

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Fetch raw ETF price data

```bash
python scripts/fetch_etf_data.py
```

---

### 4️⃣ Run EDA scripts

```bash
python scripts/eda_returns.py
python scripts/eda_volatility.py
python scripts/eda_correlation.py
```

---

### 5️⃣ Explore interactively

Open the Jupyter notebook:

```bash
notebooks/etf_eda.ipynb
```

---

## 🛑 Deactivating the Virtual Environment

When finished:

```bash
deactivate
```