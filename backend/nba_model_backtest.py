import pandas as pd
import numpy as np

print("\n🚀 NBA 市場基準驗證\n")

df = pd.read_csv("data/nba_master_clean.csv")

df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")

df["home_margin"] = df["home_score"] - df["away_score"]
df["home_result"] = df["home_margin"] + df["spread"]

df["home_cover"] = np.where(df["home_result"] > 0, 1, 0)
df["away_cover"] = np.where(df["home_result"] < 0, 1, 0)
df["push"] = np.where(df["home_result"] == 0, 1, 0)

df = df[df["push"] == 0]

START_YEAR = 2009
END_YEAR = 2018

df = df[
    (df["game_date"].dt.year >= START_YEAR) &
    (df["game_date"].dt.year <= END_YEAR)
]

print(f"樣本數: {len(df)}")

print("\n==== ATS 結構 ====")
print(f"主隊 Cover: {df['home_cover'].mean():.2%}")
print(f"客隊 Cover: {df['away_cover'].mean():.2%}")

odds = 1.91
profit = 0

for r in df["home_cover"]:
    if r == 1:
        profit += (odds - 1)
    else:
        profit -= 1

roi = profit / len(df)

print("\n==== 每場押主隊 ROI ====")
print(f"ROI: {roi:.2%}")
print("正常市場應該約 -4% ~ -6%")