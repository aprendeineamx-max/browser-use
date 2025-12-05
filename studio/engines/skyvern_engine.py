from __future__ import annotations

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_engine import AutomationEngine
from studio.utils.sentinel import ensure_config, check_vital_signs

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

    @classmethod
    def is_available(cls) -> bool:
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            return True
        except Exception:
            log_line("Skyvern en Standby: Docker no disponible")
            return False

    async def start(self) -> None:
        log_line("Iniciando motor Skyvern (mock).")

    async def stop(self) -> None:
        log_line("Deteniendo motor Skyvern (mock).")

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.start()
        log_line(f"Tarea recibida: {task}")
        cfg = ensure_config()
        check_vital_signs(cfg.get("profile", "estandar"))
        await asyncio.sleep(2)
        msg = "[MOCK] Skyvern Engine: Conectando a contenedor Docker... (No implementado aún)"
        log_line(msg)
        await self.stop()
        return {"success": True, "result": msg, "errors": []}

    async def get_screenshot(self) -> bytes | None:
        return None
