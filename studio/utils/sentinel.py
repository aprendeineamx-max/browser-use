from __future__ import annotations

import gc
import json
import time
from pathlib import Path
from typing import Dict

import psutil

from studio.utils.logger import LOG_FILE, log_event

CONFIG_PATH = Path("studio/config.json")


def log_line(message: str) -> None:
    log_event("Sentinel", message)


def ensure_config() -> Dict[str, str]:
    default_cfg = {"profile": "estandar", "lavague_mode": "api"}
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(default_cfg, indent=2), encoding="utf-8")
        return default_cfg
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {**default_cfg, **data}
    except Exception:
        return default_cfg


def check_vital_signs(profile: str) -> Dict[str, str]:
    """Monitorea RAM/CPU y aplica protocolos segun el perfil."""
    mem = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent(interval=0.2)
    log_line(f"Vitals -> RAM: {mem:.1f}% CPU: {cpu:.1f}% Perfil: {profile}")

    if profile.lower() == "ligero":
        if mem > 70:
            log_line(f"RAM al {mem:.1f}%. Modo Ligero: pausa 5s y preferir APIs externas.")
            time.sleep(5)
            return {"prefer_external_api": "true"}
    elif profile.lower() == "estandar":
        if mem > 90:
            log_line(f"RAM al {mem:.1f}%. Modo Estandar: pausa 10s y GC.")
            time.sleep(10)
            gc.collect()
            return {"prefer_external_api": "true"}
    else:  # sin limite
        log_line("Modo Sin Limite: sin mitigacion, solo monitoreo.")

    return {"prefer_external_api": "false"}


def truncate_logs(keep_lines: int = 10) -> None:
    """Mantiene solo las ultimas `keep_lines` lineas del log para evitar crecimiento infinito."""
    if not LOG_FILE.exists():
        return
    try:
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
        tail = lines[-keep_lines:] if len(lines) > keep_lines else lines
        LOG_FILE.write_text("\n".join(tail) + ("\n" if tail else ""), encoding="utf-8")
        log_line(f"Log truncado a ultimas {keep_lines} lineas")
    except Exception:
        pass
