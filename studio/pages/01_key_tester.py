import os
from typing import Dict, List, Tuple

import requests
import streamlit as st

LOG_FILE = "Registro_de_logs.txt"


def log_line(msg: str) -> None:
    try:
        import time

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[KeyTester][{ts}] {msg}\n")
    except Exception:
        pass


def tail_key(value: str) -> str:
    return value[-4:] if value else "????"


def detect_keys() -> Dict[str, List[Tuple[str, str]]]:
    env = os.environ
    providers: Dict[str, List[Tuple[str, str]]] = {"google": [], "groq": [], "openrouter": []}
    for name, val in env.items():
        low = name.lower()
        if "groq_api_key" in low:
            providers["groq"].append((name, val))
        if "openrouter_api_key" in low:
            providers["openrouter"].append((name, val))
        if "google_api_key" in low:
            providers["google"].append((name, val))
    return providers


def label_cost(model: str) -> str:
    freebies = [
        "llama-3.1-8b",
        "llama-3.3-70b",
        "gemini-1.5-flash",
        "gpt-4o-mini",
        "mixtral-8x7b",
    ]
    return "[FREE]" if any(free in model for free in freebies) else "[$$$]"


def fetch_models(provider: str, api_key: str) -> List[str]:
    models: List[str] = []
    try:
        if provider == "groq":
            url = "https://api.groq.com/openai/v1/models"
            log_line(f"Llamando a {url}")
            resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            if resp.ok:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/models"
            log_line(f"Llamando a {url}")
            resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            if resp.ok:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
        elif provider == "google":
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            log_line(f"Llamando a {url}")
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                raw = [m.get("name", "") for m in data.get("models", [])]
                # names come as "models/gemini-1.5-flash-002"
                models = [name.split("/")[-1] for name in raw if name]
    except Exception as exc:
        log_line(f"Error obteniendo modelos {provider}: {exc}")
    return models


def ping_groq(api_key: str) -> Tuple[bool, str]:
    url = "https://api.groq.com/openai/v1/models"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=8)
        log_line(f"Ping Groq -> {resp.status_code}")
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        log_line(f"Ping Groq error: {exc}")
        return False, str(exc)


def ping_openrouter(api_key: str) -> Tuple[bool, str]:
    url = "https://openrouter.ai/api/v1/models"
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=8)
        log_line(f"Ping OpenRouter -> {resp.status_code}")
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        log_line(f"Ping OpenRouter error: {exc}")
        return False, str(exc)


def ping_gemini(api_key: str) -> Tuple[bool, str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(url, timeout=8)
        log_line(f"Ping Gemini -> {resp.status_code}")
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except Exception as exc:
        log_line(f"Ping Gemini error: {exc}")
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
Selecciona una key detectada, elige modelo (lista dinámica desde las APIs) y conversa para validar latencia/calidad.
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
    api_val = os.environ.get(sel_key, "") if sel_key else ""
    models = fetch_models("google", api_val) if api_val else []
    model_labels = [f"{label_cost(m)} {m}" for m in models] or ["(sin modelos)"]
    model_value = models[0] if models else ""
    sel_model = st.selectbox("Modelo", model_labels, index=0)
    if model_labels:
        model_value = sel_model.split(" ", 1)[1] if " " in sel_model else sel_model
    st.write(f"Usando key {sel_key} (…{tail_key(api_val)})")

    if st.button("Verificar key Google"):
        ok, info = ping_gemini(api_val)
        st.success(f"Key OK ({info})" if ok else f"Key falló ({info})")

    st.divider()
    st.write("Chat de prueba")
    for message in st.session_state.get("google_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Pregunta a Gemini (flash es free)"):
        msgs = st.session_state.get("google_messages", [])
        msgs.append({"role": "user", "content": prompt})
        st.session_state["google_messages"] = msgs
        with st.spinner("Consultando Gemini..."):
            try:
                reply = chat_gemini(api_val, model_value, [{"role": "user", "content": prompt}])
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
    api_val = os.environ.get(sel_key, "") if sel_key else ""
    models = fetch_models("groq", api_val) if api_val else []
    model_labels = [f"{label_cost(m)} {m}" for m in models] or ["(sin modelos)"]
    model_value = models[0] if models else ""
    sel_model = st.selectbox("Modelo", model_labels, index=0)
    if model_labels:
        model_value = sel_model.split(" ", 1)[1] if " " in sel_model else sel_model
    st.write(f"Usando key {sel_key} (…{tail_key(api_val)})")

    if st.button("Verificar key Groq"):
        ok, info = ping_groq(api_val)
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
                reply = chat_groq(api_val, model_value, [{"role": "user", "content": prompt}])
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
    api_val = os.environ.get(sel_key, "") if sel_key else ""
    models = fetch_models("openrouter", api_val) if api_val else []
    model_labels = [f"{label_cost(m)} {m}" for m in models] or ["(sin modelos)"]
    model_value = models[0] if models else ""
    sel_model = st.selectbox("Modelo", model_labels, index=0)
    if model_labels:
        model_value = sel_model.split(" ", 1)[1] if " " in sel_model else sel_model
    st.write(f"Usando key {sel_key} (…{tail_key(api_val)})")

    if st.button("Verificar key OpenRouter"):
        ok, info = ping_openrouter(api_val)
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
                reply = chat_openrouter(api_val, model_value, [{"role": "user", "content": prompt}])
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
