# ETF Exploratory Data Analysis (US & Canada)

This repository contains exploratory data analysis (EDA) scripts for US and Canadian Exchange Traded Funds (ETFs).

The focus is on:
- Data acquisition
- Data cleaning
- Return calculation
- Volatility analysis
- Correlation analysis

All analysis is done in Python using script-based workflows (no notebooks), with CSV outputs intended for reuse in visualization tools such as Power BI.

## Structure
- `fetch_etf_data.py` – downloads and cleans historical ETF price data
- `eda_returns.py` – computes daily and cumulative returns
- `eda_volatility.py` – computes ETF volatility metrics
- `eda_correlation.py` – computes correlation matrix between ETFs

## Data
Data is sourced from Yahoo Finance via the `yfinance` library.

This project is exploratory and intended for learning and analysis purposes.
