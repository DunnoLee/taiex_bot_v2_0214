import pandas as pd

class Indicators:
    @staticmethod
    def ma(prices: pd.Series, window: int):
        """計算移動平均線"""
        if len(prices) < window:
            return None
        return float(prices.rolling(window=window).mean().iloc[-1])

    @staticmethod
    def slope(series: pd.Series, period: int):
        """計算斜率 (當前值與 N 根前的值之差)"""
        if len(series) < period + 1:
            return 0
        return float(series.iloc[-1] - series.iloc[-(period + 1)])