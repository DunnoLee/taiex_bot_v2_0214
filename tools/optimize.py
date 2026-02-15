import pandas as pd
import numpy as np
from itertools import product
import sys
import os

# 💡 導航修正
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def resample_data(df, interval):
    """
    將 1min 資料轉換為目標分鐘數 (如 '5T', '15T', '30T')
    """
    df = df.copy()
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)
    
    # 定義轉換邏輯
    resampled = df.resample(interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    return resampled.reset_index()

def run_backtest(df, short_p, long_p, moat):
    data = df.copy()
    
    # 💡 成本設定 (以點數計)
    # 2.2(單邊成本) * 2 + 1.0(預估滑點) = 5.4 點
    cost_per_round_turn = (15 + 7) * 2 / 10 + 1.0 
    
    # 1. 指標計算
    data['sma_s'] = data['Close'].rolling(window=short_p).mean()
    data['sma_l'] = data['Close'].rolling(window=long_p).mean()
    
    # 2. 訊號判斷
    data['signal'] = 0
    data.loc[data['sma_s'] > (data['sma_l'] + moat), 'signal'] = 1
    data.loc[data['sma_s'] < (data['sma_l'] - moat), 'signal'] = -1
    
    # 3. 計算部位與毛利
    data['position'] = data['signal'].shift(1).fillna(0)
    data['gross_pnl'] = data['Close'].diff() * data['position']
    
    # 4. 💡 扣除交易成本 (淨利計算)
    # 偵測部位變動 (只要 position 變動，就代表發生交易)
    trades_mask = data['position'].diff().fillna(0) != 0
    trade_count = trades_mask.sum()
    
    # 總成本 = 交易次數 * 單邊成本
    # 這裡我們用 trade_count 直接乘以單邊成本 (2.2 + 0.5滑點) 比較精確
    total_cost = trade_count * (2.2 + 0.5) 
    
    net_pnl = data['gross_pnl'].sum() - total_cost
    
    # 計算 MDD
    cum_pnl = data['gross_pnl'].cumsum() - (data['position'].diff().abs().cumsum() * 2.7)
    peak = cum_pnl.cummax()
    mdd = (cum_pnl - peak).min()
    
    return net_pnl, mdd, int(trade_count/2) # 回傳淨利, MDD, 交易對數

def main():
    csv_path = "data/history/TMF_FULL_REPLAY.csv"
    if not os.path.exists(csv_path):
        print("❌ 找不到資料檔")
        return

    raw_df = pd.read_csv(csv_path)
    
    # 💡 設定掃描的時間顆粒度: 5分鐘, 15分鐘, 30分鐘
    timeframes = {'5min': '5min', '15min': '15min', '30min': '30min'}
    
    # 💡 設定均線範圍
    short_range = [5, 10, 20]
    long_range = [60, 120, 240]
    moat_range = [0, 2, 5]

    all_results = []

    for tf_name, tf_code in timeframes.items():
        print(f"⌛ 正在轉換並掃描 {tf_name} 顆粒度...")
        tf_df = resample_data(raw_df, tf_code)
        
        combinations = list(product(short_range, long_range, moat_range))
        
        for s, l, m in combinations:
            if s >= l: continue
            pnl, mdd, trades = run_backtest(tf_df, s, l, m)
            
            all_results.append({
                'Timeframe': tf_name,
                'Short_P': s,
                'Long_P': l,
                'Moat': m,
                'PnL': pnl,
                'MDD': mdd,
                'Trades': trades,
                'Score': pnl / abs(mdd) if mdd != 0 else 0
            })

    report = pd.DataFrame(all_results)
    # 先看最高獲利
    top_pnl = report.sort_values(by='PnL', ascending=False).head(10)
    
    print("\n🏆 --- 跨時區最佳化英雄榜 ---")
    print(top_pnl.to_string(index=False))

if __name__ == "__main__":
    main()