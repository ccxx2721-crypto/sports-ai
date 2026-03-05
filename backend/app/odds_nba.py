from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

import httpx
from cachetools import TTLCache

ODDS_API_BASE = os.getenv("ODDS_API_BASE", "https://api.the-odds-api.com")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()

_cache = TTLCache(maxsize=20, ttl=60)  # 60 秒快取，避免打爆額度


class OddsAPIError(Exception):
    pass


def _pick_totals_pack_from_event(
    event: Dict[str, Any],
    preferred_books: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Return:
    {"total_line": 224.5, "bookmaker": "fanduel", "over_price": -110, "under_price": -110}
    """
    books = event.get("bookmakers") or []
    if not books:
        return {"total_line": None, "bookmaker": None, "over_price": None, "under_price": None}

    if preferred_books:
        books = sorted(books, key=lambda b: 0 if b.get("key") in preferred_books else 1)

    for b in books:
        for m in (b.get("markets") or []):
            if m.get("key") != "totals":
                continue

            outcomes = m.get("outcomes") or []
            total_line = None
            over_price = None
            under_price = None

            for o in outcomes:
                name = (o.get("name") or "").lower()
                pt = o.get("point")
                price = o.get("price")

                if isinstance(pt, (int, float)):
                    total_line = float(pt)

                if isinstance(price, (int, float)):
                    if name == "over":
                        over_price = int(price)
                    elif name == "under":
                        under_price = int(price)

            if total_line is not None:
                return {
                    "total_line": total_line,
                    "bookmaker": b.get("key"),
                    "over_price": over_price,
                    "under_price": under_price,
                }

    return {"total_line": None, "bookmaker": None, "over_price": None, "under_price": None}


async def fetch_nba_today_totals(
    sport: str = "nba",  # ✅ 收到也不會炸（目前先固定用 NBA key）
    regions: str = "us",
    odds_format: str = "american",
) -> List[Dict[str, Any]]:
    """
    The Odds API v4:
    GET /v4/sports/basketball_nba/odds?regions=us&markets=totals&oddsFormat=american&apiKey=...
    """
    if not ODDS_API_KEY:
        raise OddsAPIError("ODDS_API_KEY is missing. Set it in environment variables.")

    cache_key = f"nba:{regions}:{odds_format}"
    if cache_key in _cache:
        return _cache[cache_key]

    url = f"{ODDS_API_BASE}/v4/sports/basketball_nba/odds"
    params = {
        "regions": regions,
        "markets": "totals",
        "oddsFormat": odds_format,
        "apiKey": ODDS_API_KEY,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise OddsAPIError(f"Odds API error {resp.status_code}: {resp.text[:200]}")
        data = resp.json()

    out: List[Dict[str, Any]] = []
    for ev in data:
        pack = _pick_totals_pack_from_event(ev, preferred_books=None)
        out.append(
            {
                "event_id": ev.get("id"),
                "commence_time": ev.get("commence_time"),
                "home_team": ev.get("home_team"),
                "away_team": ev.get("away_team"),
                "total_line": pack["total_line"],
                "bookmaker": pack["bookmaker"],
                "over_price": pack["over_price"],
                "under_price": pack["under_price"],
            }
        )

    out.sort(key=lambda x: x.get("commence_time") or "")
    _cache[cache_key] = out
    return out