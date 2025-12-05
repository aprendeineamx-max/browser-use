import streamlit as st
import os
from dotenv import load_dotenv, set_key
from browser_use.llm.google.chat import ChatGoogle
from langchain_core.messages import HumanMessage
import asyncio

# Page Config
st.set_page_config(page_title="Key Tester", page_icon="🔑", layout="wide")
st.title("🔑 API Keys Manager & Tester")

# Load Env
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(ENV_PATH)

def test_google_key(api_key):
    try:
        # Usar gemini-2.0-flash como validado
        llm = ChatGoogle(model="gemini-2.0-flash", api_key=api_key)
        # Simple invoke using HumanMessage object
        async def run_test():
            msg = HumanMessage(content="Hello")
            return await llm.ainvoke([msg])
        
        response = asyncio.run(run_test())
        return True, str(response.content)
    except Exception as e:
        return False, str(e)

# --- KEY MANAGEMENT ---
st.markdown("### 1. Gestión de Keys")
st.info(f"Archivo .env: `{ENV_PATH}`")

# Helper to get all keys from env that match a provider
def get_keys(prefix):
    return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

# Generic Key Adder
with st.expander("➕ Agregar Nueva Key", expanded=True):
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        provider = st.selectbox("Proveedor", ["GOOGLE", "OPENROUTER", "OPENAI", "ANTHROPIC", "GROQ"])
    with col2:
        new_key_value = st.text_input("Valor de la API Key", type="password")
    with col3:
        alias = st.text_input("Alias (opcional)", placeholder="Ej: Pablo")
    
    if st.button("Guardar Key"):
        if not new_key_value:
            st.error("Falta el valor de la key")
        else:
            key_name = f"{provider}_API_KEY"
            if alias:
                key_name += f"_{alias.upper()}"
            
            set_key(ENV_PATH, key_name, new_key_value)
            st.success(f"Guardada: {key_name}")
            st.rerun()

# --- KEY TESTING ---
st.markdown("### 2. Verificar Conectividad")

tab1, tab2, tab3 = st.tabs(["Google Gemini", "Open Router", "Otros"])

with tab1:
    st.subheader("Google Gemini Tester")
    google_keys = get_keys("GOOGLE_API_KEY")
    
    if not google_keys:
        st.warning("No hay keys de Google configuradas.")
    else:
        selected_key_name = st.selectbox("Selecciona Key:", list(google_keys.keys()))
        selected_key_val = google_keys[selected_key_name]
        
        if st.button(f"Probar {selected_key_name}"):
             with st.spinner("Conectando con Gemini 2.0 Flash..."):
                success, msg = test_google_key(selected_key_val)
                if success:
                    st.success(f"✅ Éxito! Respuesta: {msg}")
                else:
                    st.error(f"❌ Error: {msg}")

with tab2:
    st.subheader("Open Router Tester")
    or_keys = get_keys("OPENROUTER_API_KEY")
    if not or_keys:
        st.warning("No hay keys de OpenRouter.")
    else:
        st.write(list(or_keys.keys()))
        st.info("🚧 Test de OpenRouter en construcción (requiere librería OpenAI compatible).")

with tab3:
    st.write("Otros proveedores...")
