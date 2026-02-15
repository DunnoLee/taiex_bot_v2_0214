import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# 導航修正
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def plot_pro_results():
    file_path = "data/backtest_detail.csv"
    if not os.path.exists(file_path):
        print("❌ 找不到 backtest_detail.csv，請先執行新版 backtest.py")
        return

    # 1. 載入交易日誌
    df = pd.read_csv(file_path)
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time', inplace=True)

    # 2. 建立畫布
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, 
                                   gridspec_kw={'height_ratios': [3, 1]})

    # --- 上圖：資產曲線 (Equity) ---
    ax1.step(df.index, df['equity'], where='post', color='#2ca02c', lw=2, label='Net Equity (Pts)')
    ax1.set_title('TMF Strategy with Stop-Loss (MA 10/240, 30min)', fontsize=14)
    ax1.set_ylabel('Points')
    ax1.grid(True, alpha=0.3)
    
    # 標註停損點 (在圖上找 STOP_LOSS 字樣)
    sl_points = df[df['Action'].str.contains('STOP_LOSS')]
    ax1.scatter(sl_points.index, sl_points['equity'], color='red', marker='x', s=50, label='Stop Loss Triggered')
    ax1.legend(loc='upper left')

    # --- 下圖：回撤 (Drawdown) ---
    ax2.fill_between(df.index, df['drawdown'], 0, color='#d62728', alpha=0.4, step='post')
    ax2.set_title('Drawdown Analysis', fontsize=12)
    ax2.set_ylabel('Points')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_img = "data/backtest_pro_chart.png"
    plt.savefig(output_img)
    print(f"✅ 新版圖表已生成：{output_img}")
    plt.show()

if __name__ == "__main__":
    plot_pro_results()