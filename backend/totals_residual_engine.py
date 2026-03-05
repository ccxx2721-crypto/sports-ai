import pandas as pd
import numpy as np

print("\n🚀 Totals Residual Model\n")

games = pd.read_csv("data/nba_master_clean.csv")
totals = pd.read_csv("data/nba_betting_totals.csv")

games["game_date"] = pd.to_datetime(games["game_date"], errors="coerce")

# 只取 Pinnacle
totals = totals[totals["book_name"].str.contains("Pinnacle", na=False)]
totals = totals.groupby("game_id").first().reset_index()

totals["market_total"] = totals["total1"]

df = games.merge(totals[["game_id", "market_total"]], on="game_id", how="inner")

# ===============================
# 建立簡單歷史移動平均模型
# ===============================

df = df.sort_values("game_date")

team_history = {}

predicted_totals = []

WINDOW = 10  # 最近10場

for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]

    if home not in team_history:
        team_history[home] = []
    if away not in team_history:
        team_history[away] = []

    # 預測
    if len(team_history[home]) >= WINDOW:
        home_avg = np.mean(team_history[home][-WINDOW:])
    else:
        home_avg = np.mean(team_history[home]) if team_history[home] else 110

    if len(team_history[away]) >= WINDOW:
        away_avg = np.mean(team_history[away][-WINDOW:])
    else:
        away_avg = np.mean(team_history[away]) if team_history[away] else 110

    predicted_total = home_avg + away_avg
    predicted_totals.append(predicted_total)

    # 更新歷史
    actual_total = row["home_score"] + row["away_score"]
    team_history[home].append(actual_total / 2)
    team_history[away].append(actual_total / 2)

df["model_total"] = predicted_totals

# ===============================
# Residual
# ===============================

df["residual"] = df["model_total"] - df["market_total"]

THRESHOLD = 5  # 差5分才下注

df["bet_side"] = np.where(df["residual"] > THRESHOLD, "over",
                   np.where(df["residual"] < -THRESHOLD, "under", None))

df = df[df["bet_side"].notna()]

print(f"總下注場數: {len(df)}")

# ===============================
# 計算結果
# ===============================

PAYOUT = 0.91
profit = 0

for _, row in df.iterrows():

    actual_total = row["home_score"] + row["away_score"]

    if row["bet_side"] == "over":
        win = actual_total > row["market_total"]
    else:
        win = actual_total < row["market_total"]

    if win:
        profit += PAYOUT
    else:
        profit -= 1

roi = profit / len(df) if len(df) > 0 else 0

print(f"ROI: {roi:.2%}")