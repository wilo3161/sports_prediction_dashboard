import os
from dotenv import load_dotenv
from enum import Enum
from typing import Dict, List

load_dotenv()

class Leagues(Enum):
    LA_LIGA = "La Liga"
    PREMIER_LEAGUE = "Premier League"
    BUNDESLIGA = "Bundesliga"
    SERIE_A = "Serie A"
    LIGUE_1 = "Ligue 1"
    CHAMPIONS_LEAGUE = "Champions League"
    EUROPA_LEAGUE = "Europa League"

class BetTypes(Enum):
    WIN_DRAW_WIN = "1X2"
    OVER_UNDER = "Over/Under"
    BOTH_SCORE = "Ambos Marcan"
    EXACT_SCORE = "Resultado Exacto"
    DOUBLE_CHANCE = "Doble Oportunidad"
    CORNERS = "Total Tiros de Esquina"

# Configuración de APIs
API_CONFIG = {
    "sportmonks": {
        "base_url": "https://api.sportmonks.com/v3/football",
        "key": os.getenv("SPORTMONKS_API_KEY")
    },
    "api_football": {
        "base_url": "https://v3.football.api-sports.io",
        "key": os.getenv("API_FOOTBALL_KEY")
    },
    "odds_api": {
        "base_url": "https://api.the-odds-api.com/v4",
        "key": os.getenv("ODDS_API_KEY")
    }
}

# Configuración del modelo
MODEL_CONFIG = {
    "retrain_interval_hours": 24,
    "min_training_samples": 100,
    "prediction_confidence_threshold": 0.65,
    "features": [
        "home_form_last_5",
        "away_form_last_5",
        "h2h_home_wins",
        "h2h_away_wins",
        "avg_goals_scored_home",
        "avg_goals_conceded_home",
        "avg_goals_scored_away",
        "avg_goals_conceded_away",
        "injuries_home",
        "injuries_away",
        "days_since_last_match_home",
        "days_since_last_match_away",
        "is_derby",
        "league_position_home",
        "league_position_away"
    ]
}

# Colores por liga
LEAGUE_COLORS = {
    "La Liga": "#FF6B35",
    "Premier League": "#3D195B",
    "Bundesliga": "#D00000",
    "Serie A": "#008C45",
    "Ligue 1": "#0055A4",
    "Champions League": "#F9D71C",
    "Europa League": "#7B3F00"
}
