import requests
import sqlite3
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

def archive_today():

    today = str(date.today())

    conn = sqlite3.connect("history.db")
    c = conn.cursor()

    # 自動建表
    c.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_date TEXT,
        away_team TEXT,
        home_team TEXT,
        spread REAL,
        total REAL,
        home_score INTEGER,
        away_score INTEGER
    )
    """)

    # 防止同一天重複寫入
    c.execute("SELECT COUNT(*) FROM games WHERE game_date=?", (today,))
    count = c.fetchone()[0]

    if count > 0:
        print("⚠ 今日已存過資料，跳過")
        conn.close()
        return

    odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=spreads,totals&apiKey={API_KEY}"
    scores_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?daysFrom=1&apiKey={API_KEY}"

    odds_data = requests.get(odds_url).json()
    scores_data = requests.get(scores_url).json()

    score_map = {}

    if isinstance(scores_data, list):
        for s in scores_data:
            if s.get("completed"):
                key = f"{s['away_team']}@{s['home_team']}"
                score_map[key] = {
                    "home_score": int(s["scores"][1]["score"]),
                    "away_score": int(s["scores"][0]["score"])
                }

    for game in odds_data:

        home = game["home_team"]
        away = game["away_team"]

        if not game.get("bookmakers"):
            continue

        bookmaker = game["bookmakers"][0]

        spread_line = None
        total_line = None

        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for o in market["outcomes"]:
                    if o["name"] == home:
                        spread_line = o["point"]

            if market["key"] == "totals":
                for o in market["outcomes"]:
                    total_line = o["point"]

        match_key = f"{away}@{home}"

        home_score = None
        away_score = None

        if match_key in score_map:
            home_score = score_map[match_key]["home_score"]
            away_score = score_map[match_key]["away_score"]

        c.execute("""
        INSERT INTO games 
        (game_date, away_team, home_team, spread, total, home_score, away_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (today, away, home, spread_line, total_line, home_score, away_score))

    conn.commit()
    conn.close()

    print("✅ 今日盤口已成功存檔")

if __name__ == "__main__":
    archive_today()