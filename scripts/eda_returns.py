import pandas as pd 

# load data
df = pd.read_csv('etf_price_data.csv')

# ensure correct data types
df['Date'] = pd.to_datetime(df['Date']) 

# sort properly
df = df.sort_values(by=['Ticker', 'Date'])

print("Data loaded:")
print(df.head())

# 2. CALCULATE RETURNS
df["Daily_Return"] = (
    df.groupby("Ticker")["Adj_Close"]
    .pct_change()
)

# Calculate Cumulative Return
df["Cumulative_Return"] = (
    (1 + df["Daily_Return"])
    .groupby(df["Ticker"])
    .cumprod() - 1
)

# save outputs
output_file = "etf_returns.csv"
df.to_csv(output_file, index=False)

print(f"\nSUCCESS: Saved returns data to {output_file}")

# quick sanity check
summary = (
    df.groupby("Ticker")["Cumulative_Return"]
    .last()
    .sort_values(ascending=False)
)

print("\n10-Year Performance Ranking:")
print(summary)
                    