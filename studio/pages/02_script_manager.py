"""
Gestor simple de scripts en Scripts Automaticos/:
- Listar archivos .py
- Cargar contenido en editor
- Editar y guardar (sobrescribir o guardar como)
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import streamlit as st

from studio.utils.logger import log_event, log_error, log_success

SCRIPTS_DIR = Path("Scripts Automaticos")
SCRIPTS_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="Gestor de scripts", layout="wide")
st.title("Gestor de scripts (Scripts Automaticos/)")

with st.expander("Instrucciones", expanded=True):
    st.markdown(
        """
        - Carpeta base: `Scripts Automaticos/`.
        - Selecciona un archivo `.py`, edita en el cuadro y guarda.
        - Usa "Guardar como" para crear una copia con otro nombre.
        """
    )

# Modo headless (toggle)
headless = st.checkbox("Ejecutar en modo Headless (sin interfaz gráfica)", value=False)
st.info(f"Headless: {'activado' if headless else 'desactivado'}. Ajusta este valor al generar/ejecutar tus scripts.")

# Listar scripts
scripts = sorted([p.name for p in SCRIPTS_DIR.glob("*.py")])
selected = st.selectbox("Selecciona un script", options=["(Nuevo)"] + scripts)

content: str = ""
if selected != "(Nuevo)":
    try:
        content = Path(SCRIPTS_DIR / selected).read_text(encoding="utf-8")
    except Exception as exc:
        log_error("ScriptManager", f"No se pudo leer {selected}: {exc}")

code = st.text_area(
    "Editor",
    value=content,
    height=600,
    key="code_editor",
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Guardar (sobrescribir)", type="primary"):
        if selected == "(Nuevo)":
            st.error("Elige un archivo existente o usa 'Guardar como'.")
        else:
            Path(SCRIPTS_DIR / selected).write_text(code, encoding="utf-8")
            log_success("ScriptManager", f"Archivo sobrescrito: {selected}")
            st.success(f"Archivo guardado: {selected}")
with col2:
    new_name = st.text_input("Guardar como (nombre .py)", value="", key="save_as_name")
    if st.button("Guardar como copia"):
        if not new_name.endswith(".py"):
            st.error("El nombre debe terminar en .py")
        else:
            target = SCRIPTS_DIR / new_name
            target.write_text(code, encoding="utf-8")
            log_success("ScriptManager", f"Copia guardada: {new_name}")
            st.success(f"Copia guardada en: {new_name}")
