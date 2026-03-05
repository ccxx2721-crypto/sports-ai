import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

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
    "Los Angeles Lakers": "洛杉磯湖人",
    "Golden State Warriors": "金州勇士",
    "Boston Celtics": "波士頓塞爾提克",
    "Chicago Bulls": "芝加哥公牛",
    "Miami Heat": "邁阿密熱火",
    "Denver Nuggets": "丹佛金塊",
    "Phoenix Suns": "鳳凰城太陽",
    "Minnesota Timberwolves": "明尼蘇達灰狼",
    "Toronto Raptors": "多倫多暴龍",
    "Brooklyn Nets": "布魯克林籃網",
    "New Orleans Pelicans": "紐奧良鵜鶘",
    "Sacramento Kings": "沙加緬度國王",
    "Detroit Pistons": "底特律活塞",
    "San Antonio Spurs": "聖安東尼奧馬刺",
    "Dallas Mavericks": "達拉斯獨行俠",
    "Orlando Magic": "奧蘭多魔術",
    "Utah Jazz": "猶他爵士",
    "Washington Wizards": "華盛頓巫師",
    "Houston Rockets": "休士頓火箭",
    "Cleveland Cavaliers": "克里夫蘭騎士",
    "Philadelphia 76ers": "費城76人",
    "Milwaukee Bucks": "密爾瓦基公鹿",
    "Atlanta Hawks": "亞特蘭大老鷹",
    "Indiana Pacers": "印第安納溜馬",
    "Charlotte Hornets": "夏洛特黃蜂",
    "Memphis Grizzlies": "曼菲斯灰熊",
    "New York Knicks": "紐約尼克",
    "Oklahoma City Thunder": "奧克拉荷馬雷霆",
    "Portland Trail Blazers": "波特蘭拓荒者"
}

print("🚀 今日賽事預測\n")

url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h&apiKey={API_KEY}"
response = requests.get(url)
games = response.json()

conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

for game in games:

    home_en = game["home_team"]
    away_en = game["away_team"]

    # 只抓第一個 bookmaker
    bookmaker = game["bookmakers"][0]
    home_odds = None

    for outcome in bookmaker["markets"][0]["outcomes"]:
        if outcome["name"] == home_en:
            home_odds = outcome["price"]

    if not home_odds:
        continue

    if home_en not in TEAM_ID_MAP:
        print(f"⚠ 無ID對照: {home_en}")
        continue

    home_id = TEAM_ID_MAP[home_en]
    away_id = TEAM_ID_MAP.get(away_en)

    home_rating = c.execute(
        "SELECT rating FROM team_ratings WHERE team_name = ?",
        (home_id,)
    ).fetchone()

    away_rating = c.execute(
        "SELECT rating FROM team_ratings WHERE team_name = ?",
        (away_id,)
    ).fetchone()

    if not home_rating or not away_rating:
        print(f"⚠ Elo不存在: {home_en}")
        continue

    home_rating = home_rating[0]
    away_rating = away_rating[0]

    model_prob = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))
    bookmaker_prob = 1 / home_odds
    diff = model_prob - bookmaker_prob

    home_cn = TEAM_CN.get(home_en, home_en)
    away_cn = TEAM_CN.get(away_en, away_en)

    print("----------------------------------------")
    print(f"【客隊】{away_cn}")
    print("        VS")
    print(f"【主隊】{home_cn}\n")

    print(f"主勝賠率：{home_odds}")
    print(f"莊家預期主隊勝率：{bookmaker_prob:.2%}")
    print(f"模型預測主隊勝率：{model_prob:.2%}\n")

    print(f"模型比莊家高出：{diff:.2%}")

    if diff > 0.05:
        print("結論：🔥 主隊有投注價值")
    elif diff < -0.05:
        print("結論：❌ 主隊不建議投注")
    else:
        print("結論：⚖ 接近合理盤")

conn.close()

print("\n✅ 今日預測完成")