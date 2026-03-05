from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import sqlite3
import requests
import os
from datetime import date

app = FastAPI()

DB_PATH = "history.db"
ODDS_KEY = os.getenv("ODDS_API_KEY")

TEAM_ZH = {
    "Atlanta Hawks": "亞特蘭大老鷹",
    "Boston Celtics": "波士頓塞爾提克",
    "Brooklyn Nets": "布魯克林籃網",
    "Charlotte Hornets": "夏洛特黃蜂",
    "Chicago Bulls": "芝加哥公牛",
    "Cleveland Cavaliers": "克里夫蘭騎士",
    "Dallas Mavericks": "達拉斯獨行俠",
    "Denver Nuggets": "丹佛金塊",
    "Detroit Pistons": "底特律活塞",
    "Golden State Warriors": "金州勇士",
    "Houston Rockets": "休士頓火箭",
    "Indiana Pacers": "印第安那溜馬",
    "LA Clippers": "洛杉磯快艇",
    "Los Angeles Lakers": "洛杉磯湖人",
    "Memphis Grizzlies": "曼菲斯灰熊",
    "Miami Heat": "邁阿密熱火",
    "Milwaukee Bucks": "密爾瓦基公鹿",
    "Minnesota Timberwolves": "明尼蘇達灰狼",
    "New Orleans Pelicans": "紐奧良鵜鶘",
    "New York Knicks": "紐約尼克",
    "Oklahoma City Thunder": "奧克拉荷馬雷霆",
    "Orlando Magic": "奧蘭多魔術",
    "Philadelphia 76ers": "費城七六人",
    "Phoenix Suns": "鳳凰城太陽",
    "Portland Trail Blazers": "波特蘭拓荒者",
    "Sacramento Kings": "沙加緬度國王",
    "San Antonio Spurs": "聖安東尼奧馬刺",
    "Toronto Raptors": "多倫多暴龍",
    "Utah Jazz": "猶他爵士",
    "Washington Wizards": "華盛頓巫師"
}


def get_db_games(selected_date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM games WHERE game_date=?", (selected_date,))
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_api_games():
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={ODDS_KEY}&regions=us&markets=spreads,totals"
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return r.json()


@app.get("/", response_class=HTMLResponse)
def home(selected_date: str = Query(None)):

    if not selected_date:
        selected_date = str(date.today())

    games = get_db_games(selected_date)

    html = """
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body{background:#0f1b2a;color:white;font-family:Arial;padding:20px;}
    .card{background:#1c2533;padding:20px;border-radius:15px;margin-bottom:25px;
    box-shadow:0 0 25px #00ffaa55;}
    .teams{display:flex;justify-content:space-between;font-weight:bold;}
    .yellow{color:#ffcc00;font-size:20px;}
    </style>
    </head>
    <body>
    <h2>🏀 NBA 商業級儀表板</h2>
    <form method='get'>
        <input type='date' name='selected_date' value='""" + selected_date + """'>
        <button type='submit'>查詢</button>
    </form><hr>
    """

    # ✅ 如果資料庫沒有 → 用 API 即時抓
    if not games:
        api_games = fetch_api_games()

        if not api_games:
            html += "<h3 style='color:red'>API 無法取得資料</h3>"
        else:
            html += "<h3 style='color:#00ffaa'>⚡ 即時 API 資料</h3>"

            for game in api_games:
                away = TEAM_ZH.get(game["away_team"], game["away_team"])
                home = TEAM_ZH.get(game["home_team"], game["home_team"])

                html += f"""
                <div class='card'>
                <div class='teams'>
                    <div>【客隊】{away}</div>
                    <div>【主隊】{home}</div>
                </div>
                </div>
                """

    else:
        html += "<h3 style='color:#00ffaa'>📚 歷史資料</h3>"

        for g in games:
            away = TEAM_ZH.get(g[2], g[2])
            home = TEAM_ZH.get(g[3], g[3])

            html += f"""
            <div class='card'>
            <div class='teams'>
                <div>【客隊】{away}</div>
                <div>【主隊】{home}</div>
            </div>
            </div>
            """

    html += "</body></html>"
    return html