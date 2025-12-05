from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .base_engine import AutomationEngine
from studio.utils.sentinel import ensure_config, check_vital_signs

LOG_FILE = Path("Registro_de_logs.txt")


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:Snowflake][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class SnowflakeEngine(AutomationEngine):
    """
    Motor experimental para Snowflake Cortex.
    Ejecuta snowflake.cortex.complete en modo texto plano.
    """

    @classmethod
    def is_available(cls) -> bool:
        try:
            import snowflake.connector  # noqa: F401
        except Exception:
            return False
        base_required = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_SCHEMA",
        ]
        pat = os.environ.get("SNOWFLAKE_PAT")
        if pat:
            return all(os.environ.get(k) for k in base_required)
        required = base_required + ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
        return all(os.environ.get(k) for k in required)

    async def start(self) -> None:
        # Lazy: conectar en execute_task
        return None

    async def stop(self) -> None:
        # No mantenemos conexión persistente en esta versión
        return None

    def _run_query_sync(self, task: str) -> Dict[str, Any]:
        import snowflake.connector

        account = os.environ.get("SNOWFLAKE_ACCOUNT")
        warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE")
        database = os.environ.get("SNOWFLAKE_DATABASE")
        schema = os.environ.get("SNOWFLAKE_SCHEMA")
        pat = os.environ.get("SNOWFLAKE_PAT")

        conn_kwargs: Dict[str, Any] = {
            "account": account,
            "warehouse": warehouse,
            "database": database,
            "schema": schema,
        }
        if pat:
            log_line("Usando autenticacion por PAT (token)")
            conn_kwargs["authenticator"] = "SNOWFLAKE_JWT"
            conn_kwargs["token"] = pat
        else:
            conn_kwargs["user"] = os.environ.get("SNOWFLAKE_USER")
            conn_kwargs["password"] = os.environ.get("SNOWFLAKE_PASSWORD")

        query = (
            "select snowflake.cortex.complete('llama3-70b', "
            f"{{'messages':[{{'role':'user','content':'{task}'}}]}}) as resp"
        )
        conn = snowflake.connector.connect(**conn_kwargs)
        try:
            cur = conn.cursor()
            cur.execute(query)
            row = cur.fetchone()
            return {"success": True, "result": row[0] if row else "", "errors": []}
        finally:
            try:
                cur.close()
            except Exception:
                pass
            conn.close()

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        log_line(f"[Start] Tarea: {task}")
        cfg = ensure_config()
        check_vital_signs(cfg.get("profile", "estandar"))
        if not self.is_available():
            msg = "Snowflake no disponible (faltan deps o credenciales)"
            log_line(f"[Error] {msg}")
            return {"success": False, "result": "", "errors": [msg]}
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, lambda: self._run_query_sync(task))
            log_line("[Success] Consulta Cortex completada")
            return result
        except Exception as exc:
            log_line(f"[Error] {exc}")
            return {"success": False, "result": "", "errors": [str(exc)]}

    async def get_screenshot(self) -> bytes | None:
        return None
