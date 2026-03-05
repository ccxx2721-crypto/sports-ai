import pandas as pd


def validate_market(csv_path):
    df = pd.read_csv(csv_path)

    print("欄位名稱：")
    print(df.columns)
    print("-" * 50)

    total_games = 0
    home_cover = 0
    away_cover = 0
    push = 0

    bankroll = 0
    bet_size = 100
    win_return = 90.91  # -110 回報

    for _, row in df.iterrows():

        # ⚠ 如果欄位名稱不同，這三個要改
        home_score = row["home_score"]
        away_score = row["away_score"]
        spread = row["home_spread"]  # 必須是主隊視角

        diff = home_score - away_score

        total_games += 1

        if diff > spread:
            home_cover += 1
            bankroll += win_return
        elif diff < spread:
            away_cover += 1
            bankroll -= bet_size
        else:
            push += 1

    print("\n==== 市場驗證結果 ====")
    print(f"總場數: {total_games}")
    print(f"主隊 Cover: {home_cover} ({home_cover/total_games:.2%})")
    print(f"客隊 Cover: {away_cover} ({away_cover/total_games:.2%})")
    print(f"Push: {push} ({push/total_games:.2%})")

    roi = bankroll / (total_games * bet_size)
    print("\n==== 模擬每場都下主隊 ROI ====")
    print(f"ROI: {roi:.2%}")
    print("正常市場應該約 -4% ~ -6%")


if __name__ == "__main__":
    validate_market("data/nba_games_all.csv")