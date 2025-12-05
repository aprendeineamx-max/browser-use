"""
Block Builder (avanzado)
- Nuevos tipos de bloque: click/input por CSS o XPath, scroll/reintentos.
- Datos externos: CSV/Excel/JSON para iterar tareas.
- Configuración de instancia: proveedor/modelo/API key en el script generado.
- Edición de scripts existentes (texto) desde Scripts Automaticos/.

Nota: El builder genera scripts orientados a LLM (ChatGroq/OpenRouter/Google) con instrucciones
detalladas y bloques convertidos a texto. Usa initial_actions solo para navegar/scroll determinista.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

SCRIPTS_DIR = Path("Scripts Automaticos")
SCRIPTS_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="Block Builder", layout="wide")
st.title("Block Builder (avanzado)")

with st.expander("Instrucciones", expanded=True):
    st.markdown(
        """
        - Añade bloques (navegar, scroll, click/input por CSS/XPath, reintentos).
        - Opcional: define una fuente de datos (CSV/Excel/JSON) para iterar.
        - Configura proveedor/modelo/API key para el script resultante.
        - Genera un `.py` en `Scripts Automaticos/`.
        """
    )


# -------------------------
# Estado inicial
# -------------------------
def init_state():
    if "blocks" not in st.session_state:
        st.session_state.blocks: List[Dict[str, Any]] = []
    if "data_cfg" not in st.session_state:
        st.session_state.data_cfg = {
            "source": "none",
            "path": "",
            "column": "",
            "json_field": "",
            "var_name": "item",
        }
    if "provider_cfg" not in st.session_state:
        st.session_state.provider_cfg = {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "api_key": "",
        }


init_state()


# -------------------------
# Helpers
# -------------------------
def add_block(block_type: str):
    defaults = {
        "navigate": {"url": "https://example.com", "new_tab": False},
        "scroll": {"delta_y": 300, "delta_x": 0},
        "click_css": {"selector": "a[href]", "description": "clic CSS"},
        "click_xpath": {"selector": "//a", "description": "clic XPath"},
        "input_css": {"selector": "input", "text": "texto a escribir"},
        "input_xpath": {"selector": "//input", "text": "texto a escribir"},
        "retry": {"retries": 2, "wait_seconds": 2, "note": "reintentar si falla"},
    }
    st.session_state.blocks.append({"type": block_type, "params": defaults[block_type]})


def render_block_text(block: Dict[str, Any], idx: int) -> str:
    t = block["type"]
    p = block["params"]
    if t == "navigate":
        return f"{idx}. Navega a {p['url']} (nueva pestaña: {p['new_tab']})."
    if t == "scroll":
        return f"{idx}. Haz scroll (delta_y={p['delta_y']}, delta_x={p['delta_x']})."
    if t == "click_css":
        return f"{idx}. Haz click en CSS '{p['selector']}' ({p['description']})."
    if t == "click_xpath":
        return f"{idx}. Haz click en XPath '{p['selector']}' ({p['description']})."
    if t == "input_css":
        return f"{idx}. Escribe \"{p['text']}\" en CSS '{p['selector']}'."
    if t == "input_xpath":
        return f"{idx}. Escribe \"{p['text']}\" en XPath '{p['selector']}'."
    if t == "retry":
        return f"{idx}. Reintenta hasta {p['retries']} veces, espera {p['wait_seconds']}s ({p['note']})."
    return f"{idx}. Paso sin descripcion."


# -------------------------
# UI: agregar bloques
# -------------------------
col_add = st.columns(7)
buttons = [
    ("Navegar", "navigate"),
    ("Scroll", "scroll"),
    ("Click CSS", "click_css"),
    ("Click XPath", "click_xpath"),
    ("Input CSS", "input_css"),
    ("Input XPath", "input_xpath"),
    ("Retry", "retry"),
]
for (label, btype), col in zip(buttons, col_add):
    if col.button(f"Añadir {label}"):
        add_block(btype)

st.markdown("---")

# -------------------------
# UI: editar bloques
# -------------------------
new_blocks: List[Dict[str, Any]] = []
for idx, block in enumerate(st.session_state.blocks):
    st.write(f"Bloque {idx+1}: {block['type']}")
    t = block["type"]
    p = block["params"]
    if t == "navigate":
        url = st.text_input(f"URL #{idx+1}", value=p["url"], key=f"nav_url_{idx}")
        new_tab = st.checkbox(f"New tab #{idx+1}", value=p["new_tab"], key=f"nav_tab_{idx}")
        new_blocks.append({"type": "navigate", "params": {"url": url, "new_tab": new_tab}})
    elif t == "scroll":
        dy = st.number_input(f"delta_y #{idx+1}", value=p["delta_y"], step=50, key=f"scr_dy_{idx}")
        dx = st.number_input(f"delta_x #{idx+1}", value=p["delta_x"], step=50, key=f"scr_dx_{idx}")
        new_blocks.append({"type": "scroll", "params": {"delta_y": dy, "delta_x": dx}})
    elif t == "click_css":
        sel = st.text_input(f"Selector CSS #{idx+1}", value=p["selector"], key=f"ccss_{idx}")
        desc = st.text_input(f"Descripcion #{idx+1}", value=p["description"], key=f"ccss_desc_{idx}")
        new_blocks.append({"type": "click_css", "params": {"selector": sel, "description": desc}})
    elif t == "click_xpath":
        sel = st.text_input(f"Selector XPath #{idx+1}", value=p["selector"], key=f"cxp_{idx}")
        desc = st.text_input(f"Descripcion #{idx+1}", value=p["description"], key=f"cxp_desc_{idx}")
        new_blocks.append({"type": "click_xpath", "params": {"selector": sel, "description": desc}})
    elif t == "input_css":
        sel = st.text_input(f"Selector CSS #{idx+1}", value=p["selector"], key=f"icss_{idx}")
        text = st.text_input(f"Texto #{idx+1}", value=p["text"], key=f"icss_text_{idx}")
        new_blocks.append({"type": "input_css", "params": {"selector": sel, "text": text}})
    elif t == "input_xpath":
        sel = st.text_input(f"Selector XPath #{idx+1}", value=p["selector"], key=f"ixp_{idx}")
        text = st.text_input(f"Texto #{idx+1}", value=p["text"], key=f"ixp_text_{idx}")
        new_blocks.append({"type": "input_xpath", "params": {"selector": sel, "text": text}})
    elif t == "retry":
        retries = st.number_input(f"Reintentos #{idx+1}", value=p["retries"], step=1, min_value=0, key=f"rtry_{idx}")
        wait = st.number_input(f"Espera (s) #{idx+1}", value=p["wait_seconds"], step=1, min_value=0, key=f"rwait_{idx}")
        note = st.text_input(f"Nota #{idx+1}", value=p["note"], key=f"rnote_{idx}")
        new_blocks.append({"type": "retry", "params": {"retries": retries, "wait_seconds": wait, "note": note}})
    st.markdown("---")

st.session_state.blocks = new_blocks

# -------------------------
# Datos externos
# -------------------------
st.subheader("Datos externos (opcional)")
data_cfg = st.session_state.data_cfg
data_cfg["source"] = st.selectbox("Fuente de datos", ["none", "csv", "excel", "json"], index=["none", "csv", "excel", "json"].index(data_cfg["source"]))
if data_cfg["source"] != "none":
    data_cfg["path"] = st.text_input("Ruta del archivo (CSV/Excel/JSON)", value=data_cfg["path"])
    if data_cfg["source"] in ("csv", "excel"):
        data_cfg["column"] = st.text_input("Columna a usar", value=data_cfg["column"])
    if data_cfg["source"] == "json":
        data_cfg["json_field"] = st.text_input("Campo/llave a usar", value=data_cfg["json_field"])
    data_cfg["var_name"] = st.text_input("Nombre de variable en prompt", value=data_cfg["var_name"] or "item")

    # Indicador visual de datos cargados
    rows_detected = None
    if data_cfg["path"]:
        try:
            path_obj = Path(data_cfg["path"])
            if path_obj.exists():
                if data_cfg["source"] == "csv":
                    import pandas as pd
                    rows_detected = len(pd.read_csv(path_obj))
                elif data_cfg["source"] == "excel":
                    import pandas as pd
                    rows_detected = len(pd.read_excel(path_obj))
                elif data_cfg["source"] == "json":
                    import json
                    with path_obj.open("r", encoding="utf-8") as f:
                        rows_detected = len(json.load(f))
        except Exception:
            rows_detected = None
    if rows_detected is not None:
        st.info(f"Modo de Datos Activo: {rows_detected} filas detectadas", icon="ℹ️")
st.session_state.data_cfg = data_cfg

# -------------------------
# Configuracion de instancia
# -------------------------
st.subheader("Configuración de instancia (proveedor/modelo/API key)")
provider_cfg = st.session_state.provider_cfg
provider_cfg["provider"] = st.selectbox("Proveedor", ["groq", "openrouter", "google"], index=["groq", "openrouter", "google"].index(provider_cfg["provider"]))
provider_cfg["model"] = st.text_input("Modelo", value=provider_cfg["model"])
provider_cfg["api_key"] = st.text_input("API Key (opcional en claro, no se guarda)", value=provider_cfg["api_key"], type="password")
st.session_state.provider_cfg = provider_cfg

# -------------------------
# Cargar script existente (texto)
# -------------------------
st.subheader("Cargar script existente")
existing = sorted(p.name for p in SCRIPTS_DIR.glob("*.py"))
selected_script = st.selectbox("Script", ["(ninguno)"] + existing)
loaded_code = ""
if selected_script != "(ninguno)":
    loaded_code = (SCRIPTS_DIR / selected_script).read_text(encoding="utf-8")
st.text_area("Contenido (solo texto, no parsea a bloques)", value=loaded_code, height=200, key="loaded_code")

# -------------------------
# Generar script
# -------------------------
st.subheader("Generar script")
file_name = st.text_input("Nombre del script (.py)", value="custom_script.py")


def build_task_text(blocks: List[Dict[str, Any]]) -> str:
    lines = [render_block_text(b, i + 1) for i, b in enumerate(blocks)]
    return "\n".join(lines)


def render_llm_import(provider: str) -> str:
    if provider == "groq":
        return "from browser_use.llm import ChatGroq"
    if provider == "openrouter":
        return "from browser_use.llm import ChatOpenRouter"
    if provider == "google":
        return "from browser_use.llm.google.chat import ChatGoogle"
    return "from browser_use.llm import ChatGroq"


def render_llm_ctor(provider: str, model: str, api_key: str) -> str:
    key_part = ""
    if api_key:
        key_part = f", api_key='{api_key}'"
    if provider == "groq":
        return f"llm = ChatGroq(model='{model}', temperature=0.0{key_part})"
    if provider == "openrouter":
        return f"llm = ChatOpenRouter(model='{model}', temperature=0.0{key_part})"
    if provider == "google":
        return f"llm = ChatGoogle(model='{model}'{key_part})"
    return f"llm = ChatGroq(model='{model}', temperature=0.0{key_part})"


def render_data_loader(cfg: Dict[str, Any]) -> str:
    if cfg["source"] == "none":
        return "items = [None]"
    var_name = cfg.get("var_name") or "item"
    path = cfg.get("path", "")
    if cfg["source"] == "csv":
        return f"import pandas as pd\nitems = pd.read_csv(r'{path}')[r'{cfg.get('column','')}'].dropna().tolist()"
    if cfg["source"] == "excel":
        return f"import pandas as pd\nitems = pd.read_excel(r'{path}')[r'{cfg.get('column','')}'].dropna().tolist()"
    if cfg["source"] == "json":
        field = cfg.get("json_field", "")
        return f"import json\nwith open(r'{path}', 'r', encoding='utf-8') as f:\n    data = json.load(f)\nitems = [x.get('{field}') for x in data if x.get('{field}') is not None]"
    return "items = [None]"


def generate_script(blocks: List[Dict[str, Any]], data_cfg: Dict[str, Any], provider_cfg: Dict[str, Any]) -> str:
    task_text = build_task_text(blocks)
    llm_import = render_llm_import(provider_cfg["provider"])
    llm_ctor = render_llm_ctor(provider_cfg["provider"], provider_cfg["model"], provider_cfg.get("api_key", ""))
    data_loader = render_data_loader(data_cfg)
    initial_actions = []
    # solo navegacion/scroll determinista se ejecuta antes del LLM
    for b in blocks:
        if b["type"] == "navigate":
            initial_actions.append(f"    {{'navigate': {{'url': '{b['params']['url']}', 'new_tab': {str(b['params']['new_tab']).lower()}}}}}")
        if b["type"] == "scroll":
            initial_actions.append(f"    {{'scroll': {{'delta_y': {b['params']['delta_y']}, 'delta_x': {b['params']['delta_x']}}}}}")
    initial_block = ",\n".join(initial_actions) if initial_actions else ""

    var_name = data_cfg.get("var_name") or "item"
    # Interpolacion simple: si source es distinto de none, insertamos la variable
    if data_cfg["source"] == "none":
        task_expr = f"'''{task_text}'''"
    else:
        task_expr = f"f'''{task_text}\\nDato: {{{var_name}}}'''"

    script = f"""import asyncio
from browser_use import Agent, Browser
{llm_import}


async def run_once(task_text: str, llm, browser):
    agent = Agent(
        task=task_text,
        llm=llm,
        browser=browser,
        use_vision=False,
        initial_actions=[
{initial_block}
        ],
        max_steps=10,
        max_failures=3,
        max_actions_per_step=4,
        step_timeout=180,
        llm_timeout=45,
    )
    await agent.run()


async def main():
    {llm_ctor}
    browser = Browser(headless=False, keep_alive=True)

    {data_loader}

    for {var_name} in items:
        task_text = {task_expr}
        await run_once(task_text, llm, browser)


if __name__ == "__main__":
    asyncio.run(main())

# Ejecucion recomendada via BrowserUseEngine para mayor resiliencia.
"""
    return script


if st.button("Previsualizar script"):
    if not st.session_state.blocks:
        st.warning("Agrega al menos un bloque.")
    else:
        st.code(generate_script(st.session_state.blocks, st.session_state.data_cfg, st.session_state.provider_cfg), language="python")

if st.button("Guardar en Scripts Automaticos/"):
    if not file_name.endswith(".py"):
        st.error("El nombre debe terminar en .py")
    elif not st.session_state.blocks:
        st.error("Agrega al menos un bloque.")
    else:
        target = SCRIPTS_DIR / file_name
        target.write_text(generate_script(st.session_state.blocks, st.session_state.data_cfg, st.session_state.provider_cfg), encoding="utf-8")
        st.success(f"Guardado en {target}")
