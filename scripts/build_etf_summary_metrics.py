import pandas as pd
import numpy as np 

def main():
    # 1. load data
    input_file = "processed/etf_returns.csv"
    df = pd.read_csv(input_file)

    df["Date"] = pd.to_datetime(df["Date"])

    # 2. compute etf-level metrics
    summary = (
        df.groupby(["Ticker", "Market"])
        .agg(
            Avg_Daily_Return=("Daily_Return", "mean"),
            Daily_Volatility=("Daily_Return", "std"),
            Total_Return=("Cumulative_Return", "last")
        )
        .reset_index()
    )


    # 3. Annualize Volatility
    summary["Annualized_Volatility"] = summary["Daily_Volatility"] * np.sqrt(252)

    # 4. simple risk-adjusted metric
    summary["Risk_Adjusted_Return"] =(
        summary["Avg_Daily_Return"] / summary["Daily_Volatility"]
    )

    # sort by performance 
    summary = summary.sort_values("Total_Return", ascending=False)

    # 5. save output
    output_file = "processed/etf_summary_metrics.csv"
    summary.to_csv(output_file, index=False)

    print(f"ETF summary metrics saved to {output_file}")
    print(summary)

if __name__ == "__main__":
    main()        