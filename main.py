# main.py
import time
import shioaji as sj
from config.settings import Settings
from core.trader import Trader
from core.commander import Commander
from core.aggregator import BarAggregator
from strategies.ma_strategy import MAStrategy
from core.notifier import TelegramNotifier

class TaiexBot:
    def __init__(self):
        print("🚀 啟動實戰機器人...")
        
        # 1. 連線交易所
        self.api = sj.Shioaji()
        self.api.login(Settings.SHIOAJI_API_KEY, Settings.SHIOAJI_SECRET_KEY)
        
        # 2. 組裝零件 (傳入真實 API)
        self.notifier = TelegramNotifier()
        self.trader = Trader(api=self.api)
        self.strategy = MAStrategy(
            short_p=Settings.SHORT_P, long_p=Settings.LONG_P,
            moat=Settings.MOAT, stop_loss_pts=Settings.STOP_LOSS,
            trader=self.trader
        )
        self.commander = Commander(self.trader, self.strategy, self.notifier)
        self.aggregator = BarAggregator(timeframe=Settings.TIMEFRAME) # 30分K
        
        # 3. 訂閱報價
        self.subscribe()
        self.notifier.send("🤖 機器人已上線，等待行情中...")

    def subscribe(self):
        # 請記得改為當月合約代碼
        contract = self.api.Contracts.Futures.TMF.TMFB6 
        self.api.quote.subscribe(contract, quote_type=sj.constant.QuoteType.Tick, callback=self.on_tick)
        print(f"📡 已訂閱: {contract.code}")

    def on_tick(self, exchange, tick):
        # 處理即時 Tick
        bar_complete, df_hist = self.aggregator.add_tick(tick.datetime, float(tick.close), int(tick.volume))
        
        if bar_complete:
            self.strategy.on_bar(df_hist)

    def run_forever(self):
        try:
            while True:
                # 實戰中每 5 秒檢查一次指令
                self.commander.poll_commands()
                time.sleep(5)
        except KeyboardInterrupt:
            print("👋 機器人下線")
            self.api.logout()

if __name__ == "__main__":
    bot = TaiexBot()
    bot.run_forever()