import sqlite3
import requests
import os
from dotenv import load_dotenv
from math import sqrt
from scipy.stats import norm

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

print("🚀 全市場 EV 引擎\n")

# ===== 讀 Elo =====
conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

# ===== 抓 API =====
url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h,spreads,totals&apiKey={API_KEY}"
games = requests.get(url).json()

results = []

for game in games:

    home = game["home_team"]
    away = game["away_team"]

    bookmaker = game["bookmakers"][0]
    markets = bookmaker["markets"]

    moneyline_market = next((m for m in markets if m["key"] == "h2h"), None)
    spread_market = next((m for m in markets if m["key"] == "spreads"), None)
    total_market = next((m for m in markets if m["key"] == "totals"), None)

    if not moneyline_market:
        continue

    home_odds = next(o["price"] for o in moneyline_market["outcomes"] if o["name"] == home)

    # === Elo 讀取 ===
    home_rating = c.execute("SELECT rating FROM team_ratings WHERE team_name = ?", (home,)).fetchone()
    away_rating = c.execute("SELECT rating FROM team_ratings WHERE team_name = ?", (away,)).fetchone()

    if not home_rating or not away_rating:
        continue

    home_rating = home_rating[0]
    away_rating = away_rating[0]

    model_prob = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))

    # === Moneyline EV ===
    market_prob = 1 / home_odds
    moneyline_ev = (model_prob * home_odds) - 1

    # === Spread EV ===
    spread_ev = None
    if spread_market:
        spread_line = next(o["point"] for o in spread_market["outcomes"] if o["name"] == home)
        std = 12  # NBA 平均分差標準差
        cover_prob = 1 - norm.cdf(spread_line, loc=(home_rating - away_rating)/25, scale=std)
        spread_ev = (cover_prob * 1.91) - 1

    # === Totals EV ===
    totals_ev = None
    if total_market:
        total_line = total_market["outcomes"][0]["point"]
        predicted_total = 220 + (home_rating - 1500)/10
        over_prob = 1 - norm.cdf(total_line, loc=predicted_total, scale=15)
        totals_ev = (over_prob * 1.91) - 1

    results.append({
        "match": f"{away} @ {home}",
        "moneyline_ev": moneyline_ev,
        "spread_ev": spread_ev,
        "totals_ev": totals_ev
    })

# === 排序 ===
results = sorted(results, key=lambda x: x["moneyline_ev"], reverse=True)

print("📊 Top 3 價值場次：\n")

for r in results[:3]:
    print("----------------------------------")
    print(r["match"])
    print(f"獨贏 EV: {r['moneyline_ev']:.2%}")
    if r["spread_ev"]:
        print(f"讓分 EV: {r['spread_ev']:.2%}")
    if r["totals_ev"]:
        print(f"大小分 EV: {r['totals_ev']:.2%}")

conn.close()