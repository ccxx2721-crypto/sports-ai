import os
import httpx
from datetime import date

API_KEY = os.environ.get("BASKETBALL_API_KEY")

if not API_KEY:
    raise ValueError("BASKETBALL_API_KEY 未設定")

BASE_URL = "https://v1.basketball.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}


def classify_status(short_status: str):
    if short_status in ["NS"]:
        return "未開賽"
    elif short_status in ["Q1", "Q2", "Q3", "Q4", "OT", "BT", "HT"]:
        return "進行中"
    elif short_status in ["FT", "AOT"]:
        return "已完賽"
    else:
        return "其他"


async def fetch_games(
    target_date: str = None,
    league: int = None,
    live: bool = False
):
    params = {}

    if live:
        params["live"] = "all"
    else:
        params["date"] = target_date or str(date.today())

    if league:
        params["league"] = league

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{BASE_URL}/games",
            params=params,
            headers=HEADERS
        )

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json().get("response", [])

    games = []

    for g in data:
        short_status = g.get("status", {}).get("short")

        games.append({
            "game_id": g.get("id"),
            "league": g.get("league", {}).get("name"),
            "home_team": g.get("teams", {}).get("home", {}).get("name"),
            "away_team": g.get("teams", {}).get("away", {}).get("name"),
            "home_score": g.get("scores", {}).get("home", {}).get("total"),
            "away_score": g.get("scores", {}).get("away", {}).get("total"),
            "status": classify_status(short_status),
            "raw_status": short_status,
            "period": g.get("status", {}).get("period"),
            "clock": g.get("status", {}).get("clock")
        })

    return games