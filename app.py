import streamlit as st
from streamlit_authenticator import Authenticator
import yaml
from yaml.loader import SafeLoader
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

from config import LEAGUE_COLORS, Leagues, BetTypes
from database import init_db, get_db
from data_fetcher import DataFetcher
from ml_model import BettingPredictor
from utils import format_odds, calculate_potential_win, validate_bet

# Configuración de la página
st.set_page_config(
    page_title="SportsPred Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/sportspred',
        'Report a bug': "https://github.com/sportspred/issues",
        'About': """
        # SportsPred Pro Dashboard
        Plataforma educativa de análisis deportivo y predicciones.
        **Solo para fines educativos.**
        """
    }
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .league-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        border-left: 5px solid;
    }
    .bet-ticket {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 1.5rem;
        position: sticky;
        top: 20px;
    }
    .prediction-high {
        color: #00FF00;
        font-weight: bold;
    }
    .prediction-medium {
        color: #FFFF00;
        font-weight: bold;
    }
    .prediction-low {
        color: #FF6B6B;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B35;
        color: white;
    }
    .stSelectbox, .stNumberInput {
        background-color: #2D2D2D;
    }
</style>
""", unsafe_allow_html=True)

# Autenticación
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Inicializar base de datos
init_db()

def main():
    # Sidebar con autenticación
    with st.sidebar:
        st.image("static/images/logo.png", width=200)
        st.title("⚽ SportsPred Pro")
        
        # Login/Logout
        if 'authentication_status' not in st.session_state:
            st.session_state.authentication_status = None
        
        if st.session_state.authentication_status:
            authenticator.logout('Logout', 'main')
            st.write(f"Bienvenido, {st.session_state['name']}")
            
            # Saldo del usuario
            st.metric("💰 Saldo", f"${st.session_state.get('balance', 1000):.2f}")
            
            # Límite diario
            st.progress(st.session_state.get('daily_spent', 0) / 100)
            st.caption(f"Gastado hoy: ${st.session_state.get('daily_spent', 0):.2f} / $100")
            
            # Navegación
            page = st.radio(
                "Navegación",
                ["🏠 Dashboard", "🔴 En Vivo", "🤖 Predicciones", "📊 Estadísticas", "🎫 Mis Apuestas", "⚙️ Admin"]
            )
        else:
            name, authentication_status, username = authenticator.login('Login', 'main')
            if authentication_status == False:
                st.error('Usuario/contraseña incorrectos')
            elif authentication_status == None:
                st.warning('Por favor ingresa tus credenciales')
            return
    
    # Páginas principales
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🔴 En Vivo":
        show_live_betting()
    elif page == "🤖 Predicciones":
        show_predictions()
    elif page == "📊 Estadísticas":
        show_statistics()
    elif page == "🎫 Mis Apuestas":
        show_my_bets()
    elif page == "⚙️ Admin":
        show_admin()

def show_dashboard():
    """Panel principal del dashboard"""
    st.markdown('<h1 class="main-header">📊 Dashboard Principal</h1>', unsafe_allow_html=True)
    
    # Selector de liga
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_league = st.selectbox(
            "Seleccionar Liga",
            [league.value for league in Leagues],
            format_func=lambda x: f"⚽ {x}"
        )
    
    with col2:
        days_range = st.selectbox("Rango", ["Hoy", "7 días", "30 días"])
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refrescar", value=True)
    
    # Obtener datos
    fetcher = DataFetcher(use_mock=True)
    live_matches = fetcher.get_live_matches(selected_league)
    
    # Tarjetas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 Partidos Hoy", len(live_matches))
    with col2:
        st.metric("🎯 Precisión Modelo", "78.5%")
    with col3:
        st.metric("💰 Valor Detectado", "+12.3%")
    with col4:
        st.metric("⚡ En Vivo", f"{sum(1 for m in live_matches if m['status'] == 'live')}")
    
    # Gráficos y contenido principal
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Predicciones", "📈 Estadísticas", "🔥 En Vivo", "💎 Valor"])
    
    with tab1:
        show_predictions_tab(selected_league)
    
    with tab2:
        show_statistics_tab(selected_league)
    
    with tab3:
        show_live_tab(live_matches)
    
    with tab4:
        show_value_bets_tab(selected_league)
    
    # Ticket de apuestas (sticky)
    with st.sidebar:
        show_bet_ticket()

def show_live_betting():
    """Página de apuestas en vivo"""
    st.markdown('<h1 class="main-header">🔴 Apuestas en Vivo</h1>', unsafe_allow_html=True)
    
    # Selector de competiciones en vivo
    competitions = ["La Liga", "Premier League", "Champions League", "Europa League", "Amistosos"]
    selected_comp = st.selectbox("Competición", competitions)
    
    # Obtener partidos en vivo
    fetcher = DataFetcher(use_mock=True)
    live_matches = fetcher.get_live_matches(selected_comp)
    
    # Mostrar partidos en vivo
    for match in live_matches:
        with st.expander(f"⚽ {match['home_team']} vs {match['away_team']} - Min {match['minute']}'"):
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.subheader(match['home_team'])
                if 'stats' in match:
                    st.metric("Posesión", f"{match['stats']['possession']['home']}%")
                    st.metric("Tiros", match['stats']['shots']['home'])
            
            with col2:
                st.markdown(f"<h1 style='text-align: center;'>{match['home_score']} - {match['away_score']}</h1>", 
                          unsafe_allow_html=True)
                st.caption(f"Minuto: {match['minute']}'")
                st.progress(match['minute']/90)
            
            with col3:
                st.subheader(match['away_team'])
                if 'stats' in match:
                    st.metric("Posesión", f"{match['stats']['possession']['away']}%")
                    st.metric("Tiros", match['stats']['shots']['away'])
            
            # Mercados de apuestas
            st.markdown("### 📊 Mercados de Apuesta")
            
            # 1X2
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🏠 {match['home_team']}\n{match['odds']['1']}", key=f"home_{match['id']}"):
                    add_to_bet_ticket(match, "1", match['odds']['1'])
            with col2:
                if st.button(f"⚔ Empate\n{match['odds']['X']}", key=f"draw_{match['id']}"):
                    add_to_bet_ticket(match, "X", match['odds']['X'])
            with col3:
                if st.button(f"✈ {match['away_team']}\n{match['odds']['2']}", key=f"away_{match['id']}"):
                    add_to_bet_ticket(match, "2", match['odds']['2'])
            
            # Over/Under
            st.markdown("#### Over/Under")
            over_under_cols = st.columns(5)
            markets = [
                ("Over 0.5", 1.08, 8.00),
                ("Over 1.5", 1.40, 2.75),
                ("Over 2.5", 2.10, 1.66),
                ("Over 3.5", 3.50, 1.28),
                ("Over 4.5", 6.00, 1.12)
            ]
            
            for idx, (market, over_odd, under_odd) in enumerate(markets):
                with over_under_cols[idx]:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"➕\n{over_odd}", key=f"over_{market}_{match['id']}"):
                            add_to_bet_ticket(match, f"Over {market.split()[1]}", over_odd)
                    with col2:
                        if st.button(f"➖\n{under_odd}", key=f"under_{market}_{match['id']}"):
                            add_to_bet_ticket(match, f"Under {market.split()[1]}", under_odd)

def show_predictions():
    """Página de predicciones ML"""
    st.markdown('<h1 class="main-header">🤖 Predicciones con Machine Learning</h1>', unsafe_allow_html=True)
    
    # Inicializar predictor
    db = next(get_db())
    predictor = BettingPredictor(db)
    
    # Selector de partido
    fetcher = DataFetcher(use_mock=True)
    matches = fetcher.get_live_matches("La Liga")
    
    selected_match = st.selectbox(
        "Seleccionar Partido",
        matches,
        format_func=lambda m: f"{m['home_team']} vs {m['away_team']}"
    )
    
    if selected_match:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Características del partido para el modelo
            match_features = {
                'home_possession': selected_match['stats']['possession']['home'],
                'away_possession': selected_match['stats']['possession']['away'],
                'home_shots': selected_match['stats']['shots']['home'],
                'away_shots': selected_match['stats']['shots']['away'],
                'home_xg': 1.8,  # Valores mock
                'away_xg': 1.2,
                'goal_difference_last5_home': 0.5,
                'goal_difference_last5_away': -0.2,
                'odds': selected_match['odds']
            }
            
            # Obtener predicciones
            predictions = predictor.predict_match("La Liga", match_features)
            
            # Mostrar predicciones
            st.markdown("### 📊 Predicciones del Modelo")
            
            for outcome, prediction in predictions.items():
                confidence_class = f"prediction-{prediction['confidence']}"
                col_pred1, col_pred2, col_pred3 = st.columns([1, 1, 2])
                
                with col_pred1:
                    if outcome == "1":
                        st.markdown(f"**🏠 {selected_match['home_team']}**")
                    elif outcome == "X":
                        st.markdown("**⚔ Empate**")
                    else:
                        st.markdown(f"**✈ {selected_match['away_team']}**")
                
                with col_pred2:
                    st.markdown(f"<span class='{confidence_class}'>{prediction['probability']*100:.1f}%</span>", 
                              unsafe_allow_html=True)
                
                with col_pred3:
                    if 'expected_value' in prediction:
                        ev_color = "green" if prediction['expected_value'] > 0 else "red"
                        st.markdown(f"Valor: <span style='color:{ev_color}'>{prediction['expected_value']:.3f}</span>", 
                                  unsafe_allow_html=True)
                        if prediction.get('value_bet', False):
                            st.success("✅ APUESTA DE VALOR DETECTADA")
            
            # Gráfico de probabilidades
            fig = go.Figure(data=[
                go.Bar(
                    x=list(predictions.keys()),
                    y=[p['probability']*100 for p in predictions.values()],
                    text=[f"{p['probability']*100:.1f}%" for p in predictions.values()],
                    textposition='auto',
                    marker_color=['#FF6B35', '#4ECDC4', '#45B7D1']
                )
            ])
            fig.update_layout(
                title="Probabilidades Predichas",
                yaxis_title="Probabilidad (%)",
                xaxis_title="Resultado"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Panel de análisis detallado
            st.markdown("### 🔍 Análisis Detallado")
            
            # Factores clave
            st.markdown("#### 📈 Factores Clave")
            factors = [
                ("Forma Local", "+0.5", "green"),
                ("Forma Visitante", "-0.2", "red"),
                ("H2H Histórico", "+0.3", "green"),
                ("Lesiones", "-0.4", "red"),
                ("Descanso", "+0.2", "green")
            ]
            
            for factor, value, color in factors:
                col_factor1, col_factor2 = st.columns([3, 1])
                with col_factor1:
                    st.write(factor)
                with col_factor2:
                    st.markdown(f"<span style='color:{color}'>{value}</span>", unsafe_allow_html=True)
            
            # Recomendación del modelo
            st.markdown("#### 🎯 Recomendación")
            best_pred = max(predictions.items(), key=lambda x: x[1]['probability'])
            
            if best_pred[1]['probability'] > 0.7:
                st.success(f"**RECOMENDACIÓN FUERTE:** {best_pred[0]}")
                st.metric("Confianza", f"{best_pred[1]['probability']*100:.1f}%")
                st.metric("Cuota Sugerida", f"{1/best_pred[1]['probability']:.2f}")
            elif best_pred[1]['probability'] > 0.55:
                st.warning(f"**RECOMENDACIÓN MODERADA:** {best_pred[0]}")
                st.metric("Confianza", f"{best_pred[1]['probability']*100:.1f}%")
            else:
                st.info(f"**PREDICCIÓN INCIERTA:** {best_pred[0]}")
                st.metric("Confianza", f"{best_pred[1]['probability']*100:.1f}%")

def show_bet_ticket():
    """Componente de ticket de apuestas"""
    st.markdown("### 🎫 Ticket de Apuestas")
    
    if 'bet_slip' not in st.session_state:
        st.session_state.bet_slip = []
    
    if not st.session_state.bet_slip:
        st.info("Añade selecciones a tu ticket")
        return
    
    total_odds = 1.0
    for bet in st.session_state.bet_slip:
        st.markdown(f"**{bet['match']}**")
        st.markdown(f"{bet['selection']} @ {bet['odds']}")
        st.markdown("---")
        total_odds *= bet['odds']
    
    st.markdown(f"**Cuota Total:** {total_odds:.2f}")
    
    stake = st.number_input("Importe a apostar ($)", min_value=1.0, max_value=100.0, value=10.0)
    potential_win = stake * total_odds
    
    st.metric("Ganancia Potencial", f"${potential_win:.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmar Apuesta"):
            place_bet(stake, total_odds, potential_win)
    with col2:
        if st.button("🗑 Limpiar Ticket"):
            st.session_state.bet_slip = []
            st.rerun()

def add_to_bet_ticket(match, selection, odds):
    """Añade una selección al ticket"""
    if 'bet_slip' not in st.session_state:
        st.session_state.bet_slip = []
    
    bet = {
        'match': f"{match['home_team']} vs {match['away_team']}",
        'selection': selection,
        'odds': odds,
        'match_id': match['id']
    }
    
    st.session_state.bet_slip.append(bet)
    st.success("Selección añadida al ticket!")

def place_bet(stake, odds, potential_win):
    """Registra una apuesta"""
    # Validar límites
    daily_spent = st.session_state.get('daily_spent', 0)
    if daily_spent + stake > 100:
        st.error("Has superado tu límite diario de $100")
        return
    
    # Registrar en base de datos
    db = next(get_db())
    # Implementar lógica de guardado
    
    st.success(f"Apuesta registrada por ${stake:.2f}")
    st.session_state.bet_slip = []
    st.session_state.daily_spent = daily_spent + stake
    
    # Actualizar saldo (simulado)
    if 'balance' in st.session_state:
        st.session_state.balance -= stake

if __name__ == "__main__":
    main()
