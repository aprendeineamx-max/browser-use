import streamlit as st
import os
from dotenv import load_dotenv, set_key
from browser_use.llm.google.chat import ChatGoogle
import asyncio

# Page Config
st.set_page_config(page_title="Key Tester", page_icon="🔑", layout="wide")
st.title("🔑 API Keys Tester")

# Load Env
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(ENV_PATH)

def test_google_key(api_key):
    try:
        # Usar gemini-2.0-flash como validado
        llm = ChatGoogle(model="gemini-2.0-flash", api_key=api_key)
        # Simple invoke (async wrapper)
        async def run_test():
            return await llm.ainvoke([{"role": "user", "content": "Hello"}])
        
        response = asyncio.run(run_test())
        return True, str(response.content)
    except Exception as e:
        return False, str(e)

st.markdown("### 1. Configuración de Keys")
st.info(f"Leyendo archivo .env en: `{ENV_PATH}`")

# Google Configuration
col1, col2 = st.columns([3, 1])
with col1:
    google_key = st.text_input("GOOGLE_API_KEY", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
with col2:
    if st.button("Guardar Google Key"):
        set_key(ENV_PATH, "GOOGLE_API_KEY", google_key)
        st.success("Guardado!")
        st.rerun()

# Test Google Section
st.markdown("---")
st.markdown("### 2. Prueba de Conectividad")

st.subheader("Google Gemini")
if st.button("Probar Gemini 2.0 Flash"):
    if not google_key:
        st.error("Falta la Key")
    else:
        with st.spinner("Probando conexión con Google..."):
            success, message = test_google_key(google_key)
            if success:
                st.success(f"✅ Conexión Exitosa!\nRespuesta: {message}")
            else:
                st.error(f"❌ Falló la conexión:\n{message}")

# Placeholder for other keys
st.markdown("---")
st.subheader("Otros Proveedores (Próximamente)")
st.caption("Implementaremos OpenAI y Anthropic en la siguiente actualización.")
