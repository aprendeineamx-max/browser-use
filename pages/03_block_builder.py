"""
Builder visual sencillo (tipo bloques) para generar scripts de automatización.
- Permite añadir pasos básicos: navegar, scroll, click (por selector CSS), escribir texto.
- Genera un script .py en `Scripts Automaticos/`.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

SCRIPTS_DIR = Path("Scripts Automaticos")
SCRIPTS_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="Block Builder", layout="wide")
st.title("Block Builder (beta)")

with st.expander("Instrucciones", expanded=True):
    st.markdown(
        """
        - Añade bloques de acciones (navegar, scroll, click, escribir).
        - Ajusta los parámetros de cada bloque.
        - Genera un script Python en `Scripts Automaticos/`.
        """
    )


def init_state():
    if "blocks" not in st.session_state:
        st.session_state.blocks: List[Dict[str, Any]] = []


init_state()


def add_block(action_type: str):
    defaults = {
        "navigate": {"url": "https://example.com", "new_tab": False},
        "scroll": {"delta_y": 300, "delta_x": 0},
        "click": {"selector": "a[href]", "description": "primer enlace"},
        "input": {"selector": "input", "text": "texto a escribir"},
    }
    st.session_state.blocks.append({"type": action_type, "params": defaults[action_type]})


col_add1, col_add2, col_add3, col_add4 = st.columns(4)
with col_add1:
    if st.button("Añadir navegar"):
        add_block("navigate")
with col_add2:
    if st.button("Añadir scroll"):
        add_block("scroll")
with col_add3:
    if st.button("Añadir click"):
        add_block("click")
with col_add4:
    if st.button("Añadir input"):
        add_block("input")

st.markdown("---")

# Editar bloques
new_blocks: List[Dict[str, Any]] = []
for idx, block in enumerate(st.session_state.blocks):
    st.write(f"Bloque {idx+1}: {block['type']}")
    if block["type"] == "navigate":
        url = st.text_input(f"URL #{idx+1}", value=block["params"]["url"], key=f"nav_url_{idx}")
        new_tab = st.checkbox(f"New tab #{idx+1}", value=block["params"]["new_tab"], key=f"nav_tab_{idx}")
        new_blocks.append({"type": "navigate", "params": {"url": url, "new_tab": new_tab}})
    elif block["type"] == "scroll":
        dy = st.number_input(f"delta_y #{idx+1}", value=block["params"]["delta_y"], step=50, key=f"scr_dy_{idx}")
        dx = st.number_input(f"delta_x #{idx+1}", value=block["params"]["delta_x"], step=50, key=f"scr_dx_{idx}")
        new_blocks.append({"type": "scroll", "params": {"delta_y": dy, "delta_x": dx}})
    elif block["type"] == "click":
        selector = st.text_input(f"Selector CSS #{idx+1}", value=block["params"]["selector"], key=f"clk_sel_{idx}")
        desc = st.text_input(f"Descripcion #{idx+1}", value=block["params"]["description"], key=f"clk_desc_{idx}")
        new_blocks.append({"type": "click", "params": {"selector": selector, "description": desc}})
    elif block["type"] == "input":
        selector = st.text_input(f"Selector input #{idx+1}", value=block["params"]["selector"], key=f"in_sel_{idx}")
        text = st.text_input(f"Texto #{idx+1}", value=block["params"]["text"], key=f"in_text_{idx}")
        new_blocks.append({"type": "input", "params": {"selector": selector, "text": text}})
    st.markdown("---")

st.session_state.blocks = new_blocks

# Generar script
st.subheader("Generar script")
file_name = st.text_input("Nombre del script (.py)", value="custom_script.py")


def render_block_py(block: Dict[str, Any]) -> str:
    t = block["type"]
    p = block["params"]
    if t == "navigate":
        return f"{{'navigate': {{'url': '{p['url']}', 'new_tab': {str(p['new_tab']).lower()}}}}}"
    if t == "scroll":
        return f"{{'scroll': {{'delta_y': {p['delta_y']}, 'delta_x': {p['delta_x']}}}}}"
    if t == "click":
        return (
            f"{{'click': {{'selector': \"{p['selector']}\", "
            f"'description': \"{p['description']}\"}}}}"
        )
    if t == "input":
        return (
            f"{{'send_keys': {{'selector': \"{p['selector']}\", "
            f"'text': \"{p['text']}\"}}}}"
        )
    return "# bloque desconocido"


def generate_script_py(blocks: List[Dict[str, Any]]) -> str:
    actions_py = ",\n        ".join(render_block_py(b) for b in blocks)
    return f"""from browser_use import Agent, Browser
from browser_use.llm import ChatGroq
import asyncio

async def main():
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
    browser = Browser(headless=False, keep_alive=True)

    initial_actions = [
        {actions_py}
    ]

    task = "Ejecuta las acciones iniciales y finaliza."

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=False,
        initial_actions=initial_actions,
        max_steps=10,
    )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
"""


if st.button("Previsualizar script"):
    if not st.session_state.blocks:
        st.warning("Agrega al menos un bloque.")
    else:
        st.code(generate_script_py(st.session_state.blocks), language="python")

if st.button("Guardar en Scripts Automaticos/"):
    if not file_name.endswith(".py"):
        st.error("El nombre debe terminar en .py")
    elif not st.session_state.blocks:
        st.error("Agrega al menos un bloque.")
    else:
        target = SCRIPTS_DIR / file_name
        target.write_text(generate_script_py(st.session_state.blocks), encoding="utf-8")
        st.success(f"Guardado en {target}")
