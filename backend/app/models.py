from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    game_date = Column(String)

class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    team = Column(String)
    odds = Column(Integer)
    stake = Column(Float)
    result = Column(String)
    profit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    bankroll = Column(Float)
    roi = Column(Float)