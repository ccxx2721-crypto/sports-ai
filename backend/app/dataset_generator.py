import random
import csv
import os
from datetime import datetime, timedelta

TEAMS = [
    "Celtics","Bucks","Nuggets","Warriors","Lakers","Heat","Suns","Clippers",
    "76ers","Knicks","Timberwolves","Mavericks","Kings","Cavaliers","Grizzlies",
    "Pelicans","Raptors","Hawks","Bulls","Jazz","Spurs","Pistons","Hornets",
    "Magic","Wizards","Trail Blazers","Pacers","Rockets","Thunder","Nets"
]

os.makedirs("data", exist_ok=True)

def generate_dataset(seasons=5):

    file_path = "data/nba_full_history.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerow(["date","home_team","away_team","home_score","away_score"])

        base_date = datetime(2019, 10, 1)

        for season in range(seasons):

            season_date = base_date + timedelta(days=365*season)

            for game_id in range(1230):

                home, away = random.sample(TEAMS, 2)

                home_strength = random.gauss(1500, 120)
                away_strength = random.gauss(1500, 120)

                home_score = int(random.gauss(110 + (home_strength-away_strength)/40, 12))
                away_score = int(random.gauss(110 - (home_strength-away_strength)/40, 12))

                writer.writerow([
                    (season_date + timedelta(days=game_id)).strftime("%Y-%m-%d"),
                    home,
                    away,
                    max(home_score, 80),
                    max(away_score, 80)
                ])

    print("資料生成完成")

if __name__ == "__main__":
    generate_dataset(5)