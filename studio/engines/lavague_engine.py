from __future__ import annotations

import importlib.util
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_engine import AutomationEngine

LOG_FILE = Path("Registro_de_logs.txt")


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:LaVague][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class LaVagueEngine(AutomationEngine):
    """
    Motor LaVague. Se detecta de forma blanda: si el paquete no está instalado, queda No disponible.
    """

    @classmethod
    def is_available(cls) -> bool:
        return importlib.util.find_spec("lavague_core") is not None or importlib.util.find_spec("lavague") is not None

    async def start(self) -> None:
        log_line("[Start] Inicializando LaVague")

    async def stop(self) -> None:
        log_line("[Stop] Finalizando LaVague")

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.start()
        log_line(f"[Task] {task}")
        try:
            # Import lazily to avoid failures if missing deps
            try:
                from lavague_core.world_model import WorldModel
                from lavague_core.action_engine import ActionEngine
            except ImportError as exc:
                log_line(f"[Error] LaVague no importable: {exc}")
                return {"success": False, "result": "", "errors": [f"No importable: {exc}"]}

            model = WorldModel()
            engine = ActionEngine(world_model=model)
            result = engine.act(task)
            log_line("[Success] LaVague ejecucion completada")
            return {"success": True, "result": str(result), "errors": []}
        except Exception as exc:
            log_line(f"[Error] LaVague fallo: {exc}")
            return {"success": False, "result": "", "errors": [str(exc)]}
        finally:
            await self.stop()

    async def get_screenshot(self) -> bytes | None:
        return None
