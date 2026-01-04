import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
from typing import Dict, List, Optional, Tuple
import re

def format_odds(odds: float) -> str:
    """Formatea las cuotas para mostrar"""
    return f"{odds:.2f}"

def calculate_potential_win(stake: float, odds: float) -> float:
    """Calcula la ganancia potencial"""
    return stake * odds - stake

def validate_bet(stake: float, balance: float, daily_spent: float, daily_limit: float = 100) -> Tuple[bool, str]:
    """Valida si una apuesta puede realizarse"""
    if stake <= 0:
        return False, "El importe debe ser mayor a 0"
    if stake > balance:
        return False, "Saldo insuficiente"
    if daily_spent + stake > daily_limit:
        return False, f"Límite diario excedido (${daily_limit})"
    return True, ""

def generate_match_id(home_team: str, away_team: str, date: str) -> str:
    """Genera un ID único para un partido"""
    match_string = f"{home_team}_{away_team}_{date}"
    return hashlib.md5(match_string.encode()).hexdigest()[:10]

def parse_score(score_str: str) -> Tuple[int, int]:
    """Parsea un string de resultado a tupla de enteros"""
    if not score_str or score_str == '-':
        return 0, 0
    try:
        home, away = map(int, score_str.split('-'))
        return home, away
    except:
        return 0, 0

def calculate_form(matches: List[Dict], team: str, last_n: int = 5) -> Dict:
    """Calcula la forma reciente de un equipo"""
    if not matches:
        return {"points": 0, "wins": 0, "draws": 0, "losses": 0, "avg": 0}
    
    relevant_matches = matches[-last_n:]
    points = 0
    wins = 0
    draws = 0
    losses = 0
    
    for match in relevant_matches:
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        home_score = match.get('home_score', 0)
        away_score = match.get('away_score', 0)
        
        if team == home_team:
            if home_score > away_score:
                points += 3
                wins += 1
            elif home_score == away_score:
                points += 1
                draws += 1
            else:
                losses += 1
        elif team == away_team:
            if away_score > home_score:
                points += 3
                wins += 1
            elif away_score == home_score:
                points += 1
                draws += 1
            else:
                losses += 1
    
    avg_points = points / len(relevant_matches) if relevant_matches else 0
    
    return {
        "points": points,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "avg": avg_points,
        "form_string": f"{points}p en {len(relevant_matches)} partidos"
    }

def calculate_h2h_stats(matches: List[Dict], team1: str, team2: str) -> Dict:
    """Calcula estadísticas de enfrentamientos directos"""
    h2h_matches = []
    for match in matches:
        if (match.get('home_team') == team1 and match.get('away_team') == team2) or \
           (match.get('home_team') == team2 and match.get('away_team') == team1):
            h2h_matches.append(match)
    
    if not h2h_matches:
        return {"total": 0, "team1_wins": 0, "team2_wins": 0, "draws": 0}
    
    team1_wins = 0
    team2_wins = 0
    draws = 0
    
    for match in h2h_matches:
        home_score = match.get('home_score', 0)
        away_score = match.get('away_score', 0)
        
        if match.get('home_team') == team1:
            if home_score > away_score:
                team1_wins += 1
            elif home_score < away_score:
                team2_wins += 1
            else:
                draws += 1
        else:
            if away_score > home_score:
                team1_wins += 1
            elif away_score < home_score:
                team2_wins += 1
            else:
                draws += 1
    
    return {
        "total": len(h2h_matches),
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
        "team1_win_percentage": (team1_wins / len(h2h_matches)) * 100 if h2h_matches else 0,
        "team2_win_percentage": (team2_wins / len(h2h_matches)) * 100 if h2h_matches else 0
    }

def safe_divide(numerator: float, denominator: float) -> float:
    """División segura evitando división por cero"""
    return numerator / denominator if denominator != 0 else 0.0

def get_season_year() -> str:
    """Obtiene el año de temporada actual (ej: 2023-2024)"""
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Si estamos entre julio y diciembre, es año-año+1
    if month >= 7:
        return f"{year}-{year+1}"
    else:
        return f"{year-1}-{year}"
