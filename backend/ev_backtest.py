import pandas as pd
import numpy as np

print("\n🚀 商業級 EV 引擎回測\n")

df = pd.read_csv("data/nba_master_clean.csv")

df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")

# ===== 這裡假設你有模型預測機率 =====
# 先用一個簡單 baseline（之後會換成真正模型）
df["model_home_prob"] = 0.5  # 暫時用 50% baseline

# ===== 市場賠率（先固定 -110）=====
decimal_odds = 1.91
payout = decimal_odds - 1

# ===== EV 計算 =====
df["ev"] = (
    df["model_home_prob"] * payout
    - (1 - df["model_home_prob"]) * 1
)

# 只下注 EV > 0
bets = df[df["ev"] > 0].copy()

print(f"總場數: {len(df)}")
print(f"下注場數: {len(bets)}")

# ===== 計算結果 =====
bets["home_margin"] = bets["home_score"] - bets["away_score"]
bets["home_result"] = bets["home_margin"] + bets["spread"]

bets["win"] = np.where(bets["home_result"] > 0, 1, 0)

profit = 0
for r in bets["win"]:
    if r == 1:
        profit += payout
    else:
        profit -= 1

if len(bets) > 0:
    roi = profit / len(bets)
else:
    roi = 0

print(f"ROI: {roi:.2%}")