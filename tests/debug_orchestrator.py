import os
import asyncio
import sys
from pathlib import Path

# Forzar UTF-8 en consola Windows para evitar errores de logging con emojis
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONLEGACYWINDOWSIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Asegurar que la raiz del repo este en sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
