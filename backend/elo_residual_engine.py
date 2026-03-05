import pandas as pd
import numpy as np
from scipy.stats import norm
import math

print("\n🚀 Spread Residual Elo 引擎\n")

df = pd.read_csv("data/nba_master_clean.csv")
df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
df = df.sort_values("game_date")

# ===== 參數 =====
K = 20
HOME_ADV = 100
BASE = 1500

ELO_TO_MARGIN = 25
SIGMA = 12

DECIMAL_ODDS = 1.91
PAYOUT = DECIMAL_ODDS - 1

# Residual 觸發門檻（關鍵）
RESIDUAL_THRESHOLD = 2.0  # 2 分以上才下注

ratings = {}

def get_rating(team):
    if team not in ratings:
        ratings[team] = BASE
    return ratings[team]

def expected(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

profit = 0
bankroll = 100
history = [bankroll]
bets = 0

for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]

    r_home = get_rating(home)
    r_away = get_rating(away)

    r_home_adj = r_home + HOME_ADV
    elo_diff = r_home_adj - r_away

    # 模型預測分差
    mu = elo_diff / ELO_TO_MARGIN

    spread = row["spread"]

    # Residual（模型 - 市場）
    residual = mu - spread

    bet_side = None

    if residual > RESIDUAL_THRESHOLD:
        bet_side = "home"
    elif residual < -RESIDUAL_THRESHOLD:
        bet_side = "away"

    # ===== MOV 更新 Elo =====
    margin = row["home_score"] - row["away_score"]
    home_win = 1 if margin > 0 else 0

    exp = expected(r_home_adj, r_away)

    mov_multiplier = math.log(abs(margin) + 1) * (
        2.2 / ((elo_diff * 0.001) + 2.2)
    )

    r_home_new = r_home + K * mov_multiplier * (home_win - exp)
    r_away_new = r_away + K * mov_multiplier * ((1 - home_win) - (1 - exp))

    ratings[home] = r_home_new
    ratings[away] = r_away_new

    # ===== 下注 =====
    if bet_side is not None:
        bets += 1

        cover = (margin + spread) > 0

        if bet_side == "home":
            win = cover
        else:
            win = not cover

        if win:
            profit += PAYOUT
            bankroll += PAYOUT
        else:
            profit -= 1
            bankroll -= 1

        history.append(bankroll)

# ===== 結果 =====
roi = profit / bets if bets > 0 else 0

print(f"總下注場數: {bets}")
print(f"ROI: {roi:.2%}")
print(f"最終資金: {bankroll:.2f}")

peak = history[0]
max_dd = 0
for v in history:
    if v > peak:
        peak = v
    dd = (peak - v) / peak
    if dd > max_dd:
        max_dd = dd

print(f"最大回撤: {max_dd:.2%}")