import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
SPORT = "basketball_nba"

# -----------------------------
# 抓完整盤口 (ML + Spread + Total)
# -----------------------------

odds_url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

params = {
    "apiKey": API_KEY,
    "regions": "us",
    "markets": "h2h,spreads,totals",
    "oddsFormat": "decimal"
}

response = requests.get(odds_url, params=params)

print("HTTP:", response.status_code)

data = response.json()

if not isinstance(data, list):
    print("API錯誤:", data)
    exit()

conn = sqlite3.connect("ratings.db")
c = conn.cursor()

c.execute("DELETE FROM odds_today")

insert_count = 0

for game in data:

    game_id = game.get("id")
    home = game.get("home_team")
    away = game.get("away_team")

    bookmakers = game.get("bookmakers", [])
    if not bookmakers:
        continue

    book = bookmakers[0]
    markets = book.get("markets", [])

    home_ml = away_ml = None
    home_spread = away_spread = None
    total_line = None

    for market in markets:

        if market["key"] == "h2h":
            outcomes = market["outcomes"]
            for o in outcomes:
                if o["name"] == home:
                    home_ml = o["price"]
                elif o["name"] == away:
                    away_ml = o["price"]

        if market["key"] == "spreads":
            outcomes = market["outcomes"]
            for o in outcomes:
                if o["name"] == home:
                    home_spread = o.get("point")

        if market["key"] == "totals":
            outcomes = market["outcomes"]
            for o in outcomes:
                if o["name"] == "Over":
                    total_line = o.get("point")

    if home_ml and away_ml:
        c.execute("""
        INSERT INTO odds_today
        (game_id, home_team, away_team, 
         home_ml, away_ml, 
         home_spread, total_line, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            game_id,
            home,
            away,
            home_ml,
            away_ml,
            home_spread,
            total_line,
            datetime.now().isoformat()
        ))

        insert_count += 1

conn.commit()
conn.close()

print("寫入:", insert_count)