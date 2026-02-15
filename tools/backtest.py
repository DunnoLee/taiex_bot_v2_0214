import pandas as pd
import os
import sys

# 導航修正
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from strategies.ma_strategy import MAStrategy

def run_settings_backtest():
    # 1. 讀取與處理參數
    csv_path = "data/history/TMF_FULL_REPLAY.csv"
    if not os.path.exists(csv_path):
        print("❌ 找不到資料檔，請先執行 tools/history_merger.py")
        return

    # 處理 Timeframe 格式
    raw_tf = str(Settings.TIMEFRAME)
    if "min" not in raw_tf and "T" not in raw_tf:
        resample_freq = f"{raw_tf}min"
    else:
        resample_freq = raw_tf

    print(f"⚙️ 讀取參數: TF={resample_freq} | MA({Settings.SHORT_P}, {Settings.LONG_P}) | Stop={Settings.STOP_LOSS}")

    # 2. 準備數據
    raw_df = pd.read_csv(csv_path)
    raw_df['Time'] = pd.to_datetime(raw_df['Time'])
    raw_df.set_index('Time', inplace=True)

    print(f"⌛ 轉換資料格局中...")
    df = raw_df.resample(resample_freq).agg({
        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
    }).dropna()

    # 3. 初始化策略
    strategy = MAStrategy(
        short_p=Settings.SHORT_P,
        long_p=Settings.LONG_P,
        moat=Settings.MOAT,
        stop_loss_pts=Settings.STOP_LOSS
    )

    # 4. 逐筆模擬
    trade_logs = []
    cost_pts = 5.4 

    print("🚀 執行逐筆回測...")
    # 從第 50 根開始確保有均線
    for i in range(50, len(df)): 
        current_history = df.iloc[:i+1]
        action, price = strategy.on_bar(current_history)
        
        if action:
            current_time = df.index[i]
            trade_logs.append({
                'Time': current_time,
                'Action': action,
                'Price': price
            })

    # 5. 產出結果
    if not trade_logs:
        print("⚠️ 無交易訊號。")
        return

    log_df = pd.DataFrame(trade_logs)
    
    # 計算累計損益與資產曲線
    pnl_records = []
    position = 0
    entry_price = 0
    equity = 0
    equity_curve = []

    for _, row in log_df.iterrows():
        act = row['Action']
        px = row['Price']
        
        realized_pnl = 0
        
        if "BUY" in act: 
            if position == -1: realized_pnl = (entry_price - px) - cost_pts
            position = 1
            entry_price = px
            
        elif "SELL" in act: 
            if position == 1: realized_pnl = (px - entry_price) - cost_pts
            position = -1
            entry_price = px
            
        elif "STOP_LOSS" in act:
            if "LONG" in act: realized_pnl = (px - entry_price) - cost_pts
            elif "SHORT" in act: realized_pnl = (entry_price - px) - cost_pts
            position = 0
        
        if realized_pnl != 0:
            equity += realized_pnl
            pnl_records.append(realized_pnl)
        
        # 💡 關鍵修正：這裡原本漏了 'Price'，現在補上了！
        equity_curve.append({
            'Time': row['Time'], 
            'equity': equity, 
            'Action': act,
            'Price': px  # <--- 補上這行，visualizer 才能畫圖
        })

    result_df = pd.DataFrame(equity_curve)
    
    if result_df.empty: return

    result_df.set_index('Time', inplace=True)
    
    # 計算 MDD
    result_df['peak'] = result_df['equity'].cummax()
    result_df['drawdown'] = result_df['equity'] - result_df['peak']
    mdd = result_df['drawdown'].min()
    
    output_path = "data/backtest_detail.csv"
    result_df.to_csv(output_path)

    print("\n📊 --- 修正版回測報告 ---")
    print(f"💰 總淨利: {equity:.1f} | MDD: {mdd:.1f}")
    print(f"✅ 詳細紀錄 (含價格) 已存至: {output_path}")

if __name__ == "__main__":
    run_settings_backtest()