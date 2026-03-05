import pandas as pd
import numpy as np
from math import sqrt
from .elo_offline import expected, update_elo

# ===== 參數區 =====
K = 20
HOME_ADV = 65
INITIAL_BANKROLL = 10000
MAX_KELLY = 0.03
EDGE_THRESHOLD = 0.02   # 至少 2% edge 才下注
MODEL_EDGE = 0.002    # 模型優勢測試 (1%)

def kelly_fraction(p, odds):
    k = (p * (odds - 1) - (1 - p)) / (odds - 1)
    return max(k, 0)

def backtest():

    print("🚀 EV 5.0 backtest running")

    df = pd.read_csv("data/nba_full_history.csv")

    ratings = {team: 1500 for team in df.home_team.unique()}

    bankroll = INITIAL_BANKROLL
    peak = bankroll
    returns = []

    total_bets = 0
    wins = 0

    for _, row in df.iterrows():

        home = row.home_team
        away = row.away_team

        r_home = ratings[home] + HOME_ADV
        r_away = ratings[away]

        # ===== 模型機率 =====
        prob_home = expected(r_home, r_away)
        prob_away = 1 - prob_home

        # 加入模型 alpha（測試）
        prob_home = min(max(prob_home + MODEL_EDGE, 0.01), 0.99)
        prob_away = 1 - prob_home

        # ===== 模擬市場 =====
        market_prob_home = prob_home * np.random.uniform(0.97, 1.03)
        market_prob_home = min(max(market_prob_home, 0.05), 0.95)
        market_prob_away = 1 - market_prob_home

        odds_home = 1 / market_prob_home
        odds_away = 1 / market_prob_away

        ev_home = prob_home * odds_home - 1
        ev_away = prob_away * odds_away - 1

        # ===== 選最大 EV =====
        if ev_home > ev_away:
            selected_prob = prob_home
            selected_odds = odds_home
            selected_ev = ev_home
            result = 1 if row.home_score > row.away_score else 0
        else:
            selected_prob = prob_away
            selected_odds = odds_away
            selected_ev = ev_away
            result = 1 if row.home_score < row.away_score else 0

        # ===== Edge 濾網 =====
        if selected_ev > EDGE_THRESHOLD:

            k = kelly_fraction(selected_prob, selected_odds)
            k = min(k, MAX_KELLY)

            stake = bankroll * k
            prev_bankroll = bankroll

            if result == 1:
                bankroll += stake * (selected_odds - 1)
                wins += 1
            else:
                bankroll -= stake

            returns.append((bankroll - prev_bankroll) / prev_bankroll)
            peak = max(peak, bankroll)
            total_bets += 1

        # ===== 更新 Elo =====
        result_home = 1 if row.home_score > row.away_score else 0
        new_home, new_away = update_elo(r_home, r_away, result_home)

        ratings[home] = new_home - HOME_ADV
        ratings[away] = new_away

    roi = (bankroll - INITIAL_BANKROLL) / INITIAL_BANKROLL * 100
    win_rate = wins / total_bets if total_bets else 0
    max_drawdown = (peak - bankroll) / peak * 100

    if len(returns) > 1:
        sharpe = np.mean(returns) / np.std(returns) * sqrt(252)
    else:
        sharpe = 0

    return {
        "final_bankroll": round(bankroll, 2),
        "ROI_%": round(roi, 2),
        "total_bets": total_bets,
        "win_rate": round(win_rate, 3),
        "max_drawdown_%": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe, 2)
    }