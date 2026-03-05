import pandas as pd

df = pd.read_csv("data/nba_master_clean.csv")
df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")

print("最早日期:", df["game_date"].min())
print("最晚日期:", df["game_date"].max())
print("總場數:", len(df))