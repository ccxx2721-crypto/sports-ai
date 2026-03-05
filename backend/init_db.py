import sqlite3


def init_database():
    conn = sqlite3.connect("ratings.db")
    c = conn.cursor()

    # ----------------------------
    # 今日盤口資料表
    # ----------------------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS odds_today (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT,
        home_team TEXT,
        away_team TEXT,
        home_ml REAL,
        away_ml REAL,
        home_spread REAL,
        total_line REAL,
        timestamp TEXT
    )
    """)

    # ----------------------------
    # （可選）Elo 評分表
    # ----------------------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS team_elo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT UNIQUE,
        elo_rating REAL DEFAULT 1500
    )
    """)

    conn.commit()
    conn.close()

    print("✅ 資料庫初始化完成（odds_today + team_elo）")


if __name__ == "__main__":
    init_database()