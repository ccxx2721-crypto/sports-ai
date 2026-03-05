import pandas as pd

# 讀取資料
games = pd.read_csv("data/nba_games_all.csv")
spread = pd.read_csv("data/nba_betting_spread.csv")
totals = pd.read_csv("data/nba_betting_totals.csv")
ml = pd.read_csv("data/nba_betting_money_line.csv")

# ===== 1️⃣ 整理 games =====
home = games[games["is_home"] == "t"].copy()
away = games[games["is_home"] == "f"].copy()

master = home.merge(
    away,
    on="game_id",
    suffixes=("_home", "_away")
)

master["home_score"] = master["pts_home"]
master["away_score"] = master["pts_away"]
master["home_win"] = (master["home_score"] > master["away_score"]).astype(int)

master = master[[
    "game_id",
    "game_date_home",
    "team_id_home",
    "team_id_away",
    "home_score",
    "away_score",
    "home_win"
]]

master.rename(columns={
    "game_date_home": "game_date",
    "team_id_home": "home_team",
    "team_id_away": "away_team"
}, inplace=True)

# ===== 2️⃣ 合併 Spread（正確版） =====
spread = spread[spread["book_name"].str.contains("Pinnacle", na=False)]
spread = spread.groupby("game_id").first().reset_index()

master = master.merge(
    spread[["game_id", "team_id", "a_team_id", "spread1", "spread2"]],
    on="game_id",
    how="left"
)

# 🔥 核心：正確生成 home_spread
def get_home_spread(row):
    if row["team_id"] == row["home_team"]:
        return row["spread1"]
    elif row["a_team_id"] == row["home_team"]:
        return row["spread2"]
    else:
        return None

master["spread"] = master.apply(get_home_spread, axis=1)

# ===== 3️⃣ 合併 Totals =====
totals = totals[totals["book_name"].str.contains("Pinnacle", na=False)]
totals = totals.groupby("game_id").first().reset_index()

master = master.merge(
    totals[["game_id", "total1"]],
    on="game_id",
    how="left"
)

master["total"] = master["total1"]

# ===== 4️⃣ 合併 Moneyline =====
ml = ml[ml["book_name"].str.contains("Pinnacle", na=False)]
ml = ml.groupby("game_id").first().reset_index()

master = master.merge(
    ml[["game_id", "price1"]],
    on="game_id",
    how="left"
)

master["moneyline_home"] = master["price1"]

# 存檔
master.to_csv("data/nba_master_clean.csv", index=False)

print("✅ NBA Master Dataset 正規修正完成")