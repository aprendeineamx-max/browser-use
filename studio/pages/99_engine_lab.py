import asyncio
import streamlit as st

from studio.engines.browser_use_engine import BrowserUseEngine

st.set_page_config(page_title="Engine Lab", layout="wide")
st.title("Engine Lab (experimental)")

engine_name = st.selectbox("Motor", ["Browser Use"])
task_text = st.text_area("Tarea", "Dime la hora actual en Madrid y responde corto.")
run_btn = st.button("Ejecutar con Motor")


async def run_engine(task: str):
    engine = BrowserUseEngine(headless=True, use_vision=False)
    result = await engine.execute_task(task, context={})
    await engine.stop()
    return result


if run_btn:
    with st.spinner("Ejecutando..."):
        result = asyncio.run(run_engine(task_text))
    st.success(f"Success: {result.get('success')}")
    st.write("Resultado:")
    st.write(result.get("result"))
    if result.get("errors"):
        st.warning(f"Errores: {result.get('errors')}")
