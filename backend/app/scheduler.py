from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .odds_service import update_odds_to_db

scheduler = AsyncIOScheduler()

async def daily_job():
    await update_odds_to_db("basketball_nba")
    await update_odds_to_db("baseball_mlb")

def start_scheduler():
    scheduler.add_job(daily_job, "interval", hours=24)
    scheduler.start()