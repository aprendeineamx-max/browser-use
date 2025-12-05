import streamlit as st
import os
from dotenv import load_dotenv
from browser_use.llm.google.chat import ChatGoogle
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import asyncio

st.set_page_config(page_title="Chat Playground", page_icon="💬", layout="wide")
st.title("💬 Chat Playground")

# Load Env
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(ENV_PATH)

def get_keys(prefix):
    return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Configuración")
    provider = st.selectbox("Proveedor", ["Google Gemini", "OpenRouter", "OpenAI"])
    
    selected_key_val = None
    model_name = ""
    
    if provider == "Google Gemini":
        keys = get_keys("GOOGLE_API_KEY")
        if not keys:
            st.error("No hay keys de Google.")
        else:
            key_name = st.selectbox("Selecciona Key", list(keys.keys()))
            selected_key_val = keys[key_name]
            model_name = st.selectbox("Modelo", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
            
    elif provider == "OpenRouter":
        keys = get_keys("OPENROUTER_API_KEY")
        if not keys:
            st.error("No hay keys de OpenRouter.")
        else:
            key_name = st.selectbox("Selecciona Key", list(keys.keys()))
            selected_key_val = keys[key_name]
            # Common OpenRouter models
            model_name = st.selectbox("Modelo", [
                "google/gemini-2.0-flash-exp:free",
                "meta-llama/llama-3.1-70b-instruct:free",
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o"
            ])

    elif provider == "OpenAI":
        keys = get_keys("OPENAI_API_KEY")
        if not keys:
            st.warning("No hay keys de OpenAI.")
        else:
            key_name = st.selectbox("Selecciona Key", list(keys.keys()))
            selected_key_val = keys[key_name]
            model_name = st.selectbox("Modelo", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu mensaje..."):
    if not selected_key_val:
        st.error("Por favor selecciona una Key válida primero.")
    else:
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.chat_message("assistant"):
            try:
                response_text = ""
                
                if provider == "Google Gemini":
                    llm = ChatGoogle(model=model_name, api_key=selected_key_val)
                    async def run_gemini():
                        msg = HumanMessage(content=prompt)
                        return await llm.ainvoke([msg])
                    
                    res = asyncio.run(run_gemini())
                    response_text = res.content
                    
                elif provider == "OpenRouter":
                    llm = ChatOpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=selected_key_val,
                        model=model_name
                    )
                    res = llm.invoke([HumanMessage(content=prompt)])
                    response_text = res.content

                elif provider == "OpenAI":
                    llm = ChatOpenAI(api_key=selected_key_val, model=model_name)
                    res = llm.invoke([HumanMessage(content=prompt)])
                    response_text = res.content

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
