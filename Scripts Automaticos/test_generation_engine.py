import asyncio
import sys
from studio.engines.browser_use_engine import BrowserUseEngine

# Forzar UTF-8 para evitar errores en consola Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


async def run_once(task_text: str, engine, initial_actions):
    return await engine.execute_task(task_text, context={"initial_actions": initial_actions})


async def main():
    engine = BrowserUseEngine(headless=True, use_vision=False)

    items = [None]
    initial_actions = []  # sin navegación para evitar captchas

    for item in items:
        task_text = "Responde solo 'ok'."
        result = await run_once(task_text, engine, initial_actions)
        print("Resultado:", result)

    await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

# Ejecucion recomendada via BrowserUseEngine para mayor resiliencia.
