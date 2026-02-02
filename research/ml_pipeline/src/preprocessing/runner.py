import pandas as pd
from typing import Optional
from preprocessing.preprocessing import MissingData

class DataPreprocess:

    def __init__(self, missing: Optional[MissingData] = None):
        self.missing = missing or MissingData()

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.missing.clean(df)
        # NOTE: Add future steps:
        # df = DataType().enforce(df)
        # df = DataQualityAnalysis().run(df)
        return df