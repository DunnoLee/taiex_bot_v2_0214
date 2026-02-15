# core/notifier.py
import requests
from config.settings import Settings

class TelegramNotifier:
    def __init__(self):
        self.token = Settings.TELEGRAM_TOKEN
        self.chat_id = Settings.TELEGRAM_CHAT_ID
        self.enabled = Settings.ENABLE_NOTIFIER
        self.last_update_id = 0

    def send(self, message):
        """發送訊息"""
        if not self.enabled: return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload, timeout=5)
        except Exception as e:
            print(f"❌ TG 發送失敗: {e}")

    def get_command(self):
        """接收最新指令 (Polling)"""
        if not self.enabled: return None
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        try:
            params = {"offset": self.last_update_id + 1, "timeout": 1}
            resp = requests.get(url, params=params, timeout=3).json()
            if resp.get("ok") and resp["result"]:
                for update in resp["result"]:
                    self.last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        return update["message"]["text"]
        except:
            pass
        return None

    def send_trade_signal(self, action, price, time_str):
        """發送交易訊號專用格式"""
        icon = "⚠️" if "STOP" in action else ("🔴" if "BUY" in action else "🟢")
        msg = (f"{icon} *策略訊號*\n"
               f"📍 動作: `{action}`\n"
               f"💰 價格: `{price}`\n"
               f"⏰ 時間: `{time_str}`")
        self.send(msg)