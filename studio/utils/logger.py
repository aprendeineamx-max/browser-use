from __future__ import annotations

import time
from pathlib import Path

LOG_FILE = Path("Registro_de_logs.txt")


def log_event(component: str, message: str, level: str = "INFO") -> None:
    """Escribe una linea en el log centralizado."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{component}][{ts}][{level}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Evitar que un fallo de log detenga el flujo
        pass


def log_error(component: str, message: str) -> None:
    log_event(component, message, level="ERROR")


def log_success(component: str, message: str) -> None:
    log_event(component, message, level="SUCCESS")
