import streamlit as st

st.set_page_config(page_title="Visual Builder", page_icon="🧩", layout="wide")
st.title("🧩 Visual Script Builder")

st.info("🚧 En construcción: Aquí podrás crear scripts arrastrando bloques.")

# Conceptual Design
st.subheader("Diseño Conceptual")
st.markdown("""
- **Bloques Disponibles:**
    - `Navegar(url)`
    - `Click(texto/xpath)`
    - `Escribir(texto)`
    - `Scroll(pixeles)`
    - `Extraer(elemento)`
- **Salida:** Generación automática de código Python compatible con `browser-use`.
""")
