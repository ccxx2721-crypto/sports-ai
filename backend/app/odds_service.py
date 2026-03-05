from .odds_theodds import fetch_odds


async def fetch_odds_for_games(sport: str):
    """
    專門給 /games API 用
    不寫入資料庫
    只抓即時盤口
    """
    return await fetch_odds(f"basketball_{sport}")