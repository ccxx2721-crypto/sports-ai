import sqlite3

conn = sqlite3.connect("ratings.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS odds_today (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    home_team TEXT,
    away_team TEXT,
    home_ml REAL,
    away_ml REAL,
    timestamp TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    home_team TEXT,
    away_team TEXT,
    market_prob REAL,
    model_prob REAL,
    edge REAL,
    predicted_home_score REAL,
    predicted_away_score REAL,
    recommendation TEXT,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("資料庫初始化完成")