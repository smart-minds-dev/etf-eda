# ETF Exploratory Data Analysis (EDA) – Notes & Reference

This document contains **working notes and explanations** for the ETF Exploratory Data Analysis (EDA) pipeline in this repository.

The goal of these notes is:
- To help me understand ETF behavior through **hands-on technical analysis**
- To document **what each metric is**, **how it is computed**, and **why it is used**
- To serve as a reference for others who want to learn ETF EDA using Python

This project intentionally focuses on **EDA and statistics**, not prediction or machine learning.

---

## 1. Dataset Overview

### Source
- Data is pulled from **Yahoo Finance** using the `yfinance` Python library.
- Prices used are **Adjusted Close** prices.

### Why Adjusted Close?
Adjusted Close accounts for:
- Dividends
- Stock splits

This makes it more suitable for:
- Return calculation
- Long-term performance comparison
- ETF analysis (especially dividend ETFs)

---

## 2. Price Data Structure

Each row in the dataset represents:
- One ETF
- On one trading date
- With an adjusted price

Core columns:
- `Date` – trading date
- `Ticker` – ETF symbol
- `Adj_Close` – adjusted closing price
- `Market` – US or Canada

Prices themselves are **not directly comparable** across ETFs.
This is why returns are calculated.

---

## 3. Daily Returns

### What is a Daily Return?

Daily return measures **percentage change** from one trading day to the next.

Formula:
Daily Return = (Price_today - Price_yesterday) / Price_yesterday


In code:
df.groupby("Ticker")["Adj_Close"].pct_change()

Why Returns Instead of Prices?
- Prices depend on scale (e.g. $50 vs $500)
- Returns are unit-free
- Returns allow fair comparison across ETFs

Almost all quantitative finance analysis is done in return space, not price space.

## 4. Cumulative Returns

### What is Cumulative Return?

Cumulative return shows how much an investment has grown over time, assuming reinvestment.

Formula:
Cumulative Return = (1 + r1) × (1 + r2) × ... × (1 + rt) − 1

This uses compounding, not simple addition.

In code:
(1 + Daily_Return).groupby(Ticker).cumprod() - 1

Why Compounding Matters

Markets compound over time.
Small differences in daily returns can lead to large differences over 10+ years.

Cumulative returns help answer:
- Which ETFs performed best long-term?
- Which underperformed?
- How different asset types behaved over time

## 5. Volatility

### What is Volatility?

Volatility measures how much returns fluctuate.
It is commonly used as a proxy for risk.

Mathematically, volatility is the standard deviation of returns.

In this project:
- Daily volatility is computed first
- Then annualized

Annualized Volatility Formula
Annualized Volatility = Daily Volatility × sqrt(252)

Where:
- 252 ≈ number of trading days in a year

Why Volatility Matters
Higher volatility:
- Larger price swings
- More uncertainty

Lower volatility:
- Smoother performance
- Typically considered safer

This metric helps compare:
- Bond ETFs vs equity ETFs
- Low-volatility ETFs vs broad market ETFs

## 6. Correlation

### What is Correlation?
Correlation measures how two ETFs move relative to each other.

Correlation values range from:
- +1 → move together
- 0 → no relationship
- −1 → move opposite directions

How Correlation is Computed
Correlation is calculated using daily returns, not prices.

Steps:
1. Pivot returns into a matrix (Date × Ticker)
2. Apply Pearson correlation

In code:
returns_matrix.corr()

Why Correlation Matters
Correlation helps explain:
- Diversification benefits
- Why bonds reduce portfolio risk
- Why owning many similar ETFs may not reduce risk
Low or negative correlation is a key concept in safer portfolio construction.

## 7. Why This Project Avoids Prediction & ML

This project intentionally does not include:
- Price prediction
- Machine learning models
- Trading signals

The focus is on:
- Understanding ETF behavior
- Measuring risk and return
- Building intuition through data

This aligns with:
- Low-risk quantitative investing
- Strong analytical foundations before modeling

## 8. Learning Approach

The learning approach used here is:
- Build first
- Explore data
- Learn concepts through implementation
- Refine understanding over time
These notes may evolve as understanding improves.

## 9. Disclaimer
This project is for:
- Learning
- Exploration
- Analysis
It does not constitute investment advice.

## 10. Summary
This EDA pipeline provides:
- Clean ETF price data
- Return computation
- Volatility measurement
- Correlation analysis

These are foundational tools used in:
- Quantitative finance
- Risk analysis
- Portfolio research

Further extensions may include:
- Risk-adjusted metrics (e.g. Sharpe ratio)
- Visualization dashboards
- Deeper asset comparisons