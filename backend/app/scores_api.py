import os
import httpx

API_KEY = os.getenv("SPORTS_API_KEY")

BASE_URL = "https://v1.basketball.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

async def fetch_games(sport: str, target_date):

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{BASE_URL}/games",
            params={"date": target_date},
            headers=HEADERS
        )

    data = res.json().get("response", [])

    games = []

    for g in data:
        games.append({
            "game_id": g["id"],
            "home_team": g["teams"]["home"]["name"],
            "away_team": g["teams"]["away"]["name"],
            "status": g["status"]["long"],
            "home_score": g["scores"]["home"]["points"],
            "away_score": g["scores"]["away"]["points"],
            "period": g["status"]["period"],
            "time": g["status"]["clock"]
        })

    return games