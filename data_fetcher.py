import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import cachetools
from config import API_CONFIG, Leagues
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.cache = cachetools.TTLCache(maxsize=100, ttl=300)  # 5 minutos cache
        
    def get_live_matches(self, league: str) -> List[Dict]:
        """Obtiene partidos en vivo de una liga específica"""
        cache_key = f"live_matches_{league}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        if self.use_mock:
            return self._get_mock_live_matches(league)
            
        try:
            # Implementación con API real
            headers = {"Authorization": f"Bearer {API_CONFIG['sportmonks']['key']}"}
            response = requests.get(
                f"{API_CONFIG['sportmonks']['base_url']}/livescores",
                params={"include": "participants,stats", "league": self._get_league_id(league)},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            matches = []
            for match in data.get('data', []):
                matches.append({
                    'id': match['id'],
                    'home_team': match['participants'][0]['name'],
                    'away_team': match['participants'][1]['name'],
                    'home_score': match['scores']['home_score'],
                    'away_score': match['scores']['away_score'],
                    'minute': match['time']['minute'],
                    'status': match['time']['status'],
                    'odds': self._get_match_odds(match['id'])
                })
            
            self.cache[cache_key] = matches
            return matches
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            return self._get_mock_live_matches(league)
    
    def get_match_stats(self, match_id: str) -> Dict:
        """Obtiene estadísticas detalladas de un partido"""
        # Implementación similar...
        pass
    
    def get_team_form(self, team_id: str, last_n: int = 5) -> Dict:
        """Obtiene forma reciente de un equipo"""
        pass
    
    def get_h2h_stats(self, team1_id: str, team2_id: str) -> Dict:
        """Obtiene historial de enfrentamientos directos"""
        pass
    
    def _get_mock_live_matches(self, league: str) -> List[Dict]:
        """Genera datos mock para desarrollo"""
        mock_matches = {
            "La Liga": [
                {
                    "id": "mock_1",
                    "home_team": "Real Sociedad",
                    "away_team": "Atlético de Madrid",
                    "home_score": 0,
                    "away_score": 0,
                    "minute": 45,
                    "status": "live",
                    "odds": {"1": 3.50, "X": 3.40, "2": 2.10},
                    "stats": {
                        "possession": {"home": 55, "away": 45},
                        "shots": {"home": 8, "away": 5},
                        "corners": {"home": 4, "away": 2}
                    }
                }
            ]
        }
        return mock_matches.get(league, [])
    
    def _get_league_id(self, league: str) -> int:
        """Mapea nombres de ligas a IDs de API"""
        league_ids = {
            "La Liga": 564,
            "Premier League": 8,
            "Bundesliga": 82,
            "Serie A": 384,
            "Ligue 1": 301
        }
        return league_ids.get(league, 564)
