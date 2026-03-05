import requests
import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")


def fetch_live_odds():

    if not ODDS_API_KEY:
        print("❌ ODDS_API_KEY 未讀取到")
        return []

    print("✅ ODDS_API_KEY 已讀取")

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("API Error:", response.status_code, response.text)
        return []

    return response.json()


def normalize_odds(raw_data):

    matches = []

    for game in raw_data:

        match = {
            "match": f"{game['home_team']} vs {game['away_team']}",
            "books": []
        }

        for bookmaker in game.get("bookmakers", []):

            for market in bookmaker.get("markets", []):

                if market["key"] == "h2h":

                    home_odds = None
                    away_odds = None

                    for outcome in market["outcomes"]:
                        if outcome["name"] == game["home_team"]:
                            home_odds = outcome["price"]
                        if outcome["name"] == game["away_team"]:
                            away_odds = outcome["price"]

                    if home_odds and away_odds:
                        match["books"].append({
                            "book": bookmaker["title"],
                            "home": home_odds,
                            "away": away_odds
                        })

        if len(match["books"]) >= 2:
            matches.append(match)

    return matches