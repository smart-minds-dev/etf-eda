import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List
import os

# NOTE: Removed 'yf.set_tz_cache_location' as it causes errors in newer yfinance versions

def download_etf_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Requesting data for {len(tickers)} tickers...")
    return yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        group_by="ticker",
        auto_adjust=False,  # Ensures we get 'Adj Close'
        progress=True,
        threads=False       # FIX: Use single thread to prevent Windows "database locked" errors
    )

def main() -> None:
    # 1. SETUP
    us_etfs = ["SPY", "VTI", "SCHD", "BND", "SPLV"]
    canada_etfs = ["XIC.TO", "VCN.TO", "VDY.TO", "ZAG.TO", "VFV.TO"]
    tickers = us_etfs + canada_etfs
    
    start_date = "2014-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")

    # 2. DOWNLOAD
    try:
        raw_data = download_etf_data(tickers, start_date, end_date)
    except Exception as e:
        print(f"CRITICAL ERROR: Download failed. {e}")
        return

    if raw_data.empty:
        print("No data found.")
        return

    # 3. PROCESSING
    records = []
    failed_tickers = []
    
    print("Processing data...")

    # Handle case where yfinance returns single-level index (only 1 ticker found)
    is_multi_index = isinstance(raw_data.columns, pd.MultiIndex)

    for ticker in tickers:
        try:
            # Extract DataFrame for this specific ticker
            if is_multi_index:
                if ticker not in raw_data.columns.get_level_values(0):
                    failed_tickers.append(ticker)
                    continue
                df_ticker = raw_data[ticker].copy()
            else:
                # Fallback if only 1 ticker downloaded
                df_ticker = raw_data.copy()

            # cleanup logic
            if "Adj Close" in df_ticker.columns:
                # Drop NAs and Reset Index to make Date a column
                temp = df_ticker[["Adj Close"]].dropna().reset_index()
                
                # Rename for consistency
                temp.columns = ["Date", "Adj_Close"]
                
                # Add Metadata
                temp["Ticker"] = ticker
                temp["Market"] = "Canada" if ticker.endswith(".TO") else "US"
                
                records.append(temp)
            else:
                failed_tickers.append(ticker)

        except Exception as e:
            print(f"Error extracting {ticker}: {e}")
            failed_tickers.append(ticker)

    # 4. SAVE
    if records:
        # Use consistent variable name 'final_df'
        final_df = pd.concat(records, ignore_index=True)
        
        # Clean Date format
        final_df['Date'] = pd.to_datetime(final_df['Date']).dt.date
        
        output_file = "etf_price_data.csv"
        final_df.to_csv(output_file, index=False)
        print(f"\nSUCCESS: Saved {len(final_df)} rows to {output_file}")
    else:
        print("No valid data to save.")

    if failed_tickers:
        print(f"Failed tickers: {failed_tickers}")

if __name__ == "__main__":
    main()