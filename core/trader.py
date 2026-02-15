# core/trader.py
import csv
import os
from datetime import datetime
from config.settings import Settings
from core.notifier import TelegramNotifier

class Trader:
    def __init__(self, api=None):
        self.api = api
        self.notifier = TelegramNotifier()
        self.log_file = "data/live_trades.csv" if not Settings.DRY_RUN else "data/mock_trades.csv"
        self._init_log()

    def _init_log(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                csv.writer(f).writerow(["Time", "Action", "Price", "Note"])

    def get_account_balance(self):
        """查詢保證金餘額"""
        if Settings.DRY_RUN:
            return 30000.0  # 模擬演習時的預設本金
        try:
            # 實戰：請根據 Shioaji 文件調整 (範例)
            # return self.api.account_balance()[0].available_margin
            return 0.0 # 若未串接真實 API 先回傳 0
        except:
            return -1.0

    def place_order(self, action, price, note=""):
        """執行下單邏輯"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. 寫入 CSV 紀錄
        with open(self.log_file, 'a', newline='') as f:
            csv.writer(f).writerow([now, action, price, note])
            
        # 2. 發送 Telegram
        self.notifier.send_trade_signal(action, price, now)
        print(f"🚀 [TRADER] {action} @ {price} ({note})")

        # 3. Dry Run 攔截
        if Settings.DRY_RUN:
            print("🧪 [DRY_RUN] 攔截成功：未發送 API 指令")
            return
            
        # 4. 真實下單 (僅在實戰且有 API 時執行)
        if self.api:
            # self.api.place_order(...)
            print("💰 [LIVE] 真實訂單已送出 (尚未實作 API)")