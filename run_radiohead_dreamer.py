"""
Demo: busca y reproduce "Dreamer Radiohead" en YouTube y deja la ventana abierta.

Requisitos:
- .env con BROWSER_USE_API_KEY (opcional si usas nube), GROQ_API_KEY (y opcional OPENROUTER_API_KEY).
- Entorno virtual activado.

Ejecucion:
    $env:PYTHONIOENCODING='utf-8'
    venv\Scripts\python run_radiohead_dreamer.py
"""

from __future__ import annotations

import asyncio
import logging
import sys

from dotenv import load_dotenv

from browser_use import Agent, Browser
from browser_use.llm import ChatGroq


def configure_logging() -> None:
	# Evita errores de encoding en Windows
	try:
		sys.stdout.reconfigure(encoding="utf-8", errors="replace")
		sys.stderr.reconfigure(encoding="utf-8", errors="replace")
	except Exception:
		pass

	logging.basicConfig(
		level=logging.WARNING,
		format="%(levelname)s %(name)s - %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
		force=True,
	)
	# Silenciar ruido de libreria
	for noisy in ["browser_use", "BrowserSession", "Agent"]:
		logger = logging.getLogger(noisy)
		logger.setLevel(logging.ERROR)
		logger.propagate = False
		logger.handlers = [logging.NullHandler()]


async def main() -> None:
	load_dotenv(dotenv_path=".env")
	configure_logging()

	# LLM Groq primario
	llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0.0)

	# Navegador local y persistente tras la tarea
	browser = Browser(
		use_cloud=False,               # cambia a True si quieres usar la nube (requiere saldo)
		headless=False,
		keep_alive=True,              # deja la ventana abierta al terminar
		wait_for_network_idle_page_load_time=0.75,
		minimum_wait_page_load_time=0.5,
	)

	# Tarea: buscar y reproducir (instrucciones deterministas y URL directa de búsqueda)
	task = """
	1. Abre https://www.youtube.com/results?search_query=Dreamer+Radiohead.
	2. Haz click en el primer resultado de video y empieza la reproduccion.
	3. No cierres el navegador al terminar.
	"""

	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		use_vision=False,
		vision_detail_level="low",
		max_history_items=6,
		max_steps=10,
		max_failures=2,
		step_timeout=120,
		llm_timeout=90,
		max_actions_per_step=4,
	)

	await agent.run()
	# No llamamos a close; keep_alive=True mantiene la ventana abierta.


if __name__ == "__main__":
	asyncio.run(main())
