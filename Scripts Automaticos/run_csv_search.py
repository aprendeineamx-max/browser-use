import asyncio
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
import os
import re

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
            # Modelo liviano pero compatible con structured outputs en OpenAI
            return ChatOpenRouter(model="openai/gpt-4.1-mini", temperature=0.0, api_key=OPENROUTER_KEY)
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
        override_system_message="Eres un navegador. Cumple la tarea.",
    )
    try:
        history = await agent.run()
        if not history.is_successful():
            raise RuntimeError(f"Agente termino con success={history.is_successful()}")
        if getattr(history, "has_errors", lambda: False)():
            log_line(f"Success degradado (errores internos) busqueda='{busqueda}'")
        else:
            log_line(f"Success busqueda='{busqueda}'")
        return
    except Exception as exc:
        msg = str(exc)
        schema_err = re.search(r"(response_format|json_schema|structured|Invalid JSON)", msg, re.IGNORECASE)
        if schema_err or True:
            log_line(f"Reintento degradado por error: {exc}")
            # Reintento degradado: Groq pequeño, prompt minimo y salida libre
            llm_fallback = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
            browser_fallback = Browser(
                headless=True,
                keep_alive=False,
                accept_downloads=False,
                wait_for_network_idle_page_load_time=0.5,
                minimum_wait_page_load_time=0.25,
            )
            task_fb = (
                f"Navega a https://www.google.com/search?q={busqueda.replace(' ', '+')} "
                "y devuelve en texto plano el titulo y snippet del primer resultado visible. "
                "Responde solo el dato, sin formateo JSON."
            )
            agent_fb = Agent(
                task=task_fb,
                llm=llm_fallback,
                browser=browser_fallback,
                use_vision=False,
                include_attributes=[],
                max_history_items=4,
                initial_actions=[
                    {"navigate": {"url": f"https://www.google.com/search?q={busqueda.replace(' ', '+')}", "new_tab": False}}
                ],
                max_steps=1,
                max_failures=1,
                max_actions_per_step=1,
                step_timeout=20,
                llm_timeout=15,
                flash_mode=True,
                override_system_message="Eres un navegador. Responde solo el dato encontrado.",
            )
            history_fb = await agent_fb.run()
            if not history_fb.is_successful():
                raise RuntimeError(f"Fallback tambien fallo success={history_fb.is_successful()}")
            log_line(f"Success degradado busqueda='{busqueda}'")
            return
        raise


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
