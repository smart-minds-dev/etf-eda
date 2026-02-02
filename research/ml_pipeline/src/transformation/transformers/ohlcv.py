from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ta.trend import MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator

from transformation.transformers.base import Transformer, TransformConfig

@dataclass
class DailyOhlcvParams:
    # MAs tuned for daily medium/long horizons
    ma_windows: List[int] = field(default_factory=lambda: [10, 20, 50, 100, 200])
    rsi_periods: List[int] = field(default_factory=lambda: [14, 21, 28])
    roc_periods: List[int] = field(default_factory=lambda: [10, 20, 63])  # ~2w, 1m, 3m
    adx_periods: List[int] = field(default_factory=lambda: [14, 20])

    # Volatility windows (annualized)
    volatility_windows: List[int] = field(default_factory=lambda: [20, 30, 60, 126])  # ~1m, 1.5m, 3m, 6m
    bb_periods: List[int] = field(default_factory=lambda: [20, 30])
    atr_periods: List[int] = field(default_factory=lambda: [14, 21])

    volume_ma_windows: List[int] = field(default_factory=lambda: [20, 50, 100])

    # Crosses for regime/trend
    ma_pairs: List[Tuple[int, int]] = field(default_factory=lambda: [(20, 50), (50, 200)])

    # Downside risk + persistence features
    drawdown_windows: List[int] = field(default_factory=lambda: [63, 126, 252])  # 3m, 6m, 1y
    trend_persistence_windows: List[int] = field(default_factory=lambda: [63, 126, 252])

    # Benchmark-relative features
    corr_windows: List[int] = field(default_factory=lambda: [63, 126])
    excess_return_windows: List[int] = field(default_factory=lambda: [63, 126])


def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Simplified Average Directional Index (ADX)."""
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    tr = np.maximum(
        high - low,
        np.maximum((high - close.shift(1)).abs(), (low - close.shift(1)).abs()),
    )
    atr = tr.rolling(period).mean()

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    plus_di = 100 * pd.Series(plus_dm, index=high.index).rolling(period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=high.index).rolling(period).mean() / atr

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return dx.rolling(period).mean()

def compute_drawdown(close: pd.Series) -> pd.Series:
    """Drawdown from running peak: (price - peak) / peak."""
    peak = close.cummax()
    return (close - peak) / peak.replace(0, np.nan)

def as_benchmark_series(
    benchmark: Optional[Union[pd.Series, pd.DataFrame]],
    date_col: str,
    close_col: str,
) -> Optional[pd.Series]:
    """
    Accept benchmark as:
      - pd.Series indexed by date (preferred)
      - pd.DataFrame with [date_col, close_col]
    Return: pd.Series indexed by date.
    """
    if benchmark is None:
        return None

    if isinstance(benchmark, pd.Series):
        s = benchmark.copy()
        if not isinstance(s.index, pd.DatetimeIndex):
            s.index = pd.to_datetime(s.index)
        return s.sort_index()

    if isinstance(benchmark, pd.DataFrame):
        if date_col not in benchmark.columns or close_col not in benchmark.columns:
            raise ValueError("benchmark_df must contain date_col and close_col")
        tmp = benchmark[[date_col, close_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col])
        tmp = tmp.sort_values(date_col)
        s = tmp.set_index(date_col)[close_col].astype(float)
        return s

    raise TypeError("benchmark must be a pd.Series or pd.DataFrame or None")

def select_ohlcv_features_for_horizon(prediction_days: int) -> List[str]:
    """
    Select OHLCV-related features based on prediction horizon (in days).
    """
    base = ["close", "volume", "returns_1d"]

    if prediction_days <= 30:
        return base + [
            "returns_21d",
            "sma_20", "sma_50",
            "ema_20", "ema_50",
            "price_vs_sma_20", "price_vs_sma_50",
            "sma_20_above_50",
            "rsi_14", "rsi_21",
            "roc_10", "roc_20",
            "macd", "macd_signal", "macd_diff",
            "volatility_20", "volatility_30",
            "bb_20_position", "bb_20_width",
            "atr_14_pct",
            "volume_ratio_20", "volume_ratio_50",
            "cmf_20",
            "max_drawdown_63",
            "trend_persistence_63",
        ]

    # Medium to long horizon
    return base + [
        "returns_63d",
        "sma_50", "sma_100", "sma_200",
        "ema_50", "ema_100",
        "price_vs_sma_50", "price_vs_sma_200",
        "sma_50_above_200",
        "rsi_21", "rsi_28",
        "roc_63",
        "macd", "macd_signal",
        "volatility_60", "volatility_126",
        "bb_30_position", "bb_30_width",
        "atr_21_pct",
        "volume_ratio_50", "volume_ratio_100",
        "obv_trend",
        "max_drawdown_126", "max_drawdown_252",
        "trend_persistence_126", "trend_persistence_252",
        # Optional if benchmark provided
        "corr_to_benchmark_126",
        "excess_return_126",
    ]


class DailyOhlcvTransformer(Transformer):
    """
    Transform raw daily OHLCV into a technical + medium/long horizon feature set.

    Expected raw columns (from config):
      - symbol_col
      - date_col
      - open_col, high_col, low_col, close_col, volume_col

    Optional:
      - benchmark: pd.Series indexed by date or pd.DataFrame with date+close.
        Used to compute:
          - excess_return_{window}
          - corr_to_benchmark_{window}
    """

    def __init__(
        self,
        config: TransformConfig,
        params: Optional[DailyOhlcvParams] = None,
        benchmark: Optional[Union[pd.Series, pd.DataFrame]] = None,
        benchmark_close_col: Optional[str] = None,
    ):
        super().__init__(config)
        self.params = params or DailyOhlcvParams()

        b_close = benchmark_close_col or config.close_col
        self.benchmark_close_col = b_close
        self.benchmark = benchmark  # stored, converted inside transform

    @property
    def required_columns(self):
        cfg = self.config
        return [
            cfg.symbol_col,
            cfg.date_col,
            cfg.open_col,
            cfg.high_col,
            cfg.low_col,
            cfg.close_col,
            cfg.volume_col,
        ]
    
    def transform(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        self._validate_columns(daily_df)
        
        if daily_df.empty:
            return daily_df.copy()

        cfg = self.config
        df = daily_df.copy()

        # Ensure proper types and ordering
        df[cfg.date_col] = pd.to_datetime(df[cfg.date_col])
        df = df.sort_values([cfg.symbol_col, cfg.date_col]).reset_index(drop=True)

        bench_close = as_benchmark_series(self.benchmark, cfg.date_col, self.benchmark_close_col)
        bench_ret_1d = None
        if bench_close is not None:
            bench_ret_1d = bench_close.pct_change(1)

        out: list[pd.DataFrame] = []

        for symbol, symbol_data in df.groupby(cfg.symbol_col):
            symbol_data = symbol_data.copy()

            symbol_data[cfg.close_col] = pd.to_numeric(symbol_data[cfg.close_col], errors="coerce")
            symbol_data[cfg.high_col] = pd.to_numeric(symbol_data[cfg.high_col], errors="coerce")
            symbol_data[cfg.low_col] = pd.to_numeric(symbol_data[cfg.low_col], errors="coerce")
            symbol_data[cfg.open_col] = pd.to_numeric(symbol_data[cfg.open_col], errors="coerce")
            symbol_data[cfg.volume_col] = pd.to_numeric(symbol_data[cfg.volume_col], errors="coerce")

            close = symbol_data[cfg.close_col].astype(float)
            high = symbol_data[cfg.high_col].astype(float)
            low = symbol_data[cfg.low_col].astype(float)
            open_ = symbol_data[cfg.open_col].astype(float)
            volume = symbol_data[cfg.volume_col].astype(float)

            # --- Basic returns ---
            symbol_data["returns_1d"] = close.pct_change(1)
            symbol_data["returns_21d"] = close.pct_change(21)   # ~1 month
            symbol_data["returns_63d"] = close.pct_change(63)   # ~3 months
            symbol_data["log_returns_1d"] = np.log(close / close.shift(1))

            symbol_data["high_low_range"] = (high - low) / close.replace(0, np.nan)
            symbol_data["close_open_change"] = (close - open_) / open_.replace(0, np.nan)

            # --- Moving averages + relative distance ---
            for window in self.params.ma_windows:
                sma = close.rolling(window).mean()
                ema = close.ewm(span=window, adjust=False).mean()

                symbol_data[f"sma_{window}"] = sma
                symbol_data[f"ema_{window}"] = ema

                symbol_data[f"price_vs_sma_{window}"] = (close - sma) / sma.replace(0, np.nan)
                symbol_data[f"price_vs_ema_{window}"] = (close - ema) / ema.replace(0, np.nan)

            # --- Momentum indicators ---
            for period in self.params.rsi_periods:
                rsi = RSIIndicator(close, window=period)
                symbol_data[f"rsi_{period}"] = rsi.rsi()

            stoch = StochasticOscillator(high, low, close)
            symbol_data["stoch_k"] = stoch.stoch()
            symbol_data["stoch_d"] = stoch.stoch_signal()

            for period in self.params.roc_periods:
                shifted = close.shift(period)
                symbol_data[f"roc_{period}"] = (close - shifted) / shifted * 100.0

            # --- Trend indicators ---
            macd = MACD(close)
            symbol_data["macd"] = macd.macd()
            symbol_data["macd_signal"] = macd.macd_signal()
            symbol_data["macd_diff"] = macd.macd_diff()

            for period in self.params.adx_periods:
                symbol_data[f"adx_{period}"] = calculate_adx(high, low, close, period)

            for short, long_ in self.params.ma_pairs:
                short_sma = symbol_data.get(f"sma_{short}")
                long_sma = symbol_data.get(f"sma_{long_}")
                if short_sma is not None and long_sma is not None:
                    symbol_data[f"sma_{short}_above_{long_}"] = (
                        short_sma > long_sma
                    ).astype(int)
                    symbol_data[f"sma_{short}_{long_}_diff"] = (
                        short_sma - long_sma
                    ) / long_sma.replace(0, np.nan)

            # --- Volatility (annualized) ---
            for window in self.params.volatility_windows:
                symbol_data[f"volatility_{window}"] = (
                    symbol_data["returns_1d"].rolling(window).std() * np.sqrt(252)
                )

            # --- Bollinger Bands ---
            for period in self.params.bb_periods:
                bb = BollingerBands(close, window=period, window_dev=2)
                up = bb.bollinger_hband()
                lowb = bb.bollinger_lband()
                mid = bb.bollinger_mavg()

                symbol_data[f"bb_{period}_upper"] = up
                symbol_data[f"bb_{period}_lower"] = lowb
                symbol_data[f"bb_{period}_middle"] = mid

                width = (up - lowb)
                width_safe = width.replace(0, np.nan)

                symbol_data[f"bb_{period}_position"] = (close - lowb) / width_safe
                symbol_data[f"bb_{period}_width"] = width / mid.replace(0, np.nan)

            # --- ATR ---
            for period in self.params.atr_periods:
                atr = AverageTrueRange(high, low, close, window=period)
                atr_val = atr.average_true_range()
                symbol_data[f"atr_{period}"] = atr_val
                symbol_data[f"atr_{period}_pct"] = atr_val / close.replace(0, np.nan)

            # --- Volume features ---
            for window in self.params.volume_ma_windows:
                vma = volume.rolling(window).mean()
                symbol_data[f"volume_sma_{window}"] = vma
                symbol_data[f"volume_ratio_{window}"] = volume / vma.replace(0, np.nan)

            obv = OnBalanceVolumeIndicator(close, volume)
            symbol_data["obv"] = obv.on_balance_volume()
            symbol_data["obv_sma_20"] = symbol_data["obv"].rolling(20).mean()
            symbol_data["obv_trend"] = (
                symbol_data["obv"] - symbol_data["obv_sma_20"]
            ) / symbol_data["obv_sma_20"].replace(0, np.nan)

            for period in [20]:
                cmf = ChaikinMoneyFlowIndicator(high, low, close, volume, window=period)
                symbol_data[f"cmf_{period}"] = cmf.chaikin_money_flow()

            # --- Downside / drawdown features ---
            symbol_data["drawdown"] = compute_drawdown(close)
            for window in self.params.drawdown_windows:
                symbol_data[f"max_drawdown_{window}"] = symbol_data["drawdown"].rolling(window).min()

            # --- Trend persistence ---
            # Fraction of days in last W where close > SMA(W)
            for window in self.params.trend_persistence_windows:
                sma_w = close.rolling(window).mean()
                symbol_data[f"trend_persistence_{window}"] = (close > sma_w).rolling(window).mean()

            # --- Benchmark-relative features ---
            if bench_close is not None and bench_ret_1d is not None:
                # align benchmark series by date
                bench_close_aligned = bench_close.reindex(symbol_data[cfg.date_col]).reset_index(drop=True)
                bench_ret_aligned = bench_ret_1d.reindex(symbol_data[cfg.date_col]).reset_index(drop=True)

                symbol_data["benchmark_close"] = bench_close_aligned.values
                symbol_data["benchmark_returns_1d"] = bench_ret_aligned.values

                for window in self.params.excess_return_windows:
                    # excess over same-window benchmark return
                    symbol_data[f"excess_return_{window}"] = close.pct_change(window) - pd.Series(symbol_data["benchmark_close"]).pct_change(window)

                for window in self.params.corr_windows:
                    # rolling correlation of 1d returns
                    symbol_data[f"corr_to_benchmark_{window}"] = (
                        symbol_data["returns_1d"].rolling(window).corr(pd.Series(symbol_data["benchmark_returns_1d"]))
                    )

            out.append(symbol_data)
            
        return pd.concat(out, ignore_index=True)