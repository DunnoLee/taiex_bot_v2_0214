import os
from dotenv import load_dotenv

# 1. 載入 .env
load_dotenv()

class Settings:
    # --- 基礎設定 ---
    SHIOAJI_API_KEY = os.getenv("SHIOAJI_API_KEY")
    SHIOAJI_SECRET_KEY = os.getenv("SHIOAJI_SECRET_KEY")
    
    # --- 憑證路徑處理 (關鍵修改) ---
    _cert_path = os.getenv("SHIOAJI_CERT_PATH")
    
    # 如果有設定路徑，就把它轉成電腦的絕對路徑
    # 例如 ./certs/Sinopac.pfx -> /Users/dunnolee/taiex_bot_v2/certs/Sinopac.pfx
    if _cert_path:
        SHIOAJI_CERT_PATH = os.path.abspath(_cert_path)
    else:
        SHIOAJI_CERT_PATH = None
        
    SHIOAJI_CERT_PASSWORD = os.getenv("SHIOAJI_CERT_PASSWORD")
    SHIOAJI_PERSON_ID = os.getenv("SHIOAJI_PERSON_ID")

    # --- Telegram ---
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # --- 交易目標 ---
    TARGET_CONTRACT = os.getenv("TARGET_CONTRACT", "TMF202603")

    MOAT = 0
    STOP_LOSS=400
    SHORT_P=10
    LONG_P=240
    TIMEFRAME = 30

    # 開關，演習時若不想被轟炸可以關掉
    ENABLE_NOTIFIER = True

    # --- 🔴 核彈發射鑰匙 (最重要的開關) ---
    # True  = 演習模式 (只會印 Log，絕對不會送出單)
    # False = 實戰模式 (真金白銀，請小心！)
    DRY_RUN = True