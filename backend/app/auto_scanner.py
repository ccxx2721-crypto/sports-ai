import asyncio
from .live_odds_service import fetch_live_odds, normalize_odds
from .arbitrage_engine import scan_arbitrage
from .telegram_service import send_telegram_message

last_sent = set()

async def auto_scan():
    while True:
        try:
            odds = fetch_live_odds()

            if odds:
                normalized = normalize_odds(odds)
                opportunities = scan_arbitrage(normalized)

                # 如果是 list 才處理
                if isinstance(opportunities, list) and len(opportunities) > 0:

                    for opp in opportunities:

                        key = f"{opp.get('match','')}_{opp.get('home_book','')}_{opp.get('away_book','')}"

                        if key not in last_sent:

                            msg = (
                                f"🔥 套利機會\n"
                                f"比賽: {opp.get('match')}\n"
                                f"利潤: {opp.get('profit_%')}%\n"
                                f"主莊: {opp.get('home_book')}\n"
                                f"客莊: {opp.get('away_book')}"
                            )

                            send_telegram_message(msg)
                            last_sent.add(key)

            await asyncio.sleep(10)

        except Exception as e:
            print("Auto Scan Error:", e)
            await asyncio.sleep(10)