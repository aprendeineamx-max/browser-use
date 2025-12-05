from __future__ import annotations

from typing import Any, Callable, Dict

from langchain_core.tools import tool


def engine_to_tool(name: str, description: str, engine_ctor: Callable[[], Any]):
    """
    Convierte un engine en una Tool de LangChain para uso futuro.
    Ejecuta el engine de forma síncrona usando asyncio.run internamente.
    """

    @tool(name=name, description=description)
    def _wrapped(task: str) -> str:
        import asyncio

        async def run():
            eng = engine_ctor()
            res = await eng.execute_task(task, context={})
            await eng.stop()
            return str(res.get("result"))

        return asyncio.run(run())

    return _wrapped
