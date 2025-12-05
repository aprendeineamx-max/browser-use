from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_engine import AutomationEngine

LOG_FILE = Path("Registro_de_logs.txt")
RUNNER_PATH = Path("studio/bridge_stagehand/runner.js")
NODE_CMD = ["node", str(RUNNER_PATH)]


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:Stagehand][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class StagehandEngine(AutomationEngine):
    """
    Esqueleto para Stagehand (Node/Playwright).
    Comprueba presencia de Node y declara disponibilidad.
    """

    @classmethod
    def is_available(cls) -> bool:
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            return RUNNER_PATH.exists()
        except Exception:
            log_line("Stagehand no disponible: Node.js no detectado")
            return False

    async def start(self) -> None:
        log_line("Iniciando motor Stagehand (placeholder).")

    async def stop(self) -> None:
        log_line("Deteniendo motor Stagehand (placeholder).")

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.start()
        log_line(f"Tarea recibida: {task}")
        try:
            cmd = NODE_CMD + [task]
            completed = subprocess.run(cmd, capture_output=True, text=True)
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if stdout:
                try:
                    import json

                    data = json.loads(stdout)
                    success = bool(data.get("success"))
                    result = data.get("result")
                    error = data.get("error")
                    if not success:
                        log_line(f"Stagehand devolvio error: {error}")
                    return {"success": success, "result": result, "errors": [error] if error else []}
                except Exception as parse_err:
                    log_line(f"No se pudo parsear salida Stagehand: {parse_err}")
                    return {"success": False, "result": stdout, "errors": [str(parse_err), stderr]}
            return {"success": False, "result": "", "errors": ["Sin salida de Stagehand", stderr]}
        except Exception as exc:
            log_line(f"Error ejecutando Stagehand: {exc}")
            return {"success": False, "result": "", "errors": [str(exc)]}
        finally:
            await self.stop()

    async def get_screenshot(self) -> bytes | None:
        return None
