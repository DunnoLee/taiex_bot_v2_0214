# strategies/ma_strategy.py
class MAStrategy:
    def __init__(self, short_p, long_p, moat, stop_loss_pts, trader=None):
        self.short_p = short_p
        self.long_p = long_p
        self.moat = moat
        self.stop_loss_pts = stop_loss_pts
        
        self.trader = trader
        self.position = 0          # 0:空手, 1:多單, -1:空單
        self.entry_price = 0.0
        self.is_trading_active = True 

    def on_bar(self, df):
        # 如果被指揮官暫停，就不動作
        if not self.is_trading_active or len(df) < self.long_p:
            return None, 0

        current_price = df['Close'].iloc[-1]
        sma_s = df['Close'].rolling(window=self.short_p).mean().iloc[-1]
        sma_l = df['Close'].rolling(window=self.long_p).mean().iloc[-1]

        action = None
        
        # --- 停損邏輯 ---
        if self.position == 1 and (self.entry_price - current_price) >= self.stop_loss_pts:
            action = "STOP_LOSS_LONG"
        elif self.position == -1 and (current_price - self.entry_price) >= self.stop_loss_pts:
            action = "STOP_LOSS_SHORT"

        # --- 進場邏輯 (若未觸發停損) ---
        if not action:
            if sma_s > sma_l + self.moat:
                if self.position <= 0: action = "BUY_LONG"
            elif sma_s < sma_l - self.moat:
                if self.position >= 0: action = "SELL_SHORT"

        # --- 執行動作 ---
        if action:
            # 更新內部狀態
            if "BUY" in action: self.position = 1
            elif "SELL" in action: self.position = -1
            elif "STOP" in action: self.position = 0
            
            self.entry_price = current_price
            
            # 呼叫交易員下單
            if self.trader:
                self.trader.place_order(action, current_price, note="MA_Strategy")
                
            return action, current_price
            
        return None, 0