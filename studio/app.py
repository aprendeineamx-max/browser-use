"""
Browser Use Studio launcher.
Ejecutar con:
    streamlit run studio/app.py --server.port 8501
"""

from pathlib import Path

import psutil
import streamlit as st

from studio.engines.browser_use_engine import BrowserUseEngine
from studio.engines.stagehand_engine import StagehandEngine
from studio.engines.skyvern_engine import SkyvernEngine
from studio.engines.lavague_engine import LaVagueEngine
from studio.utils.sentinel import ensure_config

st.set_page_config(page_title="Browser Use Studio", layout="wide")

st.title("Browser Use Studio")

# Panel de estado en vivo
config = ensure_config()
mem = psutil.virtual_memory().percent
cpu = psutil.cpu_percent(interval=0.2)

engines = [
    ("Browser Use", BrowserUseEngine),
    ("Stagehand (Node)", StagehandEngine),
    ("Skyvern (Docker)", SkyvernEngine),
    ("LaVague (Python)", LaVagueEngine),
]
active_count = sum(1 for _, cls in engines if cls.is_available())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Motores activos", active_count, help="Motores con is_available()==True")
col2.metric("RAM %", f"{mem:.1f}%")
col3.metric("CPU %", f"{cpu:.1f}%")
col4.metric("Perfil activo", config.get("profile", "estandar").capitalize())

st.markdown(
    """
Bienvenido. Usa el menú lateral para:
- Probar llaves (Google/OpenRouter)
- Gestionar scripts
- Builder de bloques y ejecutar al instante
- Laboratorio de motores (Browser Use, Stagehand, Skyvern mock, LaVague)
"""
)
