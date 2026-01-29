import pandas as pd
from src.eda import EDA

# Load raw dataset
df = pd.read_csv("data/raw/SPY_raw_prices.csv", index_col=0)

eda = EDA(df)
results = eda.compute_all()

print(results["summary_metrics"])
