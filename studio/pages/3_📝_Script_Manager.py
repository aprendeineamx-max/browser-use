import streamlit as st
import os

st.set_page_config(page_title="Script Manager", page_icon="📝", layout="wide")
st.title("📝 Script Manager")

st.info("🚧 En construcción: Aquí podrás cargar y editar scripts.")

# Access to automated scripts
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scripts Automaticos")

if os.path.exists(SCRIPTS_DIR):
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py")]
    selected_script = st.selectbox("Selecciona un script:", scripts)
    
    if selected_script:
        file_path = os.path.join(SCRIPTS_DIR, selected_script)
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        st.text_area("Editor (Solo lectura por ahora)", code, height=400)
        st.button("Guardar Cambios (Próximamente)")
        st.button("Ejecutar Script (Próximamente)")
else:
    st.error(f"No se encontró el directorio de scripts: {SCRIPTS_DIR}")
