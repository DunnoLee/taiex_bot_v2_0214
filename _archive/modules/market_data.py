import os
import csv
from datetime import datetime
from config.settings import Settings

class MarketData:
    def __init__(self, api, aggregator):
        self.api = api
        self.aggregator = aggregator  # 💡 資料下一站：合成器
        self.symbol = Settings.TARGET_CONTRACT
        
        # 1min Bar 狀態紀錄
        self.current_minute = None
        self.open = self.high = self.low = self.close = 0
        self.volume = 0
        
        # 存檔路徑
        self.file_dir = f"data/{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(self.file_dir, exist_ok=True)
        self.file_path = f"{self.file_dir}/{self.symbol}_1min.csv"
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as f:
                csv.writer(f).writerow(["Time", "Open", "High", "Low", "Close", "Volume"])

    def _on_tick_v1(self, exchange, tick):
        # 💡 以分鐘為切換點 (例如 09:01:59 -> 09:02:00)
        tick_min = tick.datetime.replace(second=0, microsecond=0)

        if self.current_minute is None:
            self.current_minute = tick_min
            self.open = self.high = self.low = self.close = float(tick.close)
            self.volume = int(tick.volume)
        elif tick_min > self.current_minute:
            # 🔔 一分鐘結束了！打包上一根
            bar_1m = {
                'time': self.current_minute.strftime("%Y-%m-%d %H:%M"),
                'open': self.open, 'high': self.high,
                'low': self.low, 'close': self.close,
                'volume': self.volume
            }
            # 1. 存入 CSV
            self.save_to_csv(bar_1m)
            # 2. 丟進合成器 (Aggregator)
            self.aggregator.add_1min_bar(bar_1m)
            
            # 初始化下一根
            print(f"📦 [MarketData] 1min Bar 完成: {bar_1m['time']} Close: {bar_1m['close']}")
            self.current_minute = tick_min
            self.open = self.high = self.low = self.close = float(tick.close)
            self.volume = int(tick.volume)
        else:
            # 繼續更新當前這一分鐘的 OHLC
            price = float(tick.close)
            self.high = max(self.high, price)
            self.low = min(self.low, price)
            self.close = price
            self.volume += int(tick.volume)

    def save_to_csv(self, bar):
        with open(self.file_path, 'a', newline='') as f:
            csv.writer(f).writerow([bar['time'], bar['open'], bar['high'], bar['low'], bar['close'], bar['volume']])