"""
Browser Use Studio launcher.
Ejecutar con:
    streamlit run studio/app.py --server.port 8501
"""

import streamlit as st

st.set_page_config(page_title="Browser Use Studio", layout="wide")

st.title("Browser Use Studio")
st.markdown(
    """
Bienvenido. Usa el menú lateral para:
- Probar llaves (Google/OpenRouter)
- Gestionar scripts
- Builder de bloques
"""
)
