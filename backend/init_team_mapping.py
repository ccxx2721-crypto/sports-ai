import sqlite3

print("🚀 建立 Team Mapping 資料庫")

conn = sqlite3.connect("team_mapping.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS team_map (
    api_name TEXT PRIMARY KEY,
    elo_name TEXT
)
""")

# NBA 標準對應表（完整版）
mapping_data = [
    ("Los Angeles Lakers", "Los Angeles Lakers"),
    ("LA Lakers", "Los Angeles Lakers"),
    ("Golden State Warriors", "Golden State Warriors"),
    ("GS Warriors", "Golden State Warriors"),
    ("Boston Celtics", "Boston Celtics"),
    ("Chicago Bulls", "Chicago Bulls"),
    ("Miami Heat", "Miami Heat"),
    ("Denver Nuggets", "Denver Nuggets"),
    ("Phoenix Suns", "Phoenix Suns"),
    ("Minnesota Timberwolves", "Minnesota Timberwolves"),
    ("Toronto Raptors", "Toronto Raptors"),
    ("Brooklyn Nets", "Brooklyn Nets"),
    ("New Orleans Pelicans", "New Orleans Pelicans"),
    ("Sacramento Kings", "Sacramento Kings"),
    ("Detroit Pistons", "Detroit Pistons"),
    ("San Antonio Spurs", "San Antonio Spurs"),
    ("Dallas Mavericks", "Dallas Mavericks"),
    ("Orlando Magic", "Orlando Magic"),
    ("Utah Jazz", "Utah Jazz"),
    ("Washington Wizards", "Washington Wizards"),
    ("Houston Rockets", "Houston Rockets"),
    ("Cleveland Cavaliers", "Cleveland Cavaliers"),
    ("Philadelphia 76ers", "Philadelphia 76ers"),
    ("Milwaukee Bucks", "Milwaukee Bucks"),
    ("Atlanta Hawks", "Atlanta Hawks"),
    ("Indiana Pacers", "Indiana Pacers"),
    ("Charlotte Hornets", "Charlotte Hornets"),
    ("Memphis Grizzlies", "Memphis Grizzlies"),
    ("New York Knicks", "New York Knicks"),
    ("Oklahoma City Thunder", "Oklahoma City Thunder"),
    ("Portland Trail Blazers", "Portland Trail Blazers")
]

c.executemany("INSERT OR REPLACE INTO team_map VALUES (?, ?)", mapping_data)

conn.commit()
conn.close()

print("✅ Team Mapping 建立完成")