import os
import time
from typing import Dict, List, Tuple

import requests
import streamlit as st

# Model lists con etiquetas
GEMINI_MODELS = [
    ("gemini-1.5-flash-002", "[FREE] gemini-1.5-flash-002"),
    ("gemini-1.5-pro-exp-0827", "[$$$] gemini-1.5-pro-exp"),
]
GROQ_MODELS = [
    ("llama-3.3-70b-versatile", "[FREE] llama-3.3-70b-versatile"),
    ("llama-3.1-8b-instant", "[FREE] llama-3.1-8b-instant"),
    ("mixtral-8x7b-32768", "[FREE] mixtral-8x7b"),
]
OPENROUTER_MODELS = [
    ("meta-llama/llama-3.3-70b-instruct", "[FREE] llama-3.3-70b-instruct"),
    ("gpt-4o-mini", "[FREE] gpt-4o-mini"),
    ("gpt-4o", "[$$$] gpt-4o"),
]


def tail_key(value: str) -> str:
    return value[-4:] if value else "????"


def detect_keys() -> Dict[str, List[Tuple[str, str]]]:
    """
    Devuelve diccionario por proveedor -> lista de (env_var, value).
    """
    env = os.environ
    providers: Dict[str, List[Tuple[str, str]]] = {
        "google": [],
        "groq": [],
        "openrouter": [],
    }
    for name, val in env.items():
        low = name.lower()
        if "groq_api_key" in low:
            providers["groq"].append((name, val))
        if "openrouter_api_key" in low:
            providers["openrouter"].append((name, val))
        if "google_api_key" in low:
            providers["google"].append((name, val))
    return providers


def ping_groq(api_key: str) -> Tuple[bool, str]:
    url = "https://api.groq.com/openai/v1/models"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=8)
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


def ping_openrouter(api_key: str) -> Tuple[bool, str]:
    url = "https://openrouter.ai/api/v1/models"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=8)
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


def ping_gemini(api_key: str) -> Tuple[bool, str]:
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    try:
        resp = requests.get(url, timeout=8)
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        return False, str(exc)


def chat_openrouter(api_key: str, model: str, messages: List[Dict[str, str]]) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model, "messages": messages, "max_tokens": 120}
    resp = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def chat_groq(api_key: str, model: str, messages: List[Dict[str, str]]) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {"model": model, "messages": messages, "max_tokens": 120}
    resp = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def chat_gemini(api_key: str, model: str, messages: List[Dict[str, str]]) -> str:
    # Usamos la API de countTokens como ping ligero; para chat, la API requiere safety settings.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    parts = [{"text": m["content"]} for m in messages]
    payload = {"contents": [{"role": "user", "parts": parts}]}
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")


# ---------------- UI ----------------

st.set_page_config(page_title="Centro de Comando de Modelos", layout="wide")
st.title("Centro de Comando de Modelos (Tester de Llaves)")

st.markdown(
    """
Selecciona una key detectada, elige modelo con etiqueta de costo, y conversa para validar latencia/calidad.
Botón "Verificar Todas" hace un ping rápido 1-token por proveedor.
"""
)

providers = detect_keys()

with st.expander("Keys detectadas"):
    for prov, lst in providers.items():
        st.write(f"**{prov.upper()}** ({len(lst)})")
        for name, val in lst:
            st.write(f"- {name} (…{tail_key(val)})")

tab_google, tab_groq, tab_or = st.tabs(["Google Gemini", "Groq", "OpenRouter"])

# Google tab
with tab_google:
    keys = providers.get("google", [])
    key_names = [k for k, _ in keys]
    sel_key = st.selectbox("API Key (Google)", key_names, index=0 if key_names else None)
    sel_model = st.selectbox("Modelo", [label for _, label in GEMINI_MODELS])
    model_value = [v for v, lbl in GEMINI_MODELS if lbl == sel_model][0] if GEMINI_MODELS else ""
    st.write(f"Usando key {sel_key} (…{tail_key(os.environ.get(sel_key,''))})")

    if st.button("Verificar key Google"):
        ok, info = ping_gemini(os.environ.get(sel_key, ""))
        st.success(f"Key OK ({info})" if ok else f"Key falló ({info})")

    st.divider()
    st.write("Chat de prueba")
    for message in st.session_state.get("google_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Pregunta a Gemini (FREE = flash)"):
        msgs = st.session_state.get("google_messages", [])
        msgs.append({"role": "user", "content": prompt})
        st.session_state["google_messages"] = msgs
        with st.spinner("Consultando Gemini..."):
            try:
                reply = chat_gemini(os.environ.get(sel_key, ""), model_value, [{"role": "user", "content": prompt}])
            except Exception as exc:
                reply = f"Error: {exc}"
        msgs.append({"role": "assistant", "content": reply})
        st.session_state["google_messages"] = msgs
        with st.chat_message("assistant"):
            st.markdown(reply)

# Groq tab
with tab_groq:
    keys = providers.get("groq", [])
    key_names = [k for k, _ in keys]
    sel_key = st.selectbox("API Key (Groq)", key_names, index=0 if key_names else None)
    sel_model = st.selectbox("Modelo", [label for _, label in GROQ_MODELS])
    model_value = [v for v, lbl in GROQ_MODELS if lbl == sel_model][0] if GROQ_MODELS else ""
    st.write(f"Usando key {sel_key} (…{tail_key(os.environ.get(sel_key,''))})")

    if st.button("Verificar key Groq"):
        ok, info = ping_groq(os.environ.get(sel_key, ""))
        st.success(f"Key OK ({info})" if ok else f"Key falló ({info})")

    st.divider()
    st.write("Chat de prueba")
    for message in st.session_state.get("groq_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Pregunta a Groq (Llama3 free)"):
        msgs = st.session_state.get("groq_messages", [])
        msgs.append({"role": "user", "content": prompt})
        st.session_state["groq_messages"] = msgs
        with st.spinner("Consultando Groq..."):
            try:
                reply = chat_groq(os.environ.get(sel_key, ""), model_value, [{"role": "user", "content": prompt}])
            except Exception as exc:
                reply = f"Error: {exc}"
        msgs.append({"role": "assistant", "content": reply})
        st.session_state["groq_messages"] = msgs
        with st.chat_message("assistant"):
            st.markdown(reply)

# OpenRouter tab
with tab_or:
    keys = providers.get("openrouter", [])
    key_names = [k for k, _ in keys]
    sel_key = st.selectbox("API Key (OpenRouter)", key_names, index=0 if key_names else None)
    sel_model = st.selectbox("Modelo", [label for _, label in OPENROUTER_MODELS])
    model_value = [v for v, lbl in OPENROUTER_MODELS if lbl == sel_model][0] if OPENROUTER_MODELS else ""
    st.write(f"Usando key {sel_key} (…{tail_key(os.environ.get(sel_key,''))})")

    if st.button("Verificar key OpenRouter"):
        ok, info = ping_openrouter(os.environ.get(sel_key, ""))
        st.success(f"Key OK ({info})" if ok else f"Key falló ({info})")

    st.divider()
    st.write("Chat de prueba")
    for message in st.session_state.get("or_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Pregunta a OpenRouter"):
        msgs = st.session_state.get("or_messages", [])
        msgs.append({"role": "user", "content": prompt})
        st.session_state["or_messages"] = msgs
        with st.spinner("Consultando OpenRouter..."):
            try:
                reply = chat_openrouter(os.environ.get(sel_key, ""), model_value, [{"role": "user", "content": prompt}])
            except Exception as exc:
                reply = f"Error: {exc}"
        msgs.append({"role": "assistant", "content": reply})
        st.session_state["or_messages"] = msgs
        with st.chat_message("assistant"):
            st.markdown(reply)


st.divider()
st.subheader("Verificar Todas las Keys detectadas")

if st.button("Verificar Todas"):
    summary = []
    for name, val in providers.get("google", []):
        ok, info = ping_gemini(val)
        summary.append(f"Google {name} (…{tail_key(val)}): {'OK' if ok else 'FAIL'} {info}")
    for name, val in providers.get("groq", []):
        ok, info = ping_groq(val)
        summary.append(f"Groq {name} (…{tail_key(val)}): {'OK' if ok else 'FAIL'} {info}")
    for name, val in providers.get("openrouter", []):
        ok, info = ping_openrouter(val)
        summary.append(f"OpenRouter {name} (…{tail_key(val)}): {'OK' if ok else 'FAIL'} {info}")
    st.code("\n".join(summary) or "No hay keys detectadas", language="text")
