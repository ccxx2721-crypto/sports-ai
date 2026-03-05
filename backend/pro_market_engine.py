import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

print("🚀 今日獨贏價值分析（中文專業版）\n")

TEAM_ID_MAP = {
    "Los Angeles Lakers": "1610612747",
    "Golden State Warriors": "1610612744",
    "Boston Celtics": "1610612738",
    "Chicago Bulls": "1610612741",
    "Miami Heat": "1610612748",
    "Denver Nuggets": "1610612743",
    "Phoenix Suns": "1610612756",
    "Minnesota Timberwolves": "1610612750",
    "Toronto Raptors": "1610612761",
    "Brooklyn Nets": "1610612751",
    "New Orleans Pelicans": "1610612740",
    "Sacramento Kings": "1610612758",
    "Detroit Pistons": "1610612765",
    "San Antonio Spurs": "1610612759",
    "Dallas Mavericks": "1610612742",
    "Orlando Magic": "1610612753",
    "Utah Jazz": "1610612762",
    "Washington Wizards": "1610612764",
    "Houston Rockets": "1610612745",
    "Cleveland Cavaliers": "1610612739",
    "Philadelphia 76ers": "1610612755",
    "Milwaukee Bucks": "1610612749",
    "Atlanta Hawks": "1610612737",
    "Indiana Pacers": "1610612754",
    "Charlotte Hornets": "1610612766",
    "Memphis Grizzlies": "1610612763",
    "New York Knicks": "1610612752",
    "Oklahoma City Thunder": "1610612760",
    "Portland Trail Blazers": "1610612757"
}

TEAM_CN = {
    "New Orleans Pelicans": "紐奧良鵜鶘",
    "Sacramento Kings": "沙加緬度國王",
    "Detroit Pistons": "底特律活塞",
    "San Antonio Spurs": "聖安東尼奧馬刺",
    "Dallas Mavericks": "達拉斯獨行俠",
    "Orlando Magic": "奧蘭多魔術"
}

conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h&apiKey={API_KEY}"
games = requests.get(url).json()

results = []

for game in games:

    if not game.get("bookmakers"):
        continue

    home = game["home_team"]
    away = game["away_team"]

    if home not in TEAM_ID_MAP or away not in TEAM_ID_MAP:
        continue

    home_id = TEAM_ID_MAP[home]
    away_id = TEAM_ID_MAP[away]

    home_rating = c.execute("SELECT rating FROM team_ratings WHERE team_name = ?", (home_id,)).fetchone()
    away_rating = c.execute("SELECT rating FROM team_ratings WHERE team_name = ?", (away_id,)).fetchone()

    if not home_rating or not away_rating:
        continue

    home_rating = home_rating[0]
    away_rating = away_rating[0]

    model_prob = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))

    bookmaker = game["bookmakers"][0]
    for market in bookmaker["markets"]:
        if market["key"] == "h2h":
            for outcome in market["outcomes"]:
                if outcome["name"] == home:
                    odds = outcome["price"]
                    ev = (model_prob * odds) - 1

                    results.append({
                        "match_en": f"{away} @ {home}",
                        "match_cn": f"{TEAM_CN.get(away, away)} @ {TEAM_CN.get(home, home)}",
                        "ev": ev
                    })

results = sorted(results, key=lambda x: x["ev"], reverse=True)

print("📊 今日最有價值 Top 3：\n")

for r in results[:3]:

    ev_percent = r["ev"] * 100

    print("----------------------------------------")
    print(r["match_cn"])

    if ev_percent > 0:
        print(f"長期預期報酬：+{ev_percent:.2f}%")
        print(f"期望報酬率：每下注 100 元，理論長期可賺 {ev_percent:.1f} 元")
        if ev_percent > 15:
            print("建議等級：🔥🔥🔥 強烈價值")
        elif ev_percent > 8:
            print("建議等級：🔥🔥 中等價值")
        else:
            print("建議等級：🔥 微價值")
    else:
        print(f"長期預期報酬：{ev_percent:.2f}%")
        print(f"期望報酬率：每下注 100 元，理論長期會虧 {-ev_percent:.1f} 元")
        print("建議等級：❌ 不建議投注")

conn.close()

print("\n✅ 分析完成")