# core/commander.py
from config.settings import Settings

class Commander:
    def __init__(self, trader, strategy, notifier):
        self.trader = trader
        self.strategy = strategy
        self.notifier = notifier

    def poll_commands(self):
        """
        被動檢查是否有指令，由 Main 或 Mock Replay 呼叫
        """
        cmd_text = self.notifier.get_command()
        if not cmd_text: return

        cmd = cmd_text.split()[0].lower()
        print(f"📥 [指揮官] 收到指令: {cmd}")

        if cmd == "/status":
            active = "🟢 運作中" if self.strategy.is_trading_active else "🛑 已暫停"
            bal = self.trader.get_account_balance()
            msg = (f"📊 *系統狀態報告*\n"
                   f"🤖 策略狀態: {active}\n"
                   f"📦 目前持倉: {self.strategy.position} 口\n"
                   f"💰 帳戶餘額: ${bal:.0f}\n"
                   f"⚙️ 模式: {'🧪 演習' if Settings.DRY_RUN else '🔥 實戰'}")
            self.notifier.send(msg)

        elif cmd == "/stoptrade":
            self.strategy.is_trading_active = False
            self.notifier.send("🛑 自動交易已暫停")

        elif cmd == "/starttrade":
            self.strategy.is_trading_active = True
            self.notifier.send("🚀 自動交易已恢復")
            
        elif cmd == "/help":
            self.notifier.send("指令: /status, /stoptrade, /starttrade")