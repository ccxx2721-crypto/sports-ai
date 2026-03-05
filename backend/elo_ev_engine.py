import pandas as pd
import numpy as np

print("\n🚀 NBA Elo + EV 商業引擎\n")

# ==============================
# 讀取資料
# ==============================
df = pd.read_csv("data/nba_master_clean.csv")
df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
df = df.sort_values("game_date")

# ==============================
# Elo 參數
# ==============================
K = 20
HOME_ADVANTAGE = 100
BASE_RATING = 1500

# 建立 rating 字典
ratings = {}

def get_rating(team):
    if team not in ratings:
        ratings[team] = BASE_RATING
    return ratings[team]

def expected_score(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

# 儲存模型機率
model_probs = []

# ==============================
# 逐場更新 Elo
# ==============================
for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]

    r_home = get_rating(home)
    r_away = get_rating(away)

    # 主場加成
    r_home_adj = r_home + HOME_ADVANTAGE

    # 預測主勝機率
    p_home = expected_score(r_home_adj, r_away)
    model_probs.append(p_home)

    # 實際結果
    home_win = 1 if row["home_score"] > row["away_score"] else 0

    # 更新 rating
    r_home_new = r_home + K * (home_win - p_home)
    r_away_new = r_away + K * ((1 - home_win) - (1 - p_home))

    ratings[home] = r_home_new
    ratings[away] = r_away_new

df["model_home_prob"] = model_probs

# ==============================
# EV 計算
# ==============================

DECIMAL_ODDS = 1.91
PAYOUT = DECIMAL_ODDS - 1

df["ev"] = (
    df["model_home_prob"] * PAYOUT
    - (1 - df["model_home_prob"]) * 1
)

# 只下注 EV > 0
bets = df[df["ev"] > 0].copy()

print(f"總場數: {len(df)}")
print(f"EV > 0 場數: {len(bets)}")

# ==============================
# 計算 ATS 結果
# ==============================

bets["home_margin"] = bets["home_score"] - bets["away_score"]
bets["home_result"] = bets["home_margin"] + bets["spread"]
bets["win"] = np.where(bets["home_result"] > 0, 1, 0)

profit = 0
bankroll = 100
history = [bankroll]

for r in bets["win"]:
    if r == 1:
        profit += PAYOUT
        bankroll += PAYOUT
    else:
        profit -= 1
        bankroll -= 1
    history.append(bankroll)

if len(bets) > 0:
    roi = profit / len(bets)
else:
    roi = 0

print("\n==== Elo EV 回測結果 ====")
print(f"ROI: {roi:.2%}")
print(f"最終資金: {bankroll:.2f}")

# 最大回撤
peak = history[0]
max_dd = 0
for v in history:
    if v > peak:
        peak = v
    dd = (peak - v) / peak
    if dd > max_dd:
        max_dd = dd

print(f"最大回撤: {max_dd:.2%}")