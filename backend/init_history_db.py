import sqlite3

conn = sqlite3.connect("history.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_date TEXT,
    away_team TEXT,
    home_team TEXT,
    spread REAL,
    total REAL,
    home_score INTEGER,
    away_score INTEGER
)
""")

conn.commit()
conn.close()

print("✅ 歷史資料庫建立完成")