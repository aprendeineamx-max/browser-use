import asyncio
import streamlit as st

from studio.engines.browser_use_engine import BrowserUseEngine
from studio.engines.skyvern_engine import SkyvernEngine
from studio.engines.stagehand_engine import StagehandEngine
from studio.engines.lavague_engine import LaVagueEngine

st.set_page_config(page_title="Engine Lab", layout="wide")
st.title("Engine Lab (experimental)")


def available_engines():
    engines = []
    engines.append(("Browser Use", BrowserUseEngine, BrowserUseEngine.is_available()))
    engines.append(("Stagehand (Nativo - Node.js)", StagehandEngine, StagehandEngine.is_available()))
    engines.append(("Skyvern (Standby - Docker)", SkyvernEngine, SkyvernEngine.is_available()))
    engines.append(("LaVague (Python)", LaVagueEngine, LaVagueEngine.is_available()))
    labels = []
    keys = []
    classes = []
    for name, cls, ok in engines:
        label = name if ok else f"{name} (No disponible)"
        labels.append(label)
        keys.append(name)
        classes.append((name, cls, ok))
    return labels, classes


labels, classes = available_engines()
engine_label = st.selectbox("Motor", labels)
task_text = st.text_area("Tarea", "Dime la hora actual en Madrid y responde corto.")
run_btn = st.button("Ejecutar con Motor")


async def run_engine(task: str, selected_label: str):
    chosen = next(c for c in classes if (c[0] in selected_label))
    name, cls, ok = chosen
    if not ok:
        return {"success": False, "result": f"{name} no disponible en este entorno.", "errors": ["no_available"]}
    engine = cls()
    result = await engine.execute_task(task, context={})
    await engine.stop()
    return result


if run_btn:
    with st.spinner("Ejecutando..."):
        result = asyncio.run(run_engine(task_text, engine_label))
    st.success(f"Success: {result.get('success')}")
    st.write("Resultado:")
    st.write(result.get("result"))
    if result.get("errors"):
        st.warning(f"Errores: {result.get('errors')}")
