import json
from pathlib import Path
from typing import Dict

CONFIG_PATH = Path("studio/config.json")


def load_config() -> Dict[str, str]:
    default = {"profile": "estandar", "lavague_mode": "api", "orchestrator_planner": "groq:llama-3.1-8b-instant"}
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return {**default, **data}
    except Exception:
        return default


def save_config(cfg: Dict[str, str]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
