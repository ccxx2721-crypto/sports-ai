import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
BASE = "https://api.the-odds-api.com/v4"

async def fetch_odds(sport: str, date: str | None = None):

    url = f"{BASE}/sports/{sport}/odds"

    params = {
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american",
        "apiKey": API_KEY,
    }

    if date:
        params["date"] = date

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        return r.json()