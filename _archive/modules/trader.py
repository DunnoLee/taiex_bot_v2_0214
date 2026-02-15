import shioaji as sj
from shioaji import constant, account
from config.settings import Settings

class Trader:
    def __init__(self, api):
        self.api = api
        self.account = None
        
        print("💳 [Trader] 正在掃描可用帳號...")
        try:
            # 💡 確保有登入才抓帳號
            all_accounts = self.api.list_accounts()
        except Exception as e:
            print(f"❌ 無法取得帳號列表: {e}")
            all_accounts = []

        for acc in all_accounts:
            if isinstance(acc, account.FutureAccount):
                self.account = acc
                break
        
        if self.account:
            print(f"✅ [Trader] 成功綁定期貨帳號: {self.account.account_id}")
        else:
            print(f"❌ [Trader] 嚴重警告：找不到任何期貨帳號！")

    def place_order(self, contract_code, action, quantity=1, price=0):
        try:
            if not self.account:
                print("❌ [下單失敗] 無有效帳號")
                return None

            # 💡 取得合約資訊
            contract = self.api.Contracts.Futures.TMF[contract_code]
            if not contract:
                print(f"❌ [下單錯誤] 找不到合約: {contract_code}")
                return None

            action_enum = constant.Action.Buy if action == "Buy" else constant.Action.Sell
            
            # 1. 🟢 決定價格類型 (MKT 市價 / LMT 限價)
            if price <= 0:
                p_type = constant.FuturesPriceType.MKT 
                input_price = 0 
            else:
                p_type = constant.FuturesPriceType.LMT
                input_price = price

            # 2. 🟢 決定委託條件 (關鍵修正：改用 FuturesPriceType)
            if p_type == constant.FuturesPriceType.MKT:
                o_type = constant.OrderType.IOC  # 市價單必須搭配 IOC
            else:
                o_type = constant.OrderType.ROD  # 限價單預設 ROD

            order = self.api.Order(
                price=input_price,
                quantity=quantity,
                action=action_enum,
                price_type=p_type,
                order_type=o_type, 
                oct_type=constant.FuturesOCType.Auto, # 自動判斷新倉/平倉
                account=self.account
            )

            # 3. 執行下單或攔截
            if Settings.DRY_RUN:
                print(f"🚧 [演習模式] 攔截下單！內容: {action} {contract_code} x{quantity} @ {p_type}")
                return "DryRun_Success"
            else:
                print(f"⚡ [真實下單] {action} {contract_code} x{quantity}")
                trade = self.api.place_order(contract, order)
                print(f"   👉 委託序號: {trade.status.id if hasattr(trade, 'status') else 'Sent'}")
                return trade

        except Exception as e:
            print(f"❌ [下單失敗] {e}")
            return None

    def get_positions(self):
        """[查詢] 目前期貨倉位"""
        try:
            if not self.account: return []
            positions = self.api.list_positions(self.account)
            results = []
            for p in positions:
                # 篩選微台指相關合約
                if "TMF" in p.code: 
                    results.append({
                        "code": p.code,
                        "direction": "Buy" if p.direction == constant.Action.Buy else "Sell",
                        "quantity": int(p.quantity),
                        "price": float(p.price),
                        "pnl": float(p.pnl)
                    })
            return results
        except Exception as e:
            print(f"❌ [查詢倉位失敗] {e}")
            return []

    def get_account_balance(self):
        """[查詢] 權益數資訊"""
        try:
            if not self.account: return None
            margin = self.api.margin(self.account)
            return {
                "equity": float(margin.equity),              # 權益總值
                "available": float(margin.available_margin), # 可用保證金
                "pnl": float(margin.unrealized_pnl)          # 未實現損益 (修正欄位名)
            }
        except Exception as e:
            print(f"❌ [查詢權益失敗] {e}")
            return None