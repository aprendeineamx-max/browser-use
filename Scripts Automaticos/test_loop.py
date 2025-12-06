import asyncio
import pandas as pd
from studio.engines.browser_use_engine import BrowserUseEngine


async def run_once(task_text: str, engine, initial_actions):
    return await engine.execute_task(task_text, context={"initial_actions": initial_actions})


async def main():
    engine = BrowserUseEngine(headless=False, use_vision=False)

    items = pd.read_csv(r"..\\test_data.csv")

    initial_actions = [
        {'navigate': {'url': f'https://google.com/search?q={{row["busqueda"]}}', 'new_tab': False}},
        {'type': {'selector': 'input[name=q]', 'text': f"{{row['busqueda']}}", 'by': 'css'}},
        {'scroll': {'delta_y': 400, 'delta_x': 0, 'smart': True}},
    ]

    retry_count = 0
    retry_wait = 0

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
        print(f"Procesando fila {index}")
        task_text = f"Navega y busca: {row['busqueda']}\nDato: {row}"
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
                    print(f"Error definitivo tras reintentos: {exc}")
                    raise
                print(f"Reintento {attempts}/{retry_count} en {retry_wait}s por error: {exc}")
                await asyncio.sleep(retry_wait)

    await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

# Ejecucion recomendada via BrowserUseEngine para mayor resiliencia.
