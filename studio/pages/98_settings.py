import json
from pathlib import Path
import streamlit as st

from studio.utils.sentinel import truncate_logs, log_line
from studio.utils.planner_settings import load_config, save_config

CONFIG_PATH = Path("studio/config.json")
DEFAULT_CFG = {"profile": "estandar", "lavague_mode": "api", "orchestrator_planner": "groq:llama-3.1-8b-instant"}


st.set_page_config(page_title="Ajustes", layout="wide")
st.title("Panel de Ajustes (Perfil y Motores)")

cfg = load_config()

profile = st.selectbox("Perfil del sistema", ["ligero", "estandar", "sin_limite"], index=["ligero", "estandar", "sin_limite"].index(cfg.get("profile", "estandar")))
lavague_mode = st.selectbox("LaVague: origen del modelo", ["api", "local"], index=["api", "local"].index(cfg.get("lavague_mode", "api")))

st.markdown("---")
st.subheader("Planificador del Orchestrator (LLM)")
planner_option = st.text_input("Proveedor y modelo (formato proveedor:modelo)", value=cfg.get("orchestrator_planner", "groq:llama-3.1-8b-instant"))

if st.button("Guardar ajustes"):
    new_cfg = {**cfg, "profile": profile, "lavague_mode": lavague_mode, "orchestrator_planner": planner_option}
    save_config(new_cfg)
    st.success("Configuracion guardada en studio/config.json")

if st.button("Limpiar logs (mantener ultimas 10 lineas)"):
    truncate_logs(keep_lines=10)
    log_line("Solicitud manual: truncar logs desde la UI")
    st.success("Registro_de_logs.txt truncado (ultimas 10 lineas conservadas).")

st.info(f"Config actual: {cfg}")
