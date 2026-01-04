import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FreeDataFetcher:
    """Obtiene datos deportivos de fuentes gratuitas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_inter_milan_stats(self, years_back: int = 2) -> Dict:
        """
        Obtiene estadísticas de Inter de Milán de los últimos años
        Usando web scraping de sitios públicos
        """
        # Datos mock realistas para desarrollo
        # En producción, implementarías web scraping aquí
        
        current_year = datetime.now().year
        seasons = []
        
        for i in range(years_back):
            season_year = current_year - i
            season_str = f"{season_year-1}-{season_year}"
            
            # Estadísticas realistas de Inter de Milán (puedes actualizar con datos reales)
            season_stats = {
                "season": season_str,
                "league_position": 1 if season_str == "2023-2024" else 2 if season_str == "2022-2023" else 3,
                "matches_played": 38,
                "wins": 28 if season_str == "2023-2024" else 23,
                "draws": 7 if season_str == "2023-2024" else 10,
                "losses": 3 if season_str == "2023-2024" else 5,
                "goals_for": 84 if season_str == "2023-2024" else 71,
                "goals_against": 22 if season_str == "2023-2024" else 28,
                "clean_sheets": 18 if season_str == "2023-2024" else 15,
                "avg_possession": 55.3 if season_str == "2023-2024" else 53.7,
                "shots_per_game": 15.2 if season_str == "2023-2024" else 14.5,
                "shots_on_target_per_game": 5.8 if season_str == "2023-2024" else 5.2,
                "pass_accuracy": 87.1 if season_str == "2023-2024" else 85.6,
                "top_scorer": "Lautaro Martínez" if season_str == "2023-2024" else "Lautaro Martínez",
                "top_scorer_goals": 24 if season_str == "2023-2024" else 21
            }
            seasons.append(season_stats)
        
        return {
            "team": "Inter de Milán",
            "seasons": seasons,
            "current_form": self._get_current_form("Inter de Milán"),
            "home_record": self._get_home_record("Inter de Milán"),
            "away_record": self._get_away_record("Inter de Milán"),
            "goal_timing": self._get_goal_timing_stats("Inter de Milán")
        }
    
    def _get_current_form(self, team: str) -> List[str]:
        """Forma reciente (últimos 5 partidos)"""
        # W = Win, D = Draw, L = Loss
        forms = {
            "Inter de Milán": ["W", "W", "D", "W", "W"],
            "Juventus": ["W", "L", "W", "D", "W"],
            "AC Milan": ["W", "W", "L", "W", "D"],
            "Real Madrid": ["W", "W", "W", "D", "W"],
            "Barcelona": ["W", "D", "W", "L", "W"]
        }
        return forms.get(team, ["W", "D", "L", "W", "D"])
    
    def _get_home_record(self, team: str) -> Dict:
        """Récord en casa"""
        records = {
            "Inter de Milán": {"wins": 12, "draws": 3, "losses": 0, "goals_for": 35, "goals_against": 8},
            "Juventus": {"wins": 10, "draws": 4, "losses": 1, "goals_for": 28, "goals_against": 12},
            "AC Milan": {"wins": 9, "draws": 5, "losses": 1, "goals_for": 30, "goals_against": 15}
        }
        return records.get(team, {"wins": 8, "draws": 5, "losses": 2, "goals_for": 25, "goals_against": 14})
    
    def _get_away_record(self, team: str) -> Dict:
        """Récord fuera de casa"""
        records = {
            "Inter de Milán": {"wins": 9, "draws": 4, "losses": 2, "goals_for": 25, "goals_against": 10},
            "Juventus": {"wins": 8, "draws": 3, "losses": 4, "goals_for": 22, "goals_against": 15},
            "AC Milan": {"wins": 7, "draws": 4, "losses": 4, "goals_for": 20, "goals_against": 18}
        }
        return records.get(team, {"wins": 6, "draws": 5, "losses": 4, "goals_for": 18, "goals_against": 16})
    
    def _get_goal_timing_stats(self, team: str) -> Dict:
        """Distribución de goles por minutos"""
        stats = {
            "Inter de Milán": {
                "0-15": 8,
                "16-30": 12,
                "31-45": 15,
                "46-60": 18,
                "61-75": 22,
                "76-90": 29
            },
            "Juventus": {
                "0-15": 6,
                "16-30": 10,
                "31-45": 14,
                "46-60": 16,
                "61-75": 20,
                "76-90": 24
            }
        }
        return stats.get(team, {
            "0-15": 7, "16-30": 11, "31-45": 14, "46-60": 17, "61-75": 21, "76-90": 26
        })
    
    def get_match_history(self, team1: str, team2: str, limit: int = 10) -> List[Dict]:
        """Historial de enfrentamientos directos"""
        # Datos mock de Inter vs Juventus
        if "Inter" in team1 and "Juventus" in team2 or "Inter" in team2 and "Juventus" in team1:
            return [
                {"date": "2024-02-04", "home": "Inter de Milán", "away": "Juventus", "score": "1-0", "competition": "Serie A"},
                {"date": "2023-11-26", "home": "Juventus", "away": "Inter de Milán", "score": "1-1", "competition": "Serie A"},
                {"date": "2023-04-26", "home": "Inter de Milán", "away": "Juventus", "score": "1-0", "competition": "Coppa Italia"},
                {"date": "2023-03-19", "home": "Inter de Milán", "away": "Juventus", "score": "0-1", "competition": "Serie A"},
                {"date": "2022-11-06", "home": "Juventus", "away": "Inter de Milán", "score": "2-0", "competition": "Serie A"},
                {"date": "2022-05-11", "home": "Juventus", "away": "Inter de Milán", "score": "2-4", "competition": "Coppa Italia"},
                {"date": "2022-04-03", "home": "Juventus", "away": "Inter de Milán", "score": "0-1", "competition": "Serie A"},
                {"date": "2021-10-24", "home": "Inter de Milán", "away": "Juventus", "score": "1-1", "competition": "Serie A"},
                {"date": "2021-05-15", "home": "Juventus", "away": "Inter de Milán", "score": "3-2", "competition": "Serie A"},
                {"date": "2021-01-17", "home": "Inter de Milán", "away": "Juventus", "score": "2-0", "competition": "Serie A"}
            ]
        return []
    
    def scrape_odds_from_website(self) -> List[Dict]:
        """
        Ejemplo de web scraping para obtener odds (solo para fines educativos)
        IMPORTANTE: Verifica los términos de servicio del sitio web
        """
        try:
            # Ejemplo con sitio público (usar con moderación y respetando robots.txt)
            url = "https://www.oddsportal.com/soccer/italy/serie-a/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Este es un ejemplo genérico - necesitarías adaptar los selectores
                matches = []
                match_elements = soup.select('.table-main .deactivate')
                
                for element in match_elements[:5]:  # Limitar a 5 partidos
                    try:
                        teams = element.select('.name')
                        if len(teams) >= 2:
                            home_team = teams[0].text.strip()
                            away_team = teams[1].text.strip()
                            
                            odds_elements = element.select('.odds')
                            if len(odds_elements) >= 3:
                                home_odds = float(odds_elements[0].text.strip())
                                draw_odds = float(odds_elements[1].text.strip())
                                away_odds = float(odds_elements[2].text.strip())
                                
                                matches.append({
                                    "home_team": home_team,
                                    "away_team": away_team,
                                    "odds": {
                                        "1": home_odds,
                                        "X": draw_odds,
                                        "2": away_odds
                                    }
                                })
                    except:
                        continue
                
                return matches
        except Exception as e:
            logger.error(f"Error en web scraping: {e}")
        
        # Datos mock si falla el scraping
        return self.get_mock_odds()
    
    def get_mock_odds(self) -> List[Dict]:
        """Datos mock de odds"""
        return [
            {
                "home_team": "Inter de Milán",
                "away_team": "Juventus",
                "odds": {"1": 1.80, "X": 3.60, "2": 4.50},
                "over_under": {
                    "over_0.5": 1.08, "under_0.5": 8.00,
                    "over_1.5": 1.40, "under_1.5": 2.75,
                    "over_2.5": 2.10, "under_2.5": 1.66,
                    "over_3.5": 3.50, "under_3.5": 1.28
                }
            },
            {
                "home_team": "AC Milan",
                "away_team": "Napoli",
                "odds": {"1": 2.10, "X": 3.40, "2": 3.50},
                "over_under": {
                    "over_0.5": 1.10, "under_0.5": 7.00,
                    "over_1.5": 1.45, "under_1.5": 2.60,
                    "over_2.5": 2.25, "under_2.5": 1.61
                }
            }
        ]

# Añade este método a tu DataFetcher existente

class DataFetcher:
    # ... código existente ...
    
    def get_team_historical_stats(self, team_name: str, years_back: int = 2):
        """Obtiene estadísticas históricas de un equipo"""
        if self.use_mock or not self.has_api_keys():
            free_fetcher = FreeDataFetcher()
            
            if "Inter" in team_name:
                return free_fetcher.get_inter_milan_stats(years_back)
            
            # Datos genéricos para otros equipos
            return self._generate_generic_stats(team_name, years_back)
        else:
            # Usar API real si tienes claves
            return self._get_stats_from_api(team_name, years_back)
    
    def _generate_generic_stats(self, team_name: str, years_back: int) -> Dict:
        """Genera estadísticas genéricas para equipos"""
        current_year = datetime.now().year
        seasons = []
        
        for i in range(years_back):
            season_year = current_year - i
            season_str = f"{season_year-1}-{season_year}"
            
            # Posiciones realistas basadas en el nombre del equipo
            if any(keyword in team_name.lower() for keyword in ['real', 'barca', 'bayern', 'city', 'psg']):
                position = np.random.randint(1, 4)
                wins = np.random.randint(24, 30)
            elif any(keyword in team_name.lower() for keyword in ['united', 'chelsea', 'atletico', 'dortmund']):
                position = np.random.randint(4, 8)
                wins = np.random.randint(18, 24)
            else:
                position = np.random.randint(8, 15)
                wins = np.random.randint(12, 18)
            
            season_stats = {
                "season": season_str,
                "league_position": position,
                "matches_played": 38,
                "wins": wins,
                "draws": np.random.randint(6, 12),
                "losses": 38 - wins - np.random.randint(6, 12),
                "goals_for": wins * 2 + np.random.randint(10, 30),
                "goals_against": (38 - wins) * 1 + np.random.randint(5, 20),
                "clean_sheets": wins // 2 + np.random.randint(2, 8)
            }
            seasons.append(season_stats)
        
        return {
            "team": team_name,
            "seasons": seasons,
            "current_form": ["W", "D", "L", "W", "W"][:np.random.randint(3, 6)],
            "home_record": {
                "wins": np.random.randint(8, 14),
                "draws": np.random.randint(3, 7),
                "losses": np.random.randint(0, 3)
            }
        }
