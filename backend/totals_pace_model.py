import pandas as pd
import numpy as np

print("\n🚀 Pace-Based Totals Model\n")

games_raw = pd.read_csv("data/nba_games_all.csv")
totals = pd.read_csv("data/nba_betting_totals.csv")

games_raw["game_date"] = pd.to_datetime(games_raw["game_date"], errors="coerce")

# 只取 Regular Season
games_raw = games_raw[games_raw["season_type"] == "Regular Season"]

# ===== 計算 Possessions =====
games_raw["poss"] = (
    games_raw["fga"] +
    0.44 * games_raw["fta"] -
    games_raw["oreb"] +
    games_raw["tov"]
)

# 分主客
home = games_raw[games_raw["is_home"] == "t"].copy()
away = games_raw[games_raw["is_home"] == "f"].copy()

merged = home.merge(
    away,
    on="game_id",
    suffixes=("_home", "_away")
)

# ===== 計算 Pace & OffEff =====
merged["pace"] = (
    merged["poss_home"] + merged["poss_away"]
) / 2

merged["off_eff_home"] = merged["pts_home"] / merged["poss_home"]
merged["off_eff_away"] = merged["pts_away"] / merged["poss_away"]

merged["total_points"] = merged["pts_home"] + merged["pts_away"]

# ===== 合併市場 Totals =====
totals = totals[totals["book_name"].str.contains("Pinnacle", na=False)]
totals = totals.groupby("game_id").first().reset_index()
totals["market_total"] = totals["total1"]

df = merged.merge(
    totals[["game_id", "market_total"]],
    on="game_id",
    how="inner"
)

df = df.sort_values("game_date_home")

# ===== 建立移動平均 Pace + OffEff =====
WINDOW = 10

team_history = {}

predicted_totals = []

for _, row in df.iterrows():

    home_team = row["team_id_home"]
    away_team = row["team_id_away"]

    if home_team not in team_history:
        team_history[home_team] = {"pace": [], "off": []}
    if away_team not in team_history:
        team_history[away_team] = {"pace": [], "off": []}

    # 預測
    def get_avg(team, key):
        if len(team_history[team][key]) >= WINDOW:
            return np.mean(team_history[team][key][-WINDOW:])
        elif len(team_history[team][key]) > 0:
            return np.mean(team_history[team][key])
        else:
            return np.mean(df["pace"])

    home_pace = get_avg(home_team, "pace")
    away_pace = get_avg(away_team, "pace")

    home_off = get_avg(home_team, "off")
    away_off = get_avg(away_team, "off")

    expected_pace = (home_pace + away_pace) / 2
    expected_total = expected_pace * (home_off + away_off)

    predicted_totals.append(expected_total)

    # 更新歷史
    team_history[home_team]["pace"].append(row["pace"])
    team_history[away_team]["pace"].append(row["pace"])

    team_history[home_team]["off"].append(row["off_eff_home"])
    team_history[away_team]["off"].append(row["off_eff_away"])

df["model_total"] = predicted_totals

# ===== Residual Strategy =====
df["residual"] = df["model_total"] - df["market_total"]

THRESHOLD = 4

df["bet_side"] = np.where(
    df["residual"] > THRESHOLD, "over",
    np.where(df["residual"] < -THRESHOLD, "under", None)
)

df = df[df["bet_side"].notna()]

print(f"總下注場數: {len(df)}")

# ===== 回測 =====
PAYOUT = 0.91
profit = 0

for _, row in df.iterrows():

    if row["bet_side"] == "over":
        win = row["total_points"] > row["market_total"]
    else:
        win = row["total_points"] < row["market_total"]

    if win:
        profit += PAYOUT
    else:
        profit -= 1

roi = profit / len(df) if len(df) > 0 else 0

print(f"ROI: {roi:.2%}")