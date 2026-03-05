from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import csv
import os

@dataclass
class GameHist:
    date: str
    sport: str
    away: str
    home: str
    away_score: float
    home_score: float
    spread_home: float
    total_close: float

def load_history_csv(path: str) -> List[GameHist]:
    if not os.path.exists(path):
        return []
    out: List[GameHist] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                out.append(GameHist(
                    date=r["date"],
                    sport=r["sport"].lower(),
                    away=r["away"],
                    home=r["home"],
                    away_score=float(r["away_score"]),
                    home_score=float(r["home_score"]),
                    spread_home=float(r["spread_home"]),
                    total_close=float(r["total_close"]),
                ))
            except Exception:
                continue
    return out

def cover_side(home_score: float, away_score: float, spread_home: float) -> str:
    # 主隊過盤：home_score + spread_home > away_score
    adj = home_score + spread_home
    if adj > away_score:
        return "HOME"
    if adj < away_score:
        return "AWAY"
    return "PUSH"

def total_side(home_score: float, away_score: float, total_line: float) -> str:
    total_pts = home_score + away_score
    if total_pts > total_line:
        return "O"
    if total_pts < total_line:
        return "U"
    return "PUSH"

def in_band(x: float, target: float, band: float) -> bool:
    return abs(x - target) <= band

def filter_similar_spread(rows: List[GameHist], sport: str, spread_home: float, band: float) -> List[GameHist]:
    sport = sport.lower()
    return [g for g in rows if g.sport == sport and in_band(g.spread_home, spread_home, band)]

def filter_similar_total(rows: List[GameHist], sport: str, total_line: float, band: float) -> List[GameHist]:
    sport = sport.lower()
    return [g for g in rows if g.sport == sport and in_band(g.total_close, total_line, band)]

def rate(win: int, total: int) -> float:
    return 0.0 if total <= 0 else win / total