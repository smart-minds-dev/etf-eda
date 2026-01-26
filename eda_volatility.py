import pandas as pd
import numpy as np

# load return data 
df = pd.read_csv('etf_returns.csv')
df['Date'] = pd.to_datetime(df['Date'])

# calc volatility 
# daily volatility
vol_daily = (
    df.groupby("Ticker")["Daily_Return"]
    .std()
)

# annualized volatility
vol_annual = vol_daily * np.sqrt(252)

# 3. create volatility table
volatility_df = pd.DataFrame({
    "Daily_Volatility": vol_daily,
    "Annualized_Volatility": vol_annual
}).sort_values("Annualized_Volatility")

# save outputs
output_file = "etf_volatility.csv"
volatility_df.to_csv(output_file)

print(f"\nSUCCESS: Saved volatility data to {output_file}")

# display result
print("\nETF Volatility Ranking (Low to High):")
print(volatility_df)