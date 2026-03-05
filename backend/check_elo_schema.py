import sqlite3

conn = sqlite3.connect("elo_ratings.db")
c = conn.cursor()

print(c.execute("PRAGMA table_info(team_ratings)").fetchall())