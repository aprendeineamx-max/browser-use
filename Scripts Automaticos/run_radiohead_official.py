"""
Demo robusto: busca y reproduce el video oficial de Radiohead ("Daydreaming") en YouTube
sin usar enlace directo; el agente debe seleccionar el resultado correcto (canal Radiohead).

Requisitos:
- .env con: GOOGLE_API_KEY.
- Entorno virtual activado.

Ejecucion:
    $env:PYTHONIOENCODING="utf-8"
    .\venv\Scripts\python "Scripts Automaticos/run_radiohead_official.py"
"""

from __future__ import annotations

import asyncio
import logging
import sys
import os

from dotenv import load_dotenv

from browser_use import Agent, Browser
from browser_use.llm.google.chat import ChatGoogle


def configure_logging() -> None:
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
	for noisy in ["browser_use", "BrowserSession", "Agent"]:
		logger = logging.getLogger(noisy)
		logger.setLevel(logging.ERROR)
		logger.propagate = False
		logger.handlers = [logging.NullHandler()]


async def main() -> None:
	load_dotenv(dotenv_path=".env")
	configure_logging()

    # Usamos Gemini 2.0 Flash Experimental que es el que ha demostrado funcionar
	llm = ChatGoogle(
		model='gemini-2.0-flash-exp',
		api_key=os.getenv('GOOGLE_API_KEY')
	)

	browser = Browser(
		use_cloud=False,               # Local para evitar costos
		headless=False,
		keep_alive=True,               # Mantener ventana abierta para escuchar el video
		wait_for_network_idle_page_load_time=0.75,
		minimum_wait_page_load_time=0.5,
	)

	# Acción determinista inicial para evitar about:blank y arrancar desde resultados
	# Esto ayuda mucho al modelo a no perderse en la navegación inicial
	initial_actions = [
		{'navigate': {'url': 'https://www.youtube.com/results?search_query=Radiohead+Daydreaming', 'new_tab': False}},
	]

	task = """
	Sigue estos pasos en YouTube (sin usar enlace directo al video):
	1) Ya deberias estar en los resultados de busqueda. Si no, busca "Radiohead Daydreaming".
	2) En resultados:
	   - Omite anuncios/patrocinados.
	   - Identifica el primer video cuyo titulo contenga "Daydreaming" y cuyo canal sea exactamente "Radiohead".
	   - Haz click en el thumbnail o titulo de ese video.
	3) Espera a que empiece la reproduccion y confirma que el video se este reproduciendo.
	4) Deja el navegador abierto al terminar.
	"""

	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		use_vision=True,               # permitir vision para identificar thumbnails
		vision_detail_level="low",     # low ahorra tokens y suele ser suficiente
		initial_actions=initial_actions,
		max_history_items=6,
		max_steps=18,
		max_failures=3,
		max_actions_per_step=5,
		step_timeout=180,
		llm_timeout=90,
	)

	await agent.run()
	# keep_alive=True mantiene la ventana abierta.


if __name__ == "__main__":
	asyncio.run(main())
