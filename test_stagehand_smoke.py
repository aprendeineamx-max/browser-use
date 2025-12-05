import asyncio
import sys
from studio.engines.stagehand_engine import StagehandEngine


async def main():
    engine = StagehandEngine()
    res = await engine.execute_task(
        "Ve a https://www.google.com/search?q=example.com y extrae el texto del encabezado H1",
        context={},
    )
    print(res)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    asyncio.run(main())
