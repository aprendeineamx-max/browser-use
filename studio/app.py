"""
Browser Use Studio launcher.
Ejecutar con:
    streamlit run studio/app.py --server.port 8501
"""

import os
from pathlib import Path

import psutil
import streamlit as st

from studio.engines.browser_use_engine import BrowserUseEngine
from studio.engines.stagehand_engine import StagehandEngine
from studio.engines.skyvern_engine import SkyvernEngine
from studio.engines.lavague_engine import LaVagueEngine
from studio.utils.sentinel import ensure_config
from studio.utils.logger import log_event

st.set_page_config(page_title="Browser Use Studio", layout="wide")

st.title("Browser Use Studio")

# Panel de estado en vivo
config = ensure_config()
mem = psutil.virtual_memory().percent
cpu = psutil.cpu_percent(interval=0.2)


def detect_env_keys():
    providers = {"google": [], "groq": [], "openrouter": []}
    for name, val in os.environ.items():
        low = name.lower()
        if "google" in low and "api_key" in low:
            providers["google"].append((name, val))
        if "groq_api_key" in low:
            providers["groq"].append((name, val))
        if "openrouter_api_key" in low:
            providers["openrouter"].append((name, val))
    return providers


# Sidebar: configuracion dinamica de proveedor/modelo/key por sesion
with st.sidebar:
    st.header("Sesion LLM dinamica")
    providers = detect_env_keys()
    provider_choice = st.selectbox("Proveedor", ["google", "groq", "openrouter"], index=0)
    available_keys = providers.get(provider_choice, [])
    key_labels = [f"{name} (****{val[-4:]})" for name, val in available_keys] or ["(sin vars de entorno)"]
    key_selection = st.selectbox("Key (entorno)", key_labels, index=0 if key_labels else None)
    custom_key = st.text_input("Key manual (opcional)", value="", type="password")
    model_choice = st.text_input("Modelo preferido", value=st.session_state.get("session_model", ""))

    if st.button("Guardar sesion LLM"):
        key_value = ""
        key_name = ""
        if available_keys and key_selection in key_labels:
            idx = key_labels.index(key_selection)
            key_name, key_value = available_keys[idx]
        if custom_key:
            key_value = custom_key
            key_name = "manual"
        st.session_state["session_provider"] = provider_choice
        st.session_state["session_model"] = model_choice
        st.session_state["session_api_key"] = key_value
        log_event("App", f"Sesion LLM actualizada provider={provider_choice} key={key_name} model={model_choice}")
        st.success("Sesion LLM actualizada para esta ejecucion.")

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
