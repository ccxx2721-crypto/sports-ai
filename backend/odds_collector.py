import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
SPORT = "basketball_nba"

# -----------------------------
# Step 1：先抓今日比賽 events
# -----------------------------

events_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/events"

events_params = {
    "apiKey": API_KEY
}

events_response = requests.get(events_url, params=events_params)

print("Events HTTP Status:", events_response.status_code)

events_data = events_response.json()

if not isinstance(events_data, list):
    print("❌ Events API 錯誤:")
    print(events_data)
    exit()

print("📅 今日 NBA 比賽數:", len(events_data))

if len(events_data) == 0:
    print("⚠ 今日無 NBA 比賽")
    exit()

# -----------------------------
# Step 2：抓賠率
# -----------------------------

odds_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

odds_params = {
    "apiKey": API_KEY,
    "regions": "us",
    "markets": "h2h",
    "oddsFormat": "decimal"
}

odds_response = requests.get(odds_url, params=odds_params)

print("Odds HTTP Status:", odds_response.status_code)

odds_data = odds_response.json()

if not isinstance(odds_data, list):
    print("❌ Odds API 錯誤:")
    print(odds_data)
    exit()

print("📊 抓到賠率場次:", len(odds_data))

# -----------------------------
# Step 3：寫入資料庫
# -----------------------------

conn = sqlite3.connect("ratings.db")
c = conn.cursor()

# 清空舊資料
c.execute("DELETE FROM odds_today")

insert_count = 0

for game in odds_data:

    game_id = game.get("id")
    home = game.get("home_team")
    away = game.get("away_team")

    bookmakers = game.get("bookmakers", [])

    if not bookmakers:
        continue

    # 取第一家 bookmaker（避免沒有 pinnacle）
    book = bookmakers[0]

    markets = book.get("markets", [])

    for market in markets:
        if market.get("key") != "h2h":
            continue

        outcomes = market.get("outcomes", [])

        try:
            home_ml = next(o["price"] for o in outcomes if o["name"] == home)
            away_ml = next(o["price"] for o in outcomes if o["name"] == away)
        except:
            continue

        c.execute("""
        INSERT INTO odds_today
        (game_id, home_team, away_team, home_ml, away_ml, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            home,
            away,
            home_ml,
            away_ml,
            datetime.now().isoformat()
        ))

        insert_count += 1

conn.commit()
conn.close()

print("✅ 寫入場次:", insert_count)
print("🎯 今日賠率更新完成")