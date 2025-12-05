import asyncio
import json
from pathlib import Path

from studio.engines.browser_use_engine import BrowserUseEngine
from studio.utils.sentinel import ensure_config

CONFIG_PATH = Path("studio/config.json")


def write_profile(profile: str) -> None:
    cfg = ensure_config()
    cfg["profile"] = profile
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


async def main():
    original = ensure_config()
    write_profile("ligero")
    print("Perfil temporal establecido a 'ligero'")

    engine = BrowserUseEngine(headless=True, use_vision=False, keep_alive=False, model="llama-3.1-8b-instant")
    result = await engine.execute_task("Di hola y termina.", {})
    await engine.stop()

    print("Resultado de BrowserUseEngine:", result)

    # Restaurar perfil original
    write_profile(original.get("profile", "estandar"))
    print(f"Perfil restaurado a '{original.get('profile', 'estandar')}'")


if __name__ == "__main__":
    asyncio.run(main())
