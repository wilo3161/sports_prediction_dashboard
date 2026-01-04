from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Float, default=1000.0)  # Saldo virtual
    daily_limit = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    
    bets = relationship("Bet", back_populates="user")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    api_match_id = Column(String(50), unique=True)
    league = Column(String(50))
    competition = Column(String(50))
    date = Column(DateTime)
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String(20))  # scheduled, live, finished
    odds = Column(JSON)  # { "1": 2.10, "X": 3.40, "2": 3.50 }
    
    stats = relationship("MatchStats", back_populates="match", uselist=False)
    bets = relationship("Bet", back_populates="match")

class MatchStats(Base):
    __tablename__ = 'match_stats'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'))
    home_possession = Column(Float)
    away_possession = Column(Float)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    home_fouls = Column(Integer)
    away_fouls = Column(Integer)
    home_yellow_cards = Column(Integer)
    away_yellow_cards = Column(Integer)
    home_red_cards = Column(Integer)
    away_red_cards = Column(Integer)
    home_xg = Column(Float)  # Expected goals
    away_xg = Column(Float)
    
    match = relationship("Match", back_populates="stats")

class Bet(Base):
    __tablename__ = 'bets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    match_id = Column(Integer, ForeignKey('matches.id'))
    bet_type = Column(String(50))
    selection = Column(String(100))  # "1", "X", "2", "Over 2.5", etc.
    odds = Column(Float)
    stake = Column(Float)
    potential_win = Column(Float)
    status = Column(String(20), default="pending")  # pending, won, lost
    placed_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    
    user = relationship("User", back_populates="bets")
    match = relationship("Match", back_populates="bets")

class MLModel(Base):
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50))
    model_type = Column(String(50))  # classification, regression
    version = Column(String(20))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    features_used = Column(JSON)
    trained_at = Column(DateTime, default=datetime.utcnow)
    model_path = Column(String(255))

class ModelPerformance(Base):
    __tablename__ = 'model_performance'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('ml_models.id'))
    date = Column(DateTime, default=datetime.utcnow)
    total_predictions = Column(Integer)
    correct_predictions = Column(Integer)
    accuracy = Column(Float)
    profit_loss = Column(Float)  # Virtual profit/loss en apuestas sugeridas
    avg_confidence = Column(Float)

# Configuración de la base de datos
engine = create_engine('sqlite:///data/database.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
