"""
Block Builder (avanzado)
- Nuevos tipos de bloque: click/input por CSS o XPath, scroll/reintentos.
- Datos externos: CSV/Excel/JSON para iterar tareas.
- Edición de scripts existentes (texto) desde Scripts Automaticos/.

Nota: Las API keys se gestionan en Key Tester/Settings; el builder solo arma lógica de bloques y elige motor.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

from studio.utils.logger import log_event, log_error, log_success

SCRIPTS_DIR = Path("Scripts Automaticos")
SCRIPTS_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="Block Builder", layout="wide")
st.title("Block Builder (avanzado)")

with st.expander("Instrucciones", expanded=True):
    st.markdown(
        """
        - Añade bloques (navegar, scroll, click/input por CSS/XPath, reintentos).
        - Opcional: define una fuente de datos (CSV/Excel/JSON) para iterar.
        - Elige el motor (Browser Use, Stagehand, etc.). Las keys se configuran en el Key Tester/Settings.
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
    if "engine_choice" not in st.session_state:
        st.session_state.engine_choice = "browser_use"


init_state()


# -------------------------
# Helpers
# -------------------------
def add_block(block_type: str):
    defaults = {
        "navigate": {"url": "https://example.com", "new_tab": False},
        "scroll": {"delta_y": 300, "delta_x": 0, "smart": True},
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
        return f"{idx}. Haz scroll (delta_y={p['delta_y']}, delta_x={p['delta_x']}, smart={p.get('smart', False)})."
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
        smart = st.checkbox(f"Scroll inteligente #{idx+1}", value=p.get("smart", True), key=f"scr_sm_{idx}")
        new_blocks.append({"type": "scroll", "params": {"delta_y": dy, "delta_x": dx, "smart": smart}})
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
    preview = None
    if data_cfg["path"]:
        try:
            path_obj = Path(data_cfg["path"])
            if not path_obj.exists():
                st.error("El archivo no existe.")
            elif path_obj.stat().st_size > 5 * 1024 * 1024:
                st.error("El archivo supera 5MB. Usa un archivo más pequeño.")
            else:
                if data_cfg["source"] == "csv":
                    import pandas as pd
                    df = pd.read_csv(path_obj, nrows=5)
                    preview = df
                    rows_detected = len(pd.read_csv(path_obj))
                elif data_cfg["source"] == "excel":
                    import pandas as pd
                    df = pd.read_excel(path_obj, nrows=5)
                    preview = df
                    rows_detected = len(pd.read_excel(path_obj))
                elif data_cfg["source"] == "json":
                    import json
                    with path_obj.open("r", encoding="utf-8") as f:
                        data_json = json.load(f)
                    rows_detected = len(data_json)
                    preview = data_json[:5] if isinstance(data_json, list) else None
        except Exception as exc:
            st.error(f"No se pudo cargar el archivo: {exc}")
            log_error("BlockBuilder", f"Error leyendo datos externos: {exc}")
            rows_detected = None
    if rows_detected is not None:
        st.info(f"Modo de Datos Activo: {rows_detected} filas detectadas (vista previa de 5 filas abajo)")
        if preview is not None:
            st.write(preview)
st.session_state.data_cfg = data_cfg

# -------------------------
# Seleccion de motor (Strategy)
# -------------------------
from studio.engines.browser_use_engine import BrowserUseEngine
from studio.engines.stagehand_engine import StagehandEngine
from studio.engines.skyvern_engine import SkyvernEngine
from studio.engines.lavague_engine import LaVagueEngine
from studio.engines.snowflake_engine import SnowflakeEngine

engine_defs = [
    ("browser_use", "Browser Use", BrowserUseEngine, BrowserUseEngine.is_available()),
    ("stagehand", "Stagehand (Nativo - Node.js)", StagehandEngine, StagehandEngine.is_available()),
    ("skyvern", "Skyvern (Standby - Docker)", SkyvernEngine, SkyvernEngine.is_available()),
    ("lavague", "LaVague (Python)", LaVagueEngine, LaVagueEngine.is_available()),
    ("snowflake", "Snowflake Cortex (Experimental)", SnowflakeEngine, SnowflakeEngine.is_available()),
]
engine_labels = []
engine_keys = []
for key, label, _, ok in engine_defs:
    engine_labels.append(label if ok else f"{label} (No disponible)")
    engine_keys.append(key)

current_choice = st.session_state.engine_choice
default_idx = engine_keys.index(current_choice) if current_choice in engine_keys else 0
selected_label = st.selectbox("Motor de ejecucion", engine_labels, index=default_idx)
selected_key = engine_keys[engine_labels.index(selected_label)]
st.session_state.engine_choice = selected_key


# -------------------------
# Cargar script existente (texto)
# -------------------------
st.subheader("Cargar script existente")
existing = sorted(p.name for p in SCRIPTS_DIR.glob("*.py"))
selected_script = st.selectbox("Script", ["(ninguno)"] + existing)
loaded_code = ""
if selected_script != "(ninguno)":
    loaded_code = (SCRIPTS_DIR / selected_script).read_text(encoding="utf-8")
edited_code = st.text_area("Contenido (solo texto, no parsea a bloques)", value=loaded_code, height=200, key="loaded_code")
col_edit1, col_edit2 = st.columns(2)
with col_edit1:
    if selected_script != "(ninguno)" and st.button("Guardar cambios en script cargado"):
        (SCRIPTS_DIR / selected_script).write_text(edited_code, encoding="utf-8")
        log_success("BlockBuilder", f"Script editado guardado: {selected_script}")
        st.success(f"Guardado {selected_script}")
with col_edit2:
    new_copy_name = st.text_input("Guardar copia de este script como (.py)", value="", key="loaded_save_as")
    if st.button("Guardar copia del script cargado"):
        if not new_copy_name.endswith(".py"):
            st.error("El nombre debe terminar en .py")
        else:
            target = SCRIPTS_DIR / new_copy_name
            target.write_text(edited_code, encoding="utf-8")
            log_success("BlockBuilder", f"Copia creada desde editor: {new_copy_name}")
            st.success(f"Copia guardada: {new_copy_name}")

# -------------------------
# Generar script
# -------------------------
st.subheader("Generar script")
file_name = st.text_input("Nombre del script (.py)", value="custom_script.py")


def build_task_text(blocks: List[Dict[str, Any]]) -> str:
    lines = [render_block_text(b, i + 1) for i, b in enumerate(blocks)]
    return "\n".join(lines)


def render_data_loader(cfg: Dict[str, Any]) -> str:
    if cfg["source"] == "none":
        return "items = [None]"
    var_name = cfg.get("var_name") or "item"
    path = cfg.get("path", "")
    if cfg["source"] == "csv":
        return f"import pandas as pd\nitems = pd.read_csv(r'{path}')[r'{cfg.get('column','')}'].dropna().tolist()"
    if cfg["source"] == "excel":
        return (
            "import pandas as pd\n"
            f"items = pd.read_excel(r'{path}')[r'{cfg.get('column','')}'].dropna().tolist()\n"
            "# Requiere openpyxl para archivos .xlsx"
        )
    if cfg["source"] == "json":
        field = cfg.get("json_field", "")
        return f"import json\nwith open(r'{path}', 'r', encoding='utf-8') as f:\n    data = json.load(f)\nitems = [x.get('{field}') for x in data if x.get('{field}') is not None]"
    return "items = [None]"


def split_actions(blocks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    retry_cfg: Dict[str, Any] = {"retries": 0, "wait_seconds": 0}
    for b in blocks:
        t = b["type"]
        p = b["params"]
        if t == "navigate":
            actions.append({"navigate": {"url": p["url"], "new_tab": bool(p["new_tab"])}})
        elif t == "scroll":
            actions.append({"scroll": {"delta_y": p["delta_y"], "delta_x": p["delta_x"], "smart": p.get("smart", False)}})
        elif t in ("click_css", "click_xpath"):
            actions.append({"click": {"selector": p["selector"], "by": "css" if t == "click_css" else "xpath", "description": p["description"]}})
        elif t in ("input_css", "input_xpath"):
            actions.append({"type": {"selector": p["selector"], "text": p["text"], "by": "css" if t == "input_css" else "xpath"}})
        elif t == "retry":
            retry_cfg = {"retries": int(p.get("retries", 0)), "wait_seconds": int(p.get("wait_seconds", 0)), "note": p.get("note", "")}
    return actions, retry_cfg


def format_actions(actions: List[Dict[str, Any]], row_var: str, use_row: bool) -> str:
    if not actions:
        return "    # sin acciones predefinidas\n"
    lines = []
    for act in actions:
        # sustitucion basica en strings
        normalized: Dict[str, Any] = {}
        for k, v in act.items():
            if isinstance(v, dict):
                sub = {}
                for sk, sv in v.items():
                    if isinstance(sv, str) and use_row:
                        interp = interpolate(sv)
                        if interp != sv:
                            sub[sk] = f"f\"{interp}\""
                        else:
                            sub[sk] = repr(sv)
                    else:
                        sub[sk] = sv
                normalized[k] = sub
            else:
                normalized[k] = v
        # construir linea
        rendered_parts = []
        for key, val in normalized.items():
            if isinstance(val, dict):
                inner_parts = []
                for ik, iv in val.items():
                    if isinstance(iv, str) and iv.startswith("f\""):
                        inner_parts.append(f"'{ik}': {iv}")
                    else:
                        inner_parts.append(f"'{ik}': {iv}")
                inner = ", ".join(inner_parts)
                rendered_parts.append(f"'{key}': {{{inner}}}")
            else:
                rendered_parts.append(f"'{key}': {val!r}")
        lines.append(f"        {{{', '.join(rendered_parts)}}},")
    return "\n".join(lines)


def interpolate(text: str) -> str:
    """Reemplaza ${campo} por {row['campo']} para usar en f-strings."""
    if "${" not in text:
        return text
    out = text
    matches = []
    import re

    for m in re.finditer(r"\$\{([^}]+)\}", text):
        matches.append(m.group(1))
    for field in matches:
        out = out.replace("${" + field + "}", "{row['" + field + "']}")
    return out


def generate_script(blocks: List[Dict[str, Any]], data_cfg: Dict[str, Any], engine_key: str) -> str:
    task_text = build_task_text(blocks)
    data_loader = render_data_loader(data_cfg)
    actions, retry_cfg = split_actions(blocks)
    use_row = data_cfg.get("source") != "none"
    actions_block = format_actions(actions, row_var="row", use_row=use_row)

    var_name = data_cfg.get("var_name") or "item"
    interpolated_task = interpolate(task_text)
    if data_cfg["source"] == "none":
        task_expr = f"'''{interpolated_task}'''"
    else:
        prefix = "f"
        task_expr = f"{prefix}'''{interpolated_task}\\nDato: {{{var_name}}}'''"

    engine_import = "from studio.engines.browser_use_engine import BrowserUseEngine"
    engine_ctor = "BrowserUseEngine(headless=False, use_vision=False)"
    if engine_key == "stagehand":
        engine_import = "from studio.engines.stagehand_engine import StagehandEngine"
        engine_ctor = "StagehandEngine()"
    elif engine_key == "skyvern":
        engine_import = "from studio.engines.skyvern_engine import SkyvernEngine"
        engine_ctor = "SkyvernEngine()"
    elif engine_key == "lavague":
        engine_import = "from studio.engines.lavague_engine import LaVagueEngine"
        engine_ctor = "LaVagueEngine()"
    elif engine_key == "snowflake":
        engine_import = "from studio.engines.snowflake_engine import SnowflakeEngine"
        engine_ctor = "SnowflakeEngine()"

    needs_pandas = data_cfg.get("source") in ("csv", "excel")
    pandas_import = "import pandas as pd\n" if needs_pandas else ""

    script = f"""import asyncio
{pandas_import}import json
{engine_import}


async def run_once(task_text: str, engine, initial_actions):
    return await engine.execute_task(task_text, context={{"initial_actions": initial_actions}})


async def main():
    engine = {engine_ctor}

    {data_loader}

    initial_actions = [
{actions_block}
    ]

    retry_count = {retry_cfg.get("retries", 0)}
    retry_wait = {retry_cfg.get("wait_seconds", 0)}

    # Ejecutar las acciones base para cada fila de datos
    if isinstance(items, list):
        iterable = items
    elif hasattr(items, "iterrows"):
        iterable = items.iterrows()
    else:
        iterable = [items]

    for maybe_index, maybe_row in enumerate(iterable):
        if isinstance(maybe_row, tuple) and len(maybe_row) == 2:
            index, row = maybe_row
        else:
            index, row = maybe_index, maybe_row
        print(f"Procesando fila {{index}}")
        task_text = {task_expr}.replace("${{index}}", str(index))
        attempts = 0
        while True:
            try:
                result = await run_once(task_text, engine, initial_actions)
                if isinstance(result, dict) and not result.get("success", True):
                    raise RuntimeError(result.get("errors") or "Ejecucion no exitosa")
                print("Resultado:", result)
                break
            except Exception as exc:
                attempts += 1
                if attempts > retry_count:
                    print(f"Error definitivo tras reintentos: {{exc}}")
                    raise
                print(f"Reintento {{attempts}}/{{retry_count}} en {{retry_wait}}s por error: {{exc}}")
                await asyncio.sleep(retry_wait)

    await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

# Ejecucion recomendada via BrowserUseEngine para mayor resiliencia.
"""
    return script


if st.button("Previsualizar script"):
    if not st.session_state.blocks:
        st.warning("Agrega al menos un bloque.")
    else:
        script_preview = generate_script(st.session_state.blocks, st.session_state.data_cfg, st.session_state.engine_choice)
        st.code(script_preview, language="python")
        log_event("BlockBuilder", f"Previsualizacion generada para {len(st.session_state.blocks)} bloques")

if st.button("Guardar en Scripts Automaticos/"):
    if not file_name.endswith(".py"):
        st.error("El nombre debe terminar en .py")
    elif not st.session_state.blocks:
        st.error("Agrega al menos un bloque.")
    else:
        target = SCRIPTS_DIR / file_name
        script_content = generate_script(st.session_state.blocks, st.session_state.data_cfg, st.session_state.engine_choice)
        target.write_text(script_content, encoding="utf-8")
        log_success("BlockBuilder", f"Script generado y guardado: {target}")
        st.success(f"Guardado en {target}")
