from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

@dataclass
class TransformConfig:

    ohlcv_dataset: str = "ohlcv"
    symbol_col: str = "ticker"
    date_col: str = "date"
    open_col: str = "open"
    high_col: str = "high"
    low_col: str = "low"
    close_col: str = "close"
    volume_col: str = "volume"

class Transformer(ABC):
    """
    Base interface for all feature transformers.
    Each transformer takes a raw DataFrame and returns a feature DataFrame.
    """

    required_columns: list[str] = []

    def __init__(self, config: TransformConfig):
        self.config = config

    def _validate_columns(self, df: pd.DataFrame):
        missing = [c for c in self.required_columns if c not in df.columns]
        if missing:
            raise ValueError(
                f"Missing required columns: {missing}. "
                f"Available columns: {list(df.columns)}"
            )

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main entry point. Subclasses implement their own logic.
        """
        raise NotImplementedError