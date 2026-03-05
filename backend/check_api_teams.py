# check_api_teams.py
import sqlite3
conn = sqlite3.connect("ratings.db")
c = conn.cursor()
print(c.execute("SELECT DISTINCT home_team FROM odds_today").fetchall())