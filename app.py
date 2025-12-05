"""
Browser Use Studio (v0): Lanzador de interfaz Streamlit.

Ejecucion:
    streamlit run app.py

Paginas:
- Tester de llaves (Google / OpenRouter) en pages/01_key_tester.py
"""

import streamlit as st


st.set_page_config(page_title="Browser Use Studio", layout="wide")

st.title("Browser Use Studio")
st.markdown(
    """
Interfaz inicial para probar llaves de proveedores y preparar automatizaciones con Browser-Use.

**Uso rápido**
1. Asegura tu entorno virtual.
2. Instala dependencias mínimas si te falta streamlit/requests:
   ```
   pip install streamlit requests
   ```
3. Ejecuta:
   ```
   streamlit run app.py
   ```

Ve al menú lateral para abrir el tester de llaves.
"""
)
