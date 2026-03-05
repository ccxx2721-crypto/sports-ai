import pandas as pd
import sqlite3
import math

print("🚀 建立真 Elo Rating")

# 讀歷史資料
df = pd.read_csv("data/nba_master_clean.csv")

df["game_date"] = pd.to_datetime(df["game_date"])
df = df.sort_values("game_date")

# 參數
BASE_RATING = 1500
K = 20

# Elo 計算函數
def expected_score(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

# 建立 rating dict
ratings = {}

for _, row in df.iterrows():

    home = row["home_team"]
    away = row["away_team"]
    home_score = row["home_score"]
    away_score = row["away_score"]

    if pd.isna(home_score) or pd.isna(away_score):
        continue

    if home not in ratings:
        ratings[home] = BASE_RATING
    if away not in ratings:
        ratings[away] = BASE_RATING

    r_home = ratings[home]
    r_away = ratings[away]

    exp_home = expected_score(r_home, r_away)

    if home_score > away_score:
        score_home = 1
    else:
        score_home = 0

    new_home = r_home + K * (score_home - exp_home)
    new_away = r_away + K * ((1 - score_home) - (1 - exp_home))

    ratings[home] = new_home
    ratings[away] = new_away

print("✅ Elo 計算完成")

# 存入 SQLite
conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS team_ratings (
    team_name TEXT PRIMARY KEY,
    rating REAL
)
""")

c.execute("DELETE FROM team_ratings")

for team, rating in ratings.items():
    c.execute("INSERT INTO team_ratings VALUES (?, ?)", (team, rating))

conn.commit()
conn.close()

print("✅ Elo 已寫入 elo_ratings.db")