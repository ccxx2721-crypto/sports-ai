import pandas as pd
import numpy as np

print("\n🚀 Bookmaker Disagreement 引擎\n")

spread = pd.read_csv("data/nba_betting_spread.csv")
games = pd.read_csv("data/nba_master_clean.csv")

# 只用主隊那一列（spread1）
spread["spread"] = spread["spread1"]

# ===== 計算每場市場平均與標準差 =====
market_stats = (
    spread.groupby("game_id")["spread"]
    .agg(["mean", "std"])
    .reset_index()
)

# 找 Pinnacle
pin = spread[spread["book_name"].str.contains("Pinnacle", na=False)]
pin = pin[["game_id", "spread"]]
pin.rename(columns={"spread": "pin_spread"}, inplace=True)

# 合併
market = market_stats.merge(pin, on="game_id", how="left")

# 計算 Pinnacle 與市場差距
market["diff"] = market["pin_spread"] - market["mean"]

# ===== 合併比賽結果 =====
df = games.merge(market, on="game_id", how="inner")

# ===== 只打差距大的 =====
THRESHOLD = 1.5

df["bet_side"] = np.where(df["diff"] > THRESHOLD, "home",
                   np.where(df["diff"] < -THRESHOLD, "away", None))

df = df[df["bet_side"].notna()]

print(f"總下注場數: {len(df)}")

# ===== 計算結果 =====
df["margin"] = df["home_score"] - df["away_score"]
df["cover"] = (df["margin"] + df["spread"]) > 0

profit = 0
PAYOUT = 0.91

for _, row in df.iterrows():
    if row["bet_side"] == "home":
        win = row["cover"]
    else:
        win = not row["cover"]

    if win:
        profit += PAYOUT
    else:
        profit -= 1

roi = profit / len(df) if len(df) > 0 else 0

print(f"ROI: {roi:.2%}")