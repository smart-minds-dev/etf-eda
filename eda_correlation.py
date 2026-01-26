import pandas as pd

# load return data
df = pd.read_csv('etf_returns.csv')
df['Date'] = pd.to_datetime(df['Date'])

# create returns matrix
returns_matrix = df.pivot(index='Date', 
                          columns='Ticker', 
                          values='Daily_Return'
                          )

# drop rows with any NaN values
returns_matrix = returns_matrix.dropna()

# compute correlation 
correlation_matrix = returns_matrix.corr()

# save outputs
output_file = "etf_correlation_matrix.csv"
correlation_matrix.to_csv(output_file)

print(f"\nSUCCESS: Saved correlation matrix to {output_file}")

# quick inspection
print('\nCorrelation Matrix (Preview):')
print(correlation_matrix.round(2))