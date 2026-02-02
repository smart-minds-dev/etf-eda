import pandas as pd
import numpy as np
from typing import Any, Literal, Sequence

PriceImputePolicy = Literal["drop_partial", "ffill", "none"]

class MissingData:
    """
    Handles missingness in OHLCV-ish data.

    Strategy:
    - If missingness ratio >= high_missing_threshold: be strict (drop more)
    - Else: drop rows that are essentially "no bar", then impute *non-price* columns simply.
    """
    high_missing_threshold: float = 0.20
    price_cols: Sequence[str] = ("open", "high", "low", "close")
    volume_col: str = "volume"
    group_col: str = "ticker"
    date_col: str = "date"
    numeric_impute: Literal["median", "mean"] = "median"
    price_policy: PriceImputePolicy = "drop_partial"  # safest default

    def __init__(self, high_missing_threshold: float = 0.20):
        self.high_missing_threshold = float(high_missing_threshold)

    def _ensure_required_cols(self, df: pd.DataFrame) -> None:
        needed = {self.group_col, self.date_col, *self.price_cols}
        missing = [c for c in needed if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def missingness_ratio(self, df: pd.DataFrame) -> float:
        if df.size == 0:
            return 0.0
        return float(df.isnull().sum().sum() / df.size)
    
    def missingness_count(self, df: pd.DataFrame) -> int:
        return int(df.isnull().sum().sum())
    
    def clean(self, df: pd.DataFrame):
        """
        If missingness ratio is >= high_missing_threshold: drop more aggressively.
        Else:
          - Drop rows where all OHLC are missing (no bar)
          - If price_policy == drop_partial: drop rows where any OHLC missing
          - Impute remaining numeric non-price columns per ticker (median/mean)
          - Volume: if missing, set to 0 only if comfortable with that; otherwise impute like numeric.
        """
        self._ensure_required_cols(df)

        df = df.copy()

        # Ensure date is datetime for sanity
        if not np.issubdtype(df[self.date_col].dtype, np.datetime64):
            df[self.date_col] = pd.to_datetime(df[self.date_col], errors="coerce")

        # Drop rows with invalid dates or missing ticker
        df = df.dropna(subset=[self.group_col, self.date_col])

        miss_ratio = self.missingness_ratio(df)

        # Drop "no bar" rows: all OHLC missing
        all_ohlc_missing = df[list(self.price_cols)].isna().all(axis=1)
        df = df.loc[~all_ohlc_missing].copy()

        # Handle partial OHLC missing
        partial_ohlc_missing = df[list(self.price_cols)].isna().any(axis=1)

        if self.price_policy == "drop_partial":
            df = df.loc[~partial_ohlc_missing].copy()
        elif self.price_policy == "ffill":
            # Forward fill prices per ticker, then drop any still-missing price rows
            df = df.sort_values([self.group_col, self.date_col])
            df[list(self.price_cols)] = (
                df.groupby(self.group_col, sort=False)[list(self.price_cols)]
                  .ffill()
            )
            df = df.dropna(subset=list(self.price_cols))
        elif self.price_policy == "none":
            # leave them; but generally not recommended
            pass

        # Decide strictness based on global missingness
        # If high missingness: also drop columns with too many missing values (non-critical only)
        if miss_ratio >= self.high_missing_threshold:
            # Do NOT drop price columns.
            protected = set(self.price_cols) | {self.group_col, self.date_col}
            if self.volume_col in df.columns:
                protected.add(self.volume_col)

            non_protected = [c for c in df.columns if c not in protected]
            if non_protected:
                col_missing = df[non_protected].isna().mean()
                # Drop any non-protected column with >= threshold missingness
                drop_cols = col_missing[col_missing >= self.high_missing_threshold].index.tolist()
                if drop_cols:
                    df = df.drop(columns=drop_cols)

            # For the remaining non-protected numeric columns: can still impute,
            # but being strict often means dropping rows with any remaining NA.
            df = df.dropna()
            return df

        # Low-missingness path: simple imputation
        # Identify numeric columns excluding OHLC and group/date
        protected = set(self.price_cols) | {self.group_col, self.date_col}
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        num_cols = [c for c in num_cols if c not in protected]

        # Volume handling
        # volume=0 when missing (common for some assets):
        if self.volume_col in df.columns:
            df[self.volume_col] = df[self.volume_col].fillna(0)

        if num_cols:
            df = df.sort_values([self.group_col, self.date_col])

            if self.numeric_impute == "median":
                fill_values = df.groupby(self.group_col, sort=False)[num_cols].transform("median")
            else:
                fill_values = df.groupby(self.group_col, sort=False)[num_cols].transform("mean")

            df[num_cols] = df[num_cols].fillna(fill_values)

        # Categorical/object imputation: mode per ticker
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        cat_cols = [c for c in cat_cols if c not in (self.group_col,)]
        if cat_cols:
            def _mode(s: pd.Series) -> Any:
                m = s.mode(dropna=True)
                return m.iloc[0] if len(m) else np.nan

            for c in cat_cols:
                df[c] = df[c].fillna(df.groupby(self.group_col, sort=False)[c].transform(_mode))

        # Finally: if anything is still NA (e.g., columns with all NA within a ticker), drop rows or columns
        # Drop remaining NA rows to keep things simple.
        df = df.dropna()

        return df
        
# NOTE: Future Features
# class DataType:

#     def __init__(self):
#         pass


# class DataQualityAnalysis:

#     def __init__(self):
#         pass