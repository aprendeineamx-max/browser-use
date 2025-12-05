import asyncio
import sys

# Fuerza UTF-8 para evitar errores de consola en Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from studio.engines.browser_use_engine import BrowserUseEngine


async def main():
    engine = BrowserUseEngine(headless=True, use_vision=False)
    result = await engine.execute_task("Responde solo 'ok' en una palabra.", context={"initial_actions": []})
    await engine.stop()
    print("Success:", result.get("success"))
    print("Result:", result.get("result"))
    print("Errors:", result.get("errors"))


if __name__ == "__main__":
    asyncio.run(main())
