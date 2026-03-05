import pandas as pd

spread = pd.read_csv("data/nba_betting_spread.csv")
games = pd.read_csv("data/nba_master_clean.csv")

games["game_date"] = pd.to_datetime(games["game_date"], errors="coerce")

merged = games.merge(spread[["game_id"]].drop_duplicates(), on="game_id", how="inner")

print("spread最早日期:", merged["game_date"].min())
print("spread最晚日期:", merged["game_date"].max())
print("spread總場數:", len(merged))