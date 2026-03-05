from __future__ import annotations
import os
import httpx
from cachetools import TTLCache
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

load_dotenv()

THEODDS_API_BASE = os.getenv(
    "THEODDS_API_BASE",
    "https://api.the-odds-api.com"
).rstrip("/")

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

_cache = TTLCache(maxsize=64, ttl=60)

class OddsAPIError(Exception):
    pass

async def fetch_odds(
    sport_key: str,
    regions: str = "us",
    markets: str = "h2h,spreads,totals",
    odds_format: str = "american",
    date: str | None = None,
) -> List[Dict[str, Any]]:

    if not ODDS_API_KEY:
        raise OddsAPIError("ODDS_API_KEY missing")

    cache_key = f"{sport_key}:{date}"
    if cache_key in _cache:
        return _cache[cache_key]

    url = f"{THEODDS_API_BASE}/v4/sports/{sport_key}/odds"

    params = {
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format,
        "apiKey": ODDS_API_KEY,
    }

    if date:
        params["date"] = date

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, params=params)

        if resp.status_code != 200:
            raise OddsAPIError(f"{resp.status_code} {resp.text}")

    data = resp.json()
    _cache[cache_key] = data
    return data