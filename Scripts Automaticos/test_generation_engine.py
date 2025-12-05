import asyncio
from studio.engines.browser_use_engine import BrowserUseEngine


async def run_once(task_text: str, engine, initial_actions):
    return await engine.execute_task(task_text, context={"initial_actions": initial_actions})


async def main():
    engine = BrowserUseEngine(headless=False, use_vision=False)

    items = [None]

    initial_actions = [
    {'navigate': {'url': 'https://example.com', 'new_tab': false}},
    {'scroll': {'delta_y': 200, 'delta_x': 0}}
    ]

    for item in items:
        task_text = '''1. Navega a https://example.com (nueva pesta?a: False).
2. Haz scroll (delta_y=200, delta_x=0).'''
        result = await run_once(task_text, engine, initial_actions)
        print("Resultado:", result)

    await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

# Ejecucion recomendada via BrowserUseEngine para mayor resiliencia.
