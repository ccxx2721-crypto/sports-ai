from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


# -----------------------------
# Odds math
# -----------------------------
def american_to_decimal(odds: int) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be 0")
    if odds > 0:
        return 1.0 + odds / 100.0
    return 1.0 + 100.0 / abs(odds)


def american_to_implied_prob(odds: int) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be 0")
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return abs(odds) / (abs(odds) + 100.0)


def normalize_probs(probs: List[float]) -> List[float]:
    s = sum(probs)
    if s <= 0:
        return probs
    return [p / s for p in probs]


# -----------------------------
# Robust market/outcomes extractor
# Supports:
#   1) book["h2h"] = [ {name, price}, ...]
#   2) book["markets"] = {"h2h":[...], "totals":[...]}
#   3) book["markets"] = [ {"key":"h2h","outcomes":[...]}, ... ]  (The Odds API default)
# -----------------------------
def extract_outcomes(book: Dict[str, Any], market_key: str) -> List[Dict[str, Any]]:
    # Case 1: flattened directly on book
    direct = book.get(market_key)
    if isinstance(direct, list):
        return [x for x in direct if isinstance(x, dict)]

    markets = book.get("markets")

    # Case 2: markets is dict mapping -> list[outcomes]
    if isinstance(markets, dict):
        m = markets.get(market_key)
        if isinstance(m, list):
            return [x for x in m if isinstance(x, dict)]
        # sometimes dict maps to {"outcomes":[...]}
        if isinstance(m, dict):
            outs = m.get("outcomes")
            if isinstance(outs, list):
                return [x for x in outs if isinstance(x, dict)]
        return []

    # Case 3: markets is list of {key, outcomes}
    if isinstance(markets, list):
        for m in markets:
            if not isinstance(m, dict):
                continue
            if m.get("key") == market_key:
                outs = m.get("outcomes")
                if isinstance(outs, list):
                    return [x for x in outs if isinstance(x, dict)]
                # in rare wrappers, outcomes are already under market key
                return []
        return []

    return []


def pick_best_prices_h2h(event: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Return best american odds per team across books:
    {
      "Team A": {"price": -105, "book": "fanduel", "title":"FanDuel", "decimal":1.95},
      "Team B": {"price": +120, ...}
    }
    """
    best: Dict[str, Dict[str, Any]] = {}
    books = event.get("books") or event.get("bookmakers") or []
    if not isinstance(books, list):
        return best

    for b in books:
        if not isinstance(b, dict):
            continue
        book_key = b.get("book") or b.get("key") or b.get("title") or "book"
        title = b.get("title") or book_key

        outcomes = extract_outcomes(b, "h2h")
        if not outcomes:
            continue

        for o in outcomes:
            if not isinstance(o, dict):
                continue
            name = o.get("name")
            price = o.get("price")
            if not isinstance(name, str):
                continue
            if not isinstance(price, (int, float)) or not math.isfinite(float(price)) or int(price) == 0:
                continue

            price_int = int(price)
            try:
                dec = american_to_decimal(price_int)
            except Exception:
                continue

            cur = best.get(name)
            if cur is None or dec > cur["decimal"]:
                best[name] = {
                    "price": price_int,
                    "decimal": dec,
                    "book": book_key,
                    "title": title,
                }

    return best


def calc_ev_pick_from_best_prices(best: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    For a 2-way h2h market:
      - compute implied probs from best odds
      - remove vig by normalization to get fair probs
      - compute EV for each side: fair_prob * decimal - 1
      - return the side with higher EV
    """
    if len(best) < 2:
        return None

    # Take top 2 teams by availability (usually exactly home/away)
    teams = list(best.keys())[:2]
    a, b = teams[0], teams[1]

    pa = best[a]["price"]
    pb = best[b]["price"]

    try:
        ia = american_to_implied_prob(int(pa))
        ib = american_to_implied_prob(int(pb))
    except Exception:
        return None

    fa, fb = normalize_probs([ia, ib])

    eva = fa * float(best[a]["decimal"]) - 1.0
    evb = fb * float(best[b]["decimal"]) - 1.0

    if eva >= evb:
        return {
            "team": a,
            "price": int(pa),
            "decimal": float(best[a]["decimal"]),
            "fair_prob": fa,
            "ev": eva,
            "book": best[a]["book"],
            "title": best[a]["title"],
        }
    return {
        "team": b,
        "price": int(pb),
        "decimal": float(best[b]["decimal"]),
        "fair_prob": fb,
        "ev": evb,
        "book": best[b]["book"],
        "title": best[b]["title"],
    }


def calc_surebet_h2h(best: Dict[str, Dict[str, Any]], bankroll: float) -> Optional[Dict[str, Any]]:
    """
    For a 2-way surebet, using best decimal odds:
      inv = 1/da + 1/db
      if inv < 1 => arbitrage exists
      stake_a = bankroll * (1/da) / inv
      stake_b = bankroll * (1/db) / inv
      profit = bankroll*(1/inv - 1)
      roi = 1/inv - 1
    """
    if len(best) < 2:
        return None
    teams = list(best.keys())[:2]
    a, b = teams[0], teams[1]
    da = float(best[a]["decimal"])
    db = float(best[b]["decimal"])
    inv = (1.0 / da) + (1.0 / db)
    if inv >= 1.0:
        return None

    bankroll = float(bankroll)
    stake_a = bankroll * (1.0 / da) / inv
    stake_b = bankroll * (1.0 / db) / inv
    profit = bankroll * (1.0 / inv - 1.0)
    roi = (1.0 / inv - 1.0)

    return {
        "teams": [a, b],
        "best": {
            a: best[a],
            b: best[b],
        },
        "bankroll": bankroll,
        "stakes": {
            a: round(stake_a, 2),
            b: round(stake_b, 2),
        },
        "roi": roi,          # 0.02 => 2%
        "profit": round(profit, 2),
    }


def build_parlays(picks: List[Dict[str, Any]], legs: int = 2) -> Dict[str, Any]:
    """
    Simple parlay builder: take top EV picks and group as 2-leg / 3-leg etc.
    """
    picks_sorted = sorted(picks, key=lambda x: float(x.get("ev", -999)), reverse=True)
    legs = max(2, int(legs))
    chosen = picks_sorted[:legs]

    # rough combined EV proxy (NOT true parlay EV): multiply dec odds and compare to 1
    combined_decimal = 1.0
    for p in chosen:
        combined_decimal *= float(p.get("decimal", 1.0))
    return {
        "legs": legs,
        "combined_decimal": round(combined_decimal, 4),
        "picks": chosen,
    }