# core/aggregator.py
import pandas as pd

class BarAggregator:
    def __init__(self, timeframe=30, callback=None):
        self.timeframe = timeframe
        self.callback = callback
        self.current_bar = None
        self.history_bars = []

    def add_tick(self, dt, price, volume):
        """
        接收 Tick，回傳 (是否完成K棒, 歷史DataFrame)
        """
        dt = pd.to_datetime(dt)
        bar_start = dt.floor(f'{self.timeframe}min')
        
        bar_complete = False
        df_to_return = None

        if self.current_bar is None:
            self._open_bar(bar_start, price, volume)
        elif bar_start > self.current_bar['Time']:
            # 1. 結算舊 K 棒
            self.history_bars.append(self.current_bar)
            if len(self.history_bars) > 500: 
                self.history_bars.pop(0)
            
            bar_complete = True
            df_to_return = pd.DataFrame(self.history_bars)
            
            # 若有 callback 則執行
            if self.callback:
                self.callback(df_to_return)
                
            # 2. 開新 K 棒
            self._open_bar(bar_start, price, volume)
        else:
            # 3. 更新現有 K 棒
            self.current_bar['High'] = max(self.current_bar['High'], price)
            self.current_bar['Low'] = min(self.current_bar['Low'], price)
            self.current_bar['Close'] = price
            self.current_bar['Volume'] += volume
            
        return bar_complete, df_to_return

    def _open_bar(self, dt, price, vol):
        # 統一使用大寫開頭，對齊策略
        self.current_bar = {
            'Time': dt, 'Open': price, 'High': price, 
            'Low': price, 'Close': price, 'Volume': vol
        }