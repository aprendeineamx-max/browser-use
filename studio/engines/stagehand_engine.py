from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_engine import AutomationEngine
from studio.utils.sentinel import ensure_config, check_vital_signs

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
        cfg = ensure_config()
        check_vital_signs(cfg.get("profile", "estandar"))
        try:
            cmd = NODE_CMD + [task]
            completed = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()
            if stdout:
                lines = [l for l in stdout.splitlines() if l.strip()]
                parsed = None
                import json

                for line in reversed(lines):
                    try:
                        parsed = json.loads(line)
                        break
                    except Exception:
                        continue
                if parsed:
                    success = bool(parsed.get("success"))
                    result = parsed.get("result")
                    error = parsed.get("error")
                    if not success:
                        log_line(f"Stagehand devolvio error: {error}")
                    else:
                        log_line("Stagehand ejecucion exitosa")
                    return {"success": success, "result": result or stdout, "errors": [] if success else ([error] if error else [])}
                log_line("No se pudo parsear salida Stagehand (sin JSON valido)")
                return {"success": False, "result": stdout, "errors": [stderr or "parse_error"]}
            return {"success": False, "result": "", "errors": ["Sin salida de Stagehand", stderr]}
        except Exception as exc:
            log_line(f"Error ejecutando Stagehand: {exc}")
            return {"success": False, "result": "", "errors": [str(exc)]}
        finally:
            await self.stop()

    async def get_screenshot(self) -> bytes | None:
        return None
