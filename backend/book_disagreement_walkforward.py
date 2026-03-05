import pandas as pd
import numpy as np

print("\n🚀 Bookmaker Disagreement Walk-Forward 測試\n")

spread = pd.read_csv("data/nba_betting_spread.csv")
games = pd.read_csv("data/nba_master_clean.csv")

games["game_date"] = pd.to_datetime(games["game_date"], errors="coerce")

spread["spread"] = spread["spread1"]

market_stats = (
    spread.groupby("game_id")["spread"]
    .agg(["mean", "std"])
    .reset_index()
)

pin = spread[spread["book_name"].str.contains("Pinnacle", na=False)]
pin = pin[["game_id", "spread"]]
pin.rename(columns={"spread": "pin_spread"}, inplace=True)

market = market_stats.merge(pin, on="game_id", how="left")
market["diff"] = market["pin_spread"] - market["mean"]

df = games.merge(market, on="game_id", how="inner")

df["margin"] = df["home_score"] - df["away_score"]
df["cover"] = (df["margin"] + df["spread"]) > 0

PAYOUT = 0.91
THRESHOLD = 1.5

# ===== 切分 =====
train = df[df["game_date"].dt.year <= 2012]
test = df[df["game_date"].dt.year >= 2013]

print("訓練場數:", len(train))
print("測試場數:", len(test))

def backtest(data):

    temp = data.copy()

    temp["bet_side"] = np.where(temp["diff"] > THRESHOLD, "home",
                         np.where(temp["diff"] < -THRESHOLD, "away", None))

    temp = temp[temp["bet_side"].notna()]

    if len(temp) == 0:
        return 0, 0

    profit = 0

    for _, row in temp.iterrows():
        if row["bet_side"] == "home":
            win = row["cover"]
        else:
            win = not row["cover"]

        if win:
            profit += PAYOUT
        else:
            profit -= 1

    roi = profit / len(temp)

    return len(temp), roi

train_n, train_roi = backtest(train)
test_n, test_roi = backtest(test)

print("\n===== Walk-Forward 結果 =====")
print(f"Train | 場數: {train_n} | ROI: {train_roi:.2%}")
print(f"Test  | 場數: {test_n} | ROI: {test_roi:.2%}")