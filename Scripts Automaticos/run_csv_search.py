import asyncio
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
import os

from browser_use import Agent, Browser
from browser_use.llm import ChatGroq, ChatOpenRouter

CSV_PATH = Path("prueba_datos.csv")
LOG_FILE = Path("Registro_de_logs.txt")
STREAM_LOG = Path("browser_use_stream.log")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")


# Asegura UTF-8 para que no fallen los prints en Windows con emojis/acentos.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Logueo simple apuntando a stdout reconfigurado
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler(STREAM_LOG, encoding="utf-8")],
    force=True,
)


def log_line(message: str) -> None:
    """Append message to log file and echo to stdout."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[E2E][{ts}] {message}"
    print(line)
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # No bloquear la ejecucion si no se puede escribir.
        pass


def build_llm():
    try:
        if OPENROUTER_KEY:
            return ChatOpenRouter(model="gpt-3.5-turbo", temperature=0.0, api_key=OPENROUTER_KEY)
        raise RuntimeError("OPENROUTER_API_KEY no configurada")
    except Exception as exc:
        log_line(f"Fallback a Groq por error en OpenRouter: {exc}")
        return ChatGroq(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.0,
        )


async def run_item(busqueda: str, accion: str) -> None:
    llm = build_llm()
    browser = Browser(
        headless=False,  # se deja visible para validar la prueba en vivo
        keep_alive=False,
        accept_downloads=False,
        wait_for_network_idle_page_load_time=1.0,
        minimum_wait_page_load_time=0.5,
    )
    task = (
        f"Busca en Google: {busqueda}. Accion: {accion}. "
        "Devuelve solo el primer resultado visible (titulo + fragmento breve)."
    )
    initial_actions = [
        {"navigate": {"url": f'https://www.google.com/search?q={busqueda.replace(" ", "+")}', "new_tab": False}},
        {"scroll": {"delta_y": 300, "delta_x": 0}},
    ]
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=False,
        include_attributes=[],
        max_history_items=6,
        initial_actions=initial_actions,
        max_steps=2,
        max_failures=2,
        max_actions_per_step=1,
        step_timeout=45,
        llm_timeout=25,
        flash_mode=True,
    )
    history = await agent.run()
    if not history.is_successful():
        raise RuntimeError(f"Agente termino con success={history.is_successful()}")


async def main() -> None:
    if not CSV_PATH.exists():
        log_line(f"CSV no encontrado: {CSV_PATH}")
        return
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            busqueda = row.get("busqueda", "")
            accion = row.get("accion", "")
            log_line(f"Ejecutando busqueda='{busqueda}' accion='{accion}'")
            try:
                await run_item(busqueda, accion)
                log_line(f"OK busqueda='{busqueda}'")
            except Exception as exc:
                log_line(f"Fallo busqueda='{busqueda}' error={exc}")


if __name__ == "__main__":
    asyncio.run(main())
