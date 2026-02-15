# tools/mock_replay.py
import pandas as pd
import time
import os
import sys

# 確保路徑正確
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from core.trader import Trader
from core.commander import Commander
from core.aggregator import BarAggregator
from strategies.ma_strategy import MAStrategy
from core.notifier import TelegramNotifier

def run_mock_replay():
    # 強制開啟 Dry Run
    Settings.DRY_RUN = True
    
    print("🛡️ 初始化演習系統...")
    
    # 1. 組裝零件
    notifier = TelegramNotifier()
    trader = Trader(api=None) # 演習無 API
    strategy = MAStrategy(
        short_p=Settings.SHORT_P, long_p=Settings.LONG_P,
        moat=Settings.MOAT, stop_loss_pts=Settings.STOP_LOSS,
        trader=trader
    )
    commander = Commander(trader, strategy, notifier)
    aggregator = BarAggregator(timeframe=Settings.TIMEFRAME)

    # 2. 讀取資料
    csv_path = "data/history/TMF_FULL_REPLAY.csv"
    if not os.path.exists(csv_path):
        print("❌ 找不到歷史資料 CSV")
        return
        
    df_raw = pd.read_csv(csv_path)
    print(f"📖 載入 {len(df_raw)} 筆資料，開始演習...")
    print("💡 提示：演習中可隨時用 Telegram 發送 /status 查看狀態")

    # 3. 模擬迴圈
    for i, row in df_raw.iterrows():
        tick_time = row['Time']
        price = float(row['Close'])
        vol = int(row.get('Volume', 0))

        # 餵資料給合成器
        bar_complete, df_hist = aggregator.add_tick(tick_time, price, vol)
        
        # K棒完成 -> 呼叫策略
        if bar_complete:
            strategy.on_bar(df_hist)
            # 注意：這裡不需要手動 print，因為 strategy 會呼叫 trader，trader 會 print 和發 TG

        # 💡 每 100 筆模擬 Check 一次手機指令 (模擬非同步)
        if i % 100 == 0:
            commander.poll_commands()
            
        # 模擬速度控制 (可調快慢)
        # time.sleep(0.001) 

    print("✅ 演習結束。")

if __name__ == "__main__":
    run_mock_replay()