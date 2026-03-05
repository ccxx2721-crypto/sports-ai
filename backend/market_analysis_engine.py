import requests
import os
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

def run_analysis(selected_date: str):

    today = date.today()
    selected = datetime.strptime(selected_date, "%Y-%m-%d").date()
    delta_days = (today - selected).days

    if delta_days < 0:
        delta_days = 0

    odds_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=spreads,totals&apiKey={API_KEY}"
    scores_url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?daysFrom={delta_days}&apiKey={API_KEY}"

    odds_data = requests.get(odds_url).json()
    scores_data = requests.get(scores_url).json()

    score_map = {}

    if isinstance(scores_data, list):
        for s in scores_data:
            if s.get("completed"):
                key = f"{s['away_team']}@{s['home_team']}"
                score_map[key] = {
                    "home_score": s["scores"][1]["score"],
                    "away_score": s["scores"][0]["score"]
                }

    results = []

    for game in odds_data:

        home = game["home_team"]
        away = game["away_team"]

        if not game.get("bookmakers"):
            continue

        bookmaker = game["bookmakers"][0]

        spread_line = None
        total_line = None
        result_status = None

        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for o in market["outcomes"]:
                    if o["name"] == home:
                        spread_line = o["point"]

            if market["key"] == "totals":
                for o in market["outcomes"]:
                    total_line = o["point"]

        match_key = f"{away}@{home}"

        if match_key in score_map and spread_line is not None:

            home_score = int(score_map[match_key]["home_score"])
            away_score = int(score_map[match_key]["away_score"])

            final_margin = home_score - away_score

            if final_margin > spread_line:
                result_status = "主隊過盤"
            elif final_margin < spread_line:
                result_status = "客隊過盤"
            else:
                result_status = "走盤"

            score_info = {
                "home_score": home_score,
                "away_score": away_score,
                "spread_result": result_status
            }
        else:
            score_info = None

        results.append({
            "match": f"{away} @ {home}",
            "spread": spread_line,
            "total": total_line,
            "score": score_info
        })

    return results