from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_engine import AutomationEngine

LOG_FILE = Path("Registro_de_logs.txt")


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:Skyvern][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class SkyvernEngine(AutomationEngine):
    """
    Esqueleto de motor para Skyvern.
    Simula la conexion a un contenedor docker y devuelve un mensaje mock.
    """

    async def start(self) -> None:
        log_line("Iniciando motor Skyvern (mock).")

    async def stop(self) -> None:
        log_line("Deteniendo motor Skyvern (mock).")

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.start()
        log_line(f"Tarea recibida: {task}")
        await asyncio.sleep(2)
        msg = "[MOCK] Skyvern Engine: Conectando a contenedor Docker... (No implementado aún)"
        log_line(msg)
        await self.stop()
        return {"success": True, "result": msg, "errors": []}

    async def get_screenshot(self) -> bytes | None:
        return None
