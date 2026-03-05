import sqlite3
import requests
import os
from dotenv import load_dotenv
import math

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

print("🚀 安全版全市場引擎\n")

# === Elo DB ===
conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

# === API ===
url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h,spreads,totals&apiKey={API_KEY}"
response = requests.get(url)

if response.status_code != 200:
    print("❌ API 錯誤")
    exit()

games = response.json()

results = []

for game in games:

    if not game.get("bookmakers"):
        continue

    home = game["home_team"]
    away = game["away_team"]

    bookmaker = game["bookmakers"][0]
    markets = bookmaker.get("markets", [])

    # === 讀 Elo ===
    home_rating = c.execute(
        "SELECT rating FROM team_ratings WHERE team_name = ?",
        (home,)
    ).fetchone()

    away_rating = c.execute(
        "SELECT rating FROM team_ratings WHERE team_name = ?",
        (away,)
    ).fetchone()

    if not home_rating or not away_rating:
        continue

    home_rating = home_rating[0]
    away_rating = away_rating[0]

    # === Elo 勝率 ===
    model_prob = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))

    moneyline_ev = None
    spread_ev = None
    totals_ev = None

    # === 遍歷市場 ===
    for market in markets:

        # Moneyline
        if market["key"] == "h2h":
            for outcome in market["outcomes"]:
                if outcome["name"] == home:
                    odds = outcome["price"]
                    market_prob = 1 / odds
                    moneyline_ev = (model_prob * odds) - 1

        # Spread
        if market["key"] == "spreads":
            for outcome in market["outcomes"]:
                if outcome["name"] == home:
                    spread_line = outcome.get("point")
                    if spread_line is not None:
                        # 用簡單 logistic 近似
                        spread_prob = 1 / (1 + math.exp(-spread_line/6))
                        spread_ev = (spread_prob * 1.91) - 1

        # Totals
        if market["key"] == "totals":
            for outcome in market["outcomes"]:
                total_line = outcome.get("point")
                if total_line:
                    predicted_total = 220
                    over_prob = 1 / (1 + math.exp(-(predicted_total - total_line)/10))
                    totals_ev = (over_prob * 1.91) - 1
                    break

    results.append({
        "match": f"{away} @ {home}",
        "moneyline_ev": moneyline_ev,
        "spread_ev": spread_ev,
        "totals_ev": totals_ev
    })

# === 排序（只看有值的） ===
results = [r for r in results if r["moneyline_ev"] is not None]
results = sorted(results, key=lambda x: x["moneyline_ev"], reverse=True)

print("📊 Top 3 價值場次：\n")

for r in results[:3]:
    print("----------------------------------")
    print(r["match"])
    print(f"獨贏 EV: {r['moneyline_ev']:.2%}")
    if r["spread_ev"] is not None:
        print(f"讓分 EV: {r['spread_ev']:.2%}")
    if r["totals_ev"] is not None:
        print(f"大小分 EV: {r['totals_ev']:.2%}")

conn.close()