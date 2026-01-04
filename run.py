#!/usr/bin/env python3
"""
Script de inicialización para SportsPred Dashboard
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from ml_model import BettingPredictor
from scheduler import init_scheduler
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Inicializa la base de datos"""
    logger.info("Configurando base de datos...")
    try:
        init_db()
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
        return False
    return True

def setup_directories():
    """Crea los directorios necesarios"""
    directories = ['data', 'data/mock_data', 'data/models', 'static', 'static/css', 'pages']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Creado directorio: {directory}")
    return True

def generate_mock_data():
    """Genera datos mock iniciales"""
    logger.info("Generando datos mock iniciales...")
    try:
        from data_fetcher import DataFetcher
        fetcher = DataFetcher(use_mock=True)
        
        # Generar datos para diferentes ligas
        leagues = ['La Liga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1']
        
        for league in leagues:
            matches = fetcher.get_historical_matches(league, days_back=730)  # 2 años
            logger.info(f"Generados {len(matches)} partidos mock para {league}")
        
        logger.info("✅ Datos mock generados correctamente")
    except Exception as e:
        logger.error(f"❌ Error generando datos mock: {e}")
    return True

def train_initial_models():
    """Entrena modelos iniciales"""
    logger.info("Entrenando modelos iniciales...")
    try:
        from database import SessionLocal
        db = SessionLocal()
        
        predictor = BettingPredictor(db)
        leagues = ['La Liga', 'Premier League', 'Serie A']
        
        for league in leagues:
            accuracy = predictor.train_model(league)
            logger.info(f"Modelo para {league} entrenado - Accuracy: {accuracy:.2%}")
        
        db.close()
        logger.info("✅ Modelos entrenados correctamente")
    except Exception as e:
        logger.error(f"❌ Error entrenando modelos: {e}")
    return True

def main():
    parser = argparse.ArgumentParser(description='SportsPred Dashboard Manager')
    parser.add_argument('--setup', action='store_true', help='Configuración inicial completa')
    parser.add_argument('--db-only', action='store_true', help='Solo inicializar base de datos')
    parser.add_argument('--mock-data', action='store_true', help='Generar datos mock')
    parser.add_argument('--train', action='store_true', help='Entrenar modelos')
    parser.add_argument('--run', action='store_true', help='Ejecutar aplicación')
    parser.add_argument('--scheduler', action='store_true', help='Iniciar scheduler')
    
    args = parser.parse_args()
    
    if args.setup or args.db_only:
        setup_directories()
        setup_database()
    
    if args.setup or args.mock_data:
        generate_mock_data()
    
    if args.setup or args.train:
        train_initial_models()
    
    if args.scheduler:
        init_scheduler()
        logger.info("Scheduler iniciado. Presiona Ctrl+C para detener.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Scheduler detenido")
    
    if args.run:
        import subprocess
        subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
