import pandas as pd
import numpy as np

print("\n🚀 Bookmaker Disagreement 穩定性分析\n")

spread = pd.read_csv("data/nba_betting_spread.csv")
games = pd.read_csv("data/nba_master_clean.csv")

games["game_date"] = pd.to_datetime(games["game_date"], errors="coerce")

# 只用主隊 spread
spread["spread"] = spread["spread1"]

# 市場統計
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
market["diff"] = market["pin_spread"] - market["mean"]

df = games.merge(market, on="game_id", how="inner")

df["margin"] = df["home_score"] - df["away_score"]
df["cover"] = (df["margin"] + df["spread"]) > 0

PAYOUT = 0.91

# ====================================================
# A️⃣ Threshold 全區間測試
# ====================================================
print("\n===== Threshold 敏感度測試 =====\n")

thresholds = np.arange(0.5, 3.5, 0.5)

for t in thresholds:

    temp = df.copy()

    temp["bet_side"] = np.where(temp["diff"] > t, "home",
                         np.where(temp["diff"] < -t, "away", None))

    temp = temp[temp["bet_side"].notna()]

    if len(temp) == 0:
        continue

    profit = 0

    for _, row in temp.iterrows():
        if row["bet_side"] == "home":
            win = row["cover"]
        else:
            win = not row["cover"]

        if win:
            profit += PAYOUT
        else:
            profit -= 1

    roi = profit / len(temp)

    print(f"Threshold {t:.1f} | 場數: {len(temp)} | ROI: {roi:.2%}")

# ====================================================
# B️⃣ 分年度穩定性測試（用 1.5 為基準）
# ====================================================
print("\n===== 分年度 ROI 測試 (Threshold=1.5) =====\n")

BASE_THRESHOLD = 1.5

df["bet_side"] = np.where(df["diff"] > BASE_THRESHOLD, "home",
                   np.where(df["diff"] < -BASE_THRESHOLD, "away", None))

df_year = df[df["bet_side"].notna()].copy()

years = sorted(df_year["game_date"].dt.year.dropna().unique())

for y in years:

    temp = df_year[df_year["game_date"].dt.year == y]

    if len(temp) < 10:
        continue

    profit = 0

    for _, row in temp.iterrows():
        if row["bet_side"] == "home":
            win = row["cover"]
        else:
            win = not row["cover"]

        if win:
            profit += PAYOUT
        else:
            profit -= 1

    roi = profit / len(temp)

    print(f"{y} 年 | 場數: {len(temp)} | ROI: {roi:.2%}")