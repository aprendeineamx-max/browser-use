import streamlit as st

st.set_page_config(
    page_title="Browser Use Studio",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Browser Use Studio")

st.markdown("""
### Bienvenido a tu entorno de desarrollo para Agentes Web.

Esta aplicación te permite gestionar, construir y ejecutar tus agentes de `browser-use` de manera visual.

#### Módulos disponibles:

- **🔑 Keys Tester**: Configura y prueba tus llaves de API (Google, OpenAI, etc.).
- **🧩 Visual Builder**: (Próximamente) Crea scripts arrastrando bloques como en Scratch.
- **📝 Script Manager**: (Próximamente) Edita y ejecuta tus scripts existentes.

---
*Desarrollado con ❤️ para la comunidad de Browser Use.*
""")
