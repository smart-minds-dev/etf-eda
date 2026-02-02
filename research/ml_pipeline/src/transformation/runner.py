import pandas as pd

from typing import Optional
from transformation.transformers.ohlcv import DailyOhlcvTransformer, DailyOhlcvParams
from transformation.transformers.base import TransformConfig

class DataTransform:

    def __init__(
        self, 
        transform_config: TransformConfig,
        daily_ohlcv_params: Optional[DailyOhlcvParams] = None
    ):

        self.cfg = transform_config
        self.daily_ohlcv_transformer = DailyOhlcvTransformer(
            self.cfg, daily_ohlcv_params or DailyOhlcvParams()
        )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:

        transformed_df = self.daily_ohlcv_transformer.transform(df)
        return transformed_df