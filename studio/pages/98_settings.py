import json
from pathlib import Path
import streamlit as st

CONFIG_PATH = Path("studio/config.json")
DEFAULT_CFG = {"profile": "estandar", "lavague_mode": "api"}


def load_cfg():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CFG, indent=2), encoding="utf-8")
        return DEFAULT_CFG
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {**DEFAULT_CFG, **data}
    except Exception:
        return DEFAULT_CFG


def save_cfg(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


st.set_page_config(page_title="Ajustes", layout="wide")
st.title("Panel de Ajustes (Perfil y Motores)")

cfg = load_cfg()

profile = st.selectbox("Perfil del sistema", ["ligero", "estandar", "sin_limite"], index=["ligero", "estandar", "sin_limite"].index(cfg.get("profile", "estandar")))
lavague_mode = st.selectbox("LaVague: origen del modelo", ["api", "local"], index=["api", "local"].index(cfg.get("lavague_mode", "api")))

if st.button("Guardar ajustes"):
    new_cfg = {"profile": profile, "lavague_mode": lavague_mode}
    save_cfg(new_cfg)
    st.success("Configuracion guardada en studio/config.json")

st.info(f"Config actual: {cfg}")
