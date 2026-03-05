from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
import os
import asyncio

# =========================
# 強制讀取 backend/.env
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

print("==== 環境變數讀取狀態 ====")
print("ODDS_API_KEY =", os.getenv("ODDS_API_KEY"))
print("BALLDONTLIE_API_KEY =", os.getenv("BALLDONTLIE_API_KEY"))
print("TELEGRAM_BOT_TOKEN =", os.getenv("TELEGRAM_BOT_TOKEN"))
print("TELEGRAM_CHAT_ID =", os.getenv("TELEGRAM_CHAT_ID"))
print("==========================")

from .arbitrage_engine import scan_arbitrage
from .live_odds_service import fetch_live_odds, normalize_odds
from .telegram_service import send_telegram_message
from .auto_scanner import auto_scan

app = FastAPI(title="EV 商業引擎 5.0")


# =========================
# 首頁
# =========================
@app.get("/")
def home():
    return {"message": "Live Arbitrage Engine Running"}


# =========================
# 手動即時套利掃描
# =========================
@app.get("/api/live-arbitrage")
def live_arbitrage():
    odds = fetch_live_odds()

    if not odds:
        return {"error": "無法取得即時盤口"}

    normalized = normalize_odds(odds)
    result = scan_arbitrage(normalized)

    # 如果有套利就發通知
    if result.get("arbitrage_found", 0) > 0:
        msg = f"🔥 發現 {result['arbitrage_found']} 個套利機會"
        send_telegram_message(msg)

    return result


# =========================
# 測試 Telegram
# =========================
@app.get("/api/test-telegram")
def test_telegram():
    send_telegram_message("✅ Telegram 測試成功")
    return {"status": "sent"}


# =========================
# 啟動時自動背景掃描
# =========================
@app.on_event("startup")
async def start_background_scanner():
    print("🚀 啟動 10 秒自動套利掃描")
    asyncio.create_task(auto_scan())