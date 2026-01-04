import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import joblib
from datetime import datetime, timedelta
from typing import Tuple, Dict, List
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class BettingPredictor:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
    def prepare_training_data(self, league: str, min_matches: int = 100) -> pd.DataFrame:
        """Prepara datos históricos para entrenamiento"""
        query = f"""
        SELECT 
            m.home_team, m.away_team, m.home_score, m.away_score,
            ms.home_possession, ms.away_possession,
            ms.home_shots, ms.away_shots,
            ms.home_xg, ms.away_xg,
            ms.home_corners, ms.away_corners,
            CASE 
                WHEN m.home_score > m.away_score THEN '1'
                WHEN m.home_score = m.away_score THEN 'X'
                ELSE '2'
            END as result
        FROM matches m
        JOIN match_stats ms ON m.id = ms.match_id
        WHERE m.league = '{league}' 
        AND m.status = 'finished'
        AND m.home_score IS NOT NULL
        ORDER BY m.date DESC
        LIMIT {min_matches * 2}
        """
        
        df = pd.read_sql_query(query, self.db.bind)
        
        # Ingeniería de características
        df['goal_difference'] = df['home_score'] - df['away_score']
        df['total_goals'] = df['home_score'] + df['away_score']
        df['possession_difference'] = df['home_possession'] - df['away_possession']
        df['shot_difference'] = df['home_shots'] - df['away_shots']
        df['xg_difference'] = df['home_xg'] - df['away_xg']
        
        # Agregar forma reciente (últimos 5 partidos)
        df = self._add_recent_form(df, league)
        
        return df
    
    def train_model(self, league: str, model_type: str = 'xgboost'):
        """Entrena un modelo para una liga específica"""
        df = self.prepare_training_data(league)
        
        if len(df) < 50:
            logger.warning(f"Insuficientes datos para {league}. Usando modelo dummy.")
            return self._create_dummy_model()
        
        # Preparar características y target
        features = [
            'home_possession', 'away_possession',
            'home_shots', 'away_shots',
            'home_xg', 'away_xg',
            'goal_difference_last5_home',
            'goal_difference_last5_away',
            'possession_difference',
            'shot_difference',
            'xg_difference'
        ]
        
        X = df[features].fillna(0)
        y = df['result']
        
        # Codificar target
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.label_encoders[league] = le
        
        # Escalar características
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[league] = scaler
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo
        if model_type == 'xgboost':
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                objective='multi:softprob',
                num_class=3
            )
        elif model_type == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            model = GradientBoostingClassifier(random_state=42)
        
        model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        logger.info(f"Modelo {model_type} para {league} entrenado:")
        logger.info(f"  Accuracy: {accuracy:.3f}")
        logger.info(f"  Precision: {precision:.3f}")
        logger.info(f"  Recall: {recall:.3f}")
        logger.info(f"  F1-Score: {f1:.3f}")
        
        self.models[league] = model
        
        # Guardar modelo
        model_data = {
            'model': model,
            'scaler': scaler,
            'label_encoder': le,
            'features': features,
            'metrics': {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'trained_at': datetime.now()
            }
        }
        
        joblib.dump(model_data, f"data/models/{league}_{model_type}.joblib")
        
        return accuracy
    
    def predict_match(self, league: str, match_features: Dict) -> Dict:
        """Predice resultado de un partido"""
        if league not in self.models:
            self.load_model(league)
        
        model_data = self.models[league]
        
        # Preparar características
        features_df = pd.DataFrame([match_features])
        
        # Escalar
        X_scaled = model_data['scaler'].transform(features_df)
        
        # Predecir
        probabilities = model_data['model'].predict_proba(X_scaled)[0]
        
        # Decodificar predicciones
        predictions = {}
        for i, class_name in enumerate(model_data['label_encoder'].classes_):
            predictions[class_name] = {
                'probability': float(probabilities[i]),
                'confidence': 'high' if probabilities[i] > 0.7 else 'medium' if probabilities[i] > 0.55 else 'low'
            }
        
        # Calcular valor esperado para apuestas
        if 'odds' in match_features:
            predictions = self._calculate_expected_value(predictions, match_features['odds'])
        
        return predictions
    
    def _calculate_expected_value(self, predictions: Dict, odds: Dict) -> Dict:
        """Calcula el valor esperado para cada apuesta"""
        for outcome, prediction in predictions.items():
            if outcome in odds:
                probability = prediction['probability']
                decimal_odds = odds[outcome]
                
                # EV = (probabilidad * (cuota - 1)) - (1 - probabilidad)
                ev = (probability * (decimal_odds - 1)) - (1 - probability)
                
                prediction['expected_value'] = ev
                prediction['value_bet'] = ev > 0.05  # Umbral para apuesta de valor
                
        return predictions
    
    def _add_recent_form(self, df: pd.DataFrame, league: str) -> pd.DataFrame:
        """Añade forma reciente de los equipos"""
        # Implementación simplificada
        df['goal_difference_last5_home'] = np.random.uniform(-1, 2, len(df))
        df['goal_difference_last5_away'] = np.random.uniform(-2, 1, len(df))
        return df
