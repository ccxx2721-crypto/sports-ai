import itertools


def calculate_stakes(odds_list, total_stake=1000):
    inv_sum = sum(1 / o for o in odds_list)
    stakes = [(total_stake * (1 / o) / inv_sum) for o in odds_list]
    guaranteed_profit = total_stake - sum(stakes)

    return {
        "stakes": [round(s, 2) for s in stakes],
        "guaranteed_profit": round(guaranteed_profit, 2)
    }


def find_two_way_arbitrage(match_data):

    opportunities = []
    books = match_data["books"]
    match_name = match_data["match"]

    for book_home, book_away in itertools.permutations(books, 2):

        home_odds = book_home["home"]
        away_odds = book_away["away"]

        arb_value = (1 / home_odds) + (1 / away_odds)

        if arb_value < 1:

            profit_percent = (1 - arb_value) * 100
            stake_info = calculate_stakes([home_odds, away_odds])

            opportunities.append({
                "type": "two_way",
                "match": match_name,
                "home_book": book_home["book"],
                "away_book": book_away["book"],
                "profit_%": round(profit_percent, 2),
                "bet_distribution": {
                    "home_stake": stake_info["stakes"][0],
                    "away_stake": stake_info["stakes"][1],
                    "guaranteed_profit": stake_info["guaranteed_profit"]
                }
            })

    return opportunities


def scan_arbitrage(matches):

    all_opportunities = []

    for match in matches:
        all_opportunities.extend(find_two_way_arbitrage(match))

    return all_opportunities