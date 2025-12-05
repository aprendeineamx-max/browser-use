"""
Lanzador raíz: la app de Streamlit ahora vive en studio/app.py con páginas en studio/pages/.

Ejecuta:
    streamlit run studio/app.py --server.port 8501
"""

import streamlit as st

st.set_page_config(page_title="Browser Use Studio (redirect)", layout="centered")
st.title("Browser Use Studio")
st.markdown(
    """
La aplicación se ha movido a `studio/app.py` con las páginas en `studio/pages/`.

Ejecuta:
```
streamlit run studio/app.py --server.port 8501
```
"""
)
