"""
Demo robusto y trazable: busca y reproduce el video oficial de Radiohead ("Daydreaming")
sin usar enlace directo. Registra trazas completas en agent_radiohead_debug.log.

Requisitos:
- .env con GOOGLE_API_KEY (Gemini).
- Entorno virtual activado.

Ejecucion:
    $env:PYTHONIOENCODING="utf-8"
    .\venv\Scripts\python "Scripts Automaticos/run_radiohead_official.py"
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import traceback

from dotenv import load_dotenv

from browser_use import Agent, Browser
from browser_use.llm.google.chat import ChatGoogle

LOG_FILE = "agent_radiohead_debug.log"


def configure_logging() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="w")
    file_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[console_handler, file_handler],
        force=True,
    )

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


async def main() -> None:
    try:
        load_dotenv(dotenv_path=".env")
        configure_logging()

        print("Iniciando script de automatizacion de Radiohead...")
        print(f"Log detallado en: {LOG_FILE}")
        
        # VERIFICACION DE MODELO:
        # Usamos gemini-2.0-flash que está verificado en la librería.
        # gemini-1.5-flash dió error 404 (no soportado por este wrapper).
        # gemini-2.0-flash-exp dió error 429 (cuota excedida).
        llm = ChatGoogle(
            model="gemini-2.0-flash", 
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        browser = Browser(
            use_cloud=False,
            headless=False,
            keep_alive=True,
            wait_for_network_idle_page_load_time=1.5,
            minimum_wait_page_load_time=1.0,
        )

        initial_actions = [
            {"navigate": {"url": "https://www.youtube.com/results?search_query=Radiohead+Daydreaming", "new_tab": False}},
            {"scroll": {"delta_y": 150, "delta_x": 0}},
        ]

        task = """
OBJETIVO: Reproducir "Daydreaming" de Radiohead (canal oficial).

PASOS:
1) Ya estas en resultados de YouTube para "Radiohead Daydreaming".
2) Busca el primer resultado cuyo titulo incluya "Daydreaming" y cuyo canal sea exactamente "Radiohead".
   - Ignora anuncios/patrocinados.
   - Ignora versiones de "SalvaMuñoz", "[HQ]" u otros canales.
3) Si lo ves: haz click en el TITULO del video (no en el anuncio). Si el click falla, usa Tab hasta enfocar y presiona Enter.
4) Si no aparece en pantalla, haz scroll hacia abajo (300px) y vuelve a buscar; repite hasta hallarlo.
5) Una vez en el video, espera 5s y si no reproduce, presiona 'k' o 'space' para iniciar.
6) Deja el navegador abierto.
"""

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=True,
            vision_detail_level="high",
            include_attributes=["href", "title", "aria-label", "innerText"],
            initial_actions=initial_actions,
            max_history_items=10,
            max_steps=25,
            max_failures=5,
            max_actions_per_step=10,
            step_timeout=240,
            llm_timeout=120,
        )

        await agent.run()

    except Exception as e:
        print("\n❌ ERROR CRITICO EN EL AGENTE:")
        print(str(e))
        print("\n🔍 Traceback completo:")
        traceback.print_exc()
    finally:
        print("\n🏁 Proceso finalizado.")


if __name__ == "__main__":
    asyncio.run(main())
