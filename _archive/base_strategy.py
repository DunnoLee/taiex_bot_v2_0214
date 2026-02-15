import csv
import os
from datetime import datetime
from config.settings import Settings

class BaseStrategy:
    def __init__(self, bot, trader=None):
        self.bot = bot
        self.trader = trader
        self.position = 0
        self.entry_price = 0
        self.total_profit = 0
        self.trade_count = 0
        self.is_trading_active = True
        
        # 交易紀錄檔路徑 (自動建立日期資料夾)
        self.log_path = f"data/{datetime.now().strftime('%Y-%m-%d')}/trade_log.csv"
        self._init_log()

    def _init_log(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Action", "Price", "Profit", "Total_Profit", "Note"])

    def log_trade(self, time, action, price, profit, note=""):
        try:
            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([time, action, price, f"{profit:.1f}", f"{self.total_profit:.1f}", note])
        except Exception as e:
            print(f"❌ [Log] 寫入失敗: {e}")

    def buy(self, price, time, note=""):
        price = float(price)
        profit = 0
        if self.position < 0: # 平空倉
            profit = self.entry_price - price
            self.total_profit += profit
            self.trade_count += 1
            if self.bot: self.bot.send_info("平倉通知", f"⚪ [空單平倉] {time} 價:{price} | 損益:{profit:.0f}")
            action_label = "COVER"
        else: # 開多倉
            if self.bot: self.bot.send_alert("策略訊號", f"🔴 [買進] {time} 價:{price} ({note})")
            action_label = "BUY"

        self.position += 1
        self.entry_price = price
        self.log_trade(time, action_label, price, profit, note)
        if self.trader and self.is_trading_active:
            self.trader.place_order(Settings.TARGET_CONTRACT, "Buy", 1)

    def sell(self, price, time, note=""):
        price = float(price)
        profit = 0
        if self.position > 0: # 平多倉
            profit = price - self.entry_price
            self.total_profit += profit
            self.trade_count += 1
            if self.bot: self.bot.send_info("平倉通知", f"⚪ [多單平倉] {time} 價:{price} | 損益:{profit:.0f}")
            action_label = "SELL_OFFSET"
        else: # 開空倉
            if self.bot: self.bot.send_alert("策略訊號", f"🟢 [做空] {time} 價:{price} ({note})")
            action_label = "SELL"

        self.position -= 1
        self.entry_price = price
        self.log_trade(time, action_label, price, profit, note)
        if self.trader and self.is_trading_active:
            self.trader.place_order(Settings.TARGET_CONTRACT, "Sell", 1)