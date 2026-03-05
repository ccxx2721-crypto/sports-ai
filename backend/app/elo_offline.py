import pandas as pd

K = 20
HOME_ADV = 65

def expected(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

def update_elo(r1, r2, score1):

    e1 = expected(r1, r2)
    r1_new = r1 + K * (score1 - e1)
    r2_new = r2 + K * ((1-score1) - (1-e1))

    return r1_new, r2_new

def train_elo():

    df = pd.read_csv("data/nba_full_history.csv")
    ratings = {team:1500 for team in df.home_team.unique()}

    for _, row in df.iterrows():

        home = row.home_team
        away = row.away_team

        r_home = ratings[home] + HOME_ADV
        r_away = ratings[away]

        result = 1 if row.home_score > row.away_score else 0

        new_home, new_away = update_elo(r_home, r_away, result)

        ratings[home] = new_home - HOME_ADV
        ratings[away] = new_away

    return ratings