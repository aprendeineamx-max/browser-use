import asyncio

from studio.engines.orchestrator_engine import OrchestratorEngine


async def main() -> None:
    task = (
        "Busca en la web el precio actual de la accion de Apple. "
        "Una vez que tengas el precio, usa Snowflake para escribir un comentario de analista de 5 palabras sobre ese precio."
    )
    orch = OrchestratorEngine()
    result = await orch.execute_task(task, context={})
    print("=== Resultado Orchestrator ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
