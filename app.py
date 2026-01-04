# app.py - VERSIÓN CORREGIDA PARA STREAMLIT CLOUD
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import os
import sys

# Añadir el directorio actual al path para importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from streamlit_authenticator import Authenticate
except ImportError as e:
    st.error(f"Error de importación: {e}")
    st.info("Instalando dependencias faltantes...")
    import subprocess
    import pkg_resources
    
    # Lista de paquetes necesarios
    required = {
        'streamlit-authenticator': '0.2.3',
        'bcrypt': '4.0.1',
        'pyyaml': '6.0.1'
    }
    
    for package, version in required.items():
        try:
            dist = pkg_resources.get_distribution(package)
            st.write(f"✓ {package} {dist.version} está instalado")
        except pkg_resources.DistributionNotFound:
            st.write(f"Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}=={version}"])
    
    # Recargar después de instalar
    import importlib
    import streamlit_authenticator
    importlib.reload(streamlit_authenticator)
    from streamlit_authenticator import Authenticate

# Configuración de la página
st.set_page_config(
    page_title="SportsPred Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar configuración YAML o usar valores por defecto
config_path = 'config.yaml'
if os.path.exists(config_path):
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
else:
    # Configuración por defecto si no existe config.yaml
    st.warning("Archivo config.yaml no encontrado. Usando configuración por defecto.")
    config = {
        'credentials': {
            'usernames': {
                'demo': {
                    'email': 'demo@sportspred.com',
                    'name': 'Usuario Demo',
                    'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # demo123
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'sportspred_demo_key',
            'name': 'sportspred_auth'
        },
        'preauthorized': {
            'emails': []
        }
    }

# Inicializar autenticador
authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config.get('preauthorized', {})
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
    .stButton>button {
        background-color: #FF6B35;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar con autenticación
    with st.sidebar:
        st.title("⚽ SportsPred Pro")
        
        # Login/Logout
        if 'authentication_status' not in st.session_state:
            st.session_state.authentication_status = None
        
        if st.session_state.authentication_status:
            authenticator.logout('Logout', 'sidebar')
            st.write(f"Bienvenido, **{st.session_state['name']}**")
            
            # Saldo simulado
            if 'balance' not in st.session_state:
                st.session_state.balance = 1000.0
            
            st.metric("💰 Saldo", f"${st.session_state.balance:.2f}")
            
            # Navegación
            page = st.radio(
                "Navegación",
                ["🏠 Dashboard", "🔴 En Vivo", "🤖 Predicciones", "📊 Estadísticas", "🎫 Mis Apuestas"]
            )
        else:
            # Login form
            try:
                name, authentication_status, username = authenticator.login('Login', 'main')
                if authentication_status:
                    st.session_state.authentication_status = True
                    st.session_state.name = name
                    st.session_state.username = username
                    st.rerun()
                elif authentication_status == False:
                    st.error('Usuario/contraseña incorrectos')
                elif authentication_status == None:
                    st.warning('Por favor ingresa tus credenciales')
            except Exception as e:
                st.error(f"Error en autenticación: {e}")
                # Usuario demo por defecto
                if st.button("Acceder como Demo"):
                    st.session_state.authentication_status = True
                    st.session_state.name = "Usuario Demo"
                    st.session_state.username = "demo"
                    st.session_state.balance = 1000.0
                    st.rerun()
            return
    
    # Si no está autenticado, no mostrar contenido principal
    if not st.session_state.get('authentication_status'):
        st.info("Por favor inicia sesión desde la barra lateral")
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

def show_dashboard():
    """Panel principal simplificado"""
    st.markdown('<h1 class="main-header">📊 Dashboard Principal</h1>', unsafe_allow_html=True)
    
    # Selector de liga
    leagues = ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"]
    selected_league = st.selectbox("Seleccionar Liga", leagues)
    
    # Datos de ejemplo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 Partidos Hoy", "12")
    with col2:
        st.metric("🎯 Precisión Modelo", "78.5%")
    with col3:
        st.metric("💰 Valor Detectado", "+12.3%")
    with col4:
        st.metric("⚡ En Vivo", "3")
    
    # Gráfico de ejemplo
    st.subheader("📊 Distribución de Goles por Minuto - Inter de Milán")
    data = pd.DataFrame({
        'Minuto': ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90'],
        'Goles %': [8, 12, 15, 18, 22, 25],
        'Goles': [5, 8, 10, 12, 15, 18]
    })
    
    fig = px.bar(data, x='Minuto', y='Goles %', 
                 title="% de Goles por Intervalo - Temporada 2023/24",
                 color='Goles %', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de partidos
    st.subheader("🎯 Próximos Partidos - Valor Detectado")
    matches = pd.DataFrame({
        'Partido': ['Inter vs Juventus', 'Real Madrid vs Barcelona', 'Bayern vs Dortmund'],
        'Fecha': ['Hoy 20:45', 'Mañana 21:00', '15/01 20:30'],
        'Sugerencia': ['Inter ganador', 'Over 2.5 goles', 'Ambos marcan'],
        'Confianza': ['85%', '72%', '68%'],
        'Cuota': [2.10, 1.85, 1.95]
    })
    st.dataframe(matches, use_container_width=True)

def show_live_betting():
    """Página de apuestas en vivo simplificada"""
    st.markdown('<h1 class="main-header">🔴 Apuestas en Vivo</h1>', unsafe_allow_html=True)
    
    # Partidos en vivo de ejemplo
    live_matches = [
        {
            'id': 1,
            'home_team': 'Real Sociedad',
            'away_team': 'Atlético Madrid',
            'minute': 65,
            'score': '1-0',
            'odds': {'1': 3.50, 'X': 3.40, '2': 2.10}
        },
        {
            'id': 2,
            'home_team': 'Inter de Milán',
            'away_team': 'Juventus',
            'minute': 45,
            'score': '0-0',
            'odds': {'1': 1.85, 'X': 3.60, '2': 4.20}
        }
    ]
    
    for match in live_matches:
        with st.expander(f"⚽ {match['home_team']} vs {match['away_team']} - Min {match['minute']}' | {match['score']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🏠 {match['home_team']}\n{match['odds']['1']}", key=f"home_{match['id']}"):
                    st.success(f"Apuesta añadida: {match['home_team']} a ganar")
            
            with col2:
                if st.button(f"⚔ Empate\n{match['odds']['X']}", key=f"draw_{match['id']}"):
                    st.success("Apuesta añadida: Empate")
            
            with col3:
                if st.button(f"✈ {match['away_team']}\n{match['odds']['2']}", key=f"away_{match['id']}"):
                    st.success(f"Apuesta añadida: {match['away_team']} a ganar")
            
            # Mercados adicionales
            st.markdown("**📊 Mercados Adicionales**")
            col4, col5, col6, col7 = st.columns(4)
            with col4:
                if st.button(f"Over 0.5\n1.08", key=f"over05_{match['id']}"):
                    st.success("Apuesta añadida: Over 0.5 goles")
            with col5:
                if st.button(f"Over 1.5\n1.40", key=f"over15_{match['id']}"):
                    st.success("Apuesta añadida: Over 1.5 goles")
            with col6:
                if st.button(f"Over 2.5\n2.10", key=f"over25_{match['id']}"):
                    st.success("Apuesta añadida: Over 2.5 goles")
            with col7:
                if st.button(f"Ambos marcan\n1.80", key=f"btss_{match['id']}"):
                    st.success("Apuesta añadida: Ambos equipos marcan")

def show_predictions():
    """Página de predicciones simplificada"""
    st.markdown('<h1 class="main-header">🤖 Predicciones con ML</h1>', unsafe_allow_html=True)
    
    # Selector de partido
    match = st.selectbox(
        "Seleccionar Partido",
        ["Inter de Milán vs Juventus", "Real Madrid vs Barcelona", "Bayern vs Dortmund"]
    )
    
    if "Inter" in match:
        st.subheader("📊 Análisis del Partido: Inter vs Juventus")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("**🔍 Factores Clave:**")
            st.write("✅ Inter invicto en casa esta temporada (12-3-0)")
            st.write("✅ Juventus con 3 derrotas fuera de casa")
            st.write("✅ Inter anotó 35 goles en casa (promedio 2.33 por partido)")
            st.write("❌ Lautaro Martínez dudoso por lesión")
            st.write("✅ Historial H2H: Inter 4 victorias, Juventus 2, 4 empates")
        
        with col2:
            st.success("**🎯 Recomendación del Modelo:**")
            st.metric("Predicción", "Inter ganador")
            st.metric("Confianza", "78%")
            st.metric("Cuota Sugerida", "1.85")
            st.metric("Valor Esperado", "+12.3%")
        
        # Gráfico de probabilidades
        prob_data = pd.DataFrame({
            'Resultado': ['Inter gana', 'Empate', 'Juventus gana'],
            'Probabilidad': [48, 30, 22]
        })
        
        fig = px.pie(prob_data, values='Probabilidad', names='Resultado',
                    title='Probabilidades Predichas', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

def show_statistics():
    """Página de estadísticas simplificada"""
    st.markdown('<h1 class="main-header">📊 Estadísticas Detalladas</h1>', unsafe_allow_html=True)
    
    team = st.selectbox("Seleccionar Equipo", 
                       ["Inter de Milán", "Juventus", "Real Madrid", "Barcelona", "Bayern München"])
    
    if team == "Inter de Milán":
        st.subheader("📈 Estadísticas Temporada 2023/24 - Serie A")
        
        # Métricas clave
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Posición", "1º")
        with col2:
            st.metric("Puntos", "45")
        with col3:
            st.metric("Partidos", "18")
        with col4:
            st.metric("Diferencia de goles", "+38")
        
        # Tabla de estadísticas
        stats = pd.DataFrame({
            'Métrica': ['Victorias', 'Empates', 'Derrotas', 'Goles a favor', 'Goles en contra', 
                       'Clean sheets', 'Posesión promedio', 'Tiros por partido', 'Tiros a puerta'],
            'Total': [15, 3, 0, 45, 7, 12, '58.2%', 16.8, 6.3],
            'Casa': [9, 0, 0, 28, 3, 7, '62.1%', 18.2, 7.1],
            'Fuera': [6, 3, 0, 17, 4, 5, '54.3%', 15.4, 5.5]
        })
        st.dataframe(stats, use_container_width=True)

def show_my_bets():
    """Página de mis apuestas simplificada"""
    st.markdown('<h1 class="main-header">🎫 Mis Apuestas</h1>', unsafe_allow_html=True)
    
    # Historial de apuestas
    bets = pd.DataFrame({
        'Fecha': ['05/01/2024', '04/01/2024', '03/01/2024', '02/01/2024'],
        'Partido': ['Inter vs Juventus', 'Real Madrid vs Barcelona', 'Bayern vs Dortmund', 'PSG vs Marseille'],
        'Apuesta': ['Inter ganador', 'Over 2.5 goles', 'Ambos marcan', 'PSG ganador'],
        'Cuota': [2.10, 1.85, 1.95, 1.45],
        'Importe': [50, 30, 20, 40],
        'Estado': ['✅ Ganada', '❌ Perdida', '✅ Ganada', '🔄 Pendiente'],
        'Ganancia': [105, 0, 39, 0]
    })
    
    st.dataframe(bets, use_container_width=True)
    
    # Resumen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Apuestas Totales", "4")
    with col2:
        st.metric("✅ Éxito", "50%")
    with col3:
        st.metric("💰 Ganancia Neta", "+$74")

# Ticket de apuestas fijo en sidebar
if st.session_state.get('authentication_status'):
    with st.sidebar:
        st.markdown("---")
        st.subheader("🎫 Ticket de Apuestas")
        
        stake = st.number_input("Importe ($)", min_value=1.0, max_value=100.0, value=10.0, step=5.0)
        
        if st.button("📝 Crear Apuesta Demo"):
            import random
            teams = ['Inter vs Juventus', 'Real Madrid vs Barcelona', 'Bayern vs Dortmund']
            bet_types = ['Local ganador', 'Empate', 'Visitante ganador', 'Over 2.5 goles']
            odds = round(random.uniform(1.5, 3.5), 2)
            win = stake * odds
            
            st.success(f"✅ Apuesta creada!")
            st.write(f"**Partido:** {random.choice(teams)}")
            st.write(f"**Apuesta:** {random.choice(bet_types)}")
            st.write(f"**Cuota:** {odds}")
            st.write(f"**Ganancia potencial:** ${win:.2f}")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
