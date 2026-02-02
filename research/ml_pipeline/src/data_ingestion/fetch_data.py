import yfinance as yf
from pathlib import Path
from typing import List, Optional, Any
import pandas as pd


class DataFetch:
    """DISCLAIMER:
    This class is solely rely on yahoo finance as its resource. Will add more 
    financial data resource as it develops.
    """

    def __init__(self):
        pass

    def export_local(self,
                    df: pd.DataFrame,
                    output_dir: str = 'data/raw', 
                    filename: str = 'fetched_data.csv'
        ):
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save locally
        file_path = output_path / filename
        df.to_csv(file_path, index=False)
        print(f"Saved: {file_path}")

    def fetch_data(self, 
                tickers: List[str], 
                start_date: Any, 
                end_date: Optional[Any],
                output_dir: str = 'data/raw',
                filename: str = 'fetched_data.csv'
        ):
        """Can and should be extended to other sources"""
        # if source == 'yfinance':
        #     yfinance_fetch_data()

        df = yf.download(tickers=tickers, 
                        start=start_date,
                        end=end_date,
                        group_by="ticker", 
                        auto_adjust=False)
        
        if df.empty:
            raise ValueError(f"No data downloaded.")
        
        # df columns are either:
        # - MultiIndex: (ticker, field) when multiple tickers
        # - SingleIndex: field when one ticker
        if isinstance(df.columns, pd.MultiIndex):
            long_df = (
                df.stack(level=0)              # index: (Date, Ticker)
                .rename_axis(["date", "ticker"])
                .reset_index()
            )
        else:
            # single ticker case
            long_df = df.reset_index()
            long_df.insert(1, "ticker", tickers[0])

        # Standardize column names to preferred schema
        rename_map = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
        long_df = long_df.rename(columns=rename_map)

        # Keep just what we want (drop adj_close if not needed)
        keep_cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
        missing = [c for c in keep_cols if c not in long_df.columns]
        if missing:
            raise ValueError(f"Missing expected columns: {missing}")

        long_df = long_df[keep_cols].sort_values(["ticker", "date"])

        # Optional: enforce uniqueness
        if long_df.duplicated(subset=["ticker", "date"]).any():
            raise ValueError("Duplicate (ticker, date) rows found!")
        
        self.export_local(df=long_df, output_dir=output_dir, filename=filename)
        return long_df
