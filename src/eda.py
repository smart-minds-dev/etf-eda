import pandas as pd

class EDA:
    def __init__(self, df: pd.DataFrame):
        """
        General EDA class for time-series financial data
        """
        self.df = df.copy()

        self._prepare_dataframe()

    def _prepare_dataframe(self):
        """
        Basic cleaning and preparation 
        """
         # If index is not datetime, try to fix it
        if not isinstance(self.df.index, pd.DatetimeIndex):

        # Case 1: Date column exists
            if "Date" in self.df.columns:
                self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
            self.df = self.df.set_index("Date")

        # Case 2: Try converting index directly
        else:
            self.df.index = pd.to_datetime(self.df.index, errors="coerce")

         # Drop rows where datetime conversion failed
        self.df = self.df[~self.df.index.isna()]

         # Sort by date
        self.df.sort_index(inplace=True)

        # Drop rows with missing Close prices
        if "Close" in self.df.columns:
            self.df = self.df.dropna(subset=["Close"])

    def compute_returns(self) -> pd.Series:
        """
        Compute daily returns.
        """
        if "Close" not in self.df.columns:
            raise ValueError("Close column not found in dataset")

        returns = self.df["Close"].pct_change()
        return returns.dropna()
    
    def compute_volatility(self, window: int = 30) -> pd.Series:
        """
        Compute rolling volatility.
        """
        returns = self.compute_returns()
        volatility = returns.rolling(window).std()
        return volatility.dropna()

    def summary_metrics(self) -> pd.DataFrame:
        """
        Generate basic summary metrics.
        """
        returns = self.compute_returns()

        metrics = {
            "mean_return": returns.mean(),
            "volatility": returns.std(),
            "min_return": returns.min(),
            "max_return": returns.max(),
        }

        return pd.DataFrame.from_dict(metrics, orient="index", columns=["value"])
    
    def compute_all(self) -> dict:
        """
        Compute all EDA outputs.
        """
        return {
            "returns": self.compute_returns(),
            "volatility": self.compute_volatility(),
            "summary_metrics": self.summary_metrics(),
        }

