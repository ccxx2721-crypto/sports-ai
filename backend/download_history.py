import os
import requests
import csv
import time
from dotenv import load_dotenv

load_dotenv()

BALLDONTLIE_KEY = os.getenv("BALLDONTLIE_API_KEY")

BASE_URL = "https://api.balldontlie.io/v1/games"
SEASONS = [2023, 2024, 2025]
OUTPUT_PATH = "data/nba_history.csv"

os.makedirs("data", exist_ok=True)

def safe_request(params, headers):
    for attempt in range(5):
        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response

        if response.status_code == 429:
            print("⚠️ 429 Too Many Requests，等待 5 秒...")
            time.sleep(5)
            continue

        print("API Error:", response.text)
        return None

    return None

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)
    writer.writerow(["home_team", "away_team", "home_score", "away_score", "date"])

    total_games = 0

    for season in SEASONS:

        print(f"\n==== 開始下載 {season} 賽季 ====")

        page = 1

        while True:

            params = {
                "seasons[]": season,
                "per_page": 100,
                "page": page
            }

            headers = {
                "Authorization": f"Bearer {BALLDONTLIE_KEY}"
            }

            response = safe_request(params, headers)

            if not response:
                break

            data = response.json()
            games = data.get("data", [])

            if not games:
                break

            games.sort(key=lambda x: x["date"])

            for game in games:

                if game["home_team_score"] is None:
                    continue

                writer.writerow([
                    game["home_team"]["name"],
                    game["visitor_team"]["name"],
                    game["home_team_score"],
                    game["visitor_team_score"],
                    game["date"]
                ])

                total_games += 1

            print(f"Season {season} Page {page} 完成")

            page += 1
            time.sleep(1)  # 防止 API 爆量

    print("\n===== 下載完成 =====")
    print("總比賽數:", total_games)