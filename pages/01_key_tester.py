"""
Tester de llaves (Google Gemini y OpenRouter).
Permite validar rapidamente si una API key es válida y si el modelo responde.
No guarda tus llaves en disco.
"""

from __future__ import annotations

import os
import time
from typing import Optional, Tuple

import requests
import streamlit as st


def test_google_key(api_key: str, model: str = "gemini-1.5-flash") -> Tuple[bool, str]:
    """
    Prueba simple: countTokens en el modelo indicado.
    Devuelve (ok, mensaje).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "ping"}]}]}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return True, "OK"
        return False, f"{resp.status_code} - {resp.text}"
    except Exception as exc:  # network/error
        return False, f"Error: {exc}"


def test_openrouter_key(api_key: str, model: str = "meta-llama/llama-3-8b-instruct:free") -> Tuple[bool, str]:
    """
    Prueba: llamar a /api/v1/chat/completions con un prompt mínimo.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Browser-Use-Studio",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 4,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            return True, "OK"
        return False, f"{resp.status_code} - {resp.text}"
    except Exception as exc:  # network/error
        return False, f"Error: {exc}"


st.set_page_config(page_title="Tester de llaves", layout="wide")
st.title("Tester de llaves (Google / OpenRouter)")

with st.expander("Instrucciones", expanded=True):
    st.markdown(
        """
        - Nada se guarda en disco; las llaves viven solo en la sesión de Streamlit.
        - Se hace una llamada mínima: `countTokens` en Gemini, chat de 1 token en OpenRouter.
        - Usa un modelo libre/ligero para evitar costos.
        """
    )

tab_google, tab_openrouter = st.tabs(["Google Gemini", "OpenRouter"])

with tab_google:
    st.subheader("Google Gemini")
    default_models = ["gemini-1.5-flash", "gemini-1.5-flash-002", "gemini-1.5-pro"]
    model = st.selectbox("Modelo", default_models, index=0)
    key_input = st.text_input("API Key (no se guarda)", type="password", key="google_key_input")
    if st.button("Probar Gemini", type="primary"):
        if not key_input:
            st.error("Ingresa la API key de Google.")
        else:
            with st.spinner("Probando clave Gemini..."):
                ok, msg = test_google_key(key_input.strip(), model=model)
                if ok:
                    st.success(f"✅ Key válida para {model}: {msg}")
                else:
                    st.error(f"❌ Falló: {msg}")

with tab_openrouter:
    st.subheader("OpenRouter")
    default_models = [
        "meta-llama/llama-3-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    model = st.selectbox("Modelo", default_models, index=0, key="or_model")
    key_input = st.text_input("API Key (no se guarda)", type="password", key="or_key_input")
    if st.button("Probar OpenRouter", type="primary", key="btn_or"):
        if not key_input:
            st.error("Ingresa la API key de OpenRouter.")
        else:
            with st.spinner("Probando clave OpenRouter..."):
                ok, msg = test_openrouter_key(key_input.strip(), model=model)
                if ok:
                    st.success(f"✅ Key válida para {model}: {msg}")
                else:
                    st.error(f"❌ Falló: {msg}")
