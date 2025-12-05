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

	# Acción determinista: SCROLL SUAVE para no saltarnos el video.
	initial_actions = [
		{'navigate': {'url': 'https://www.youtube.com/results?search_query=Radiohead+Daydreaming', 'new_tab': False}},
		{'scroll': {'delta_y': 150, 'delta_x': 0}}, # Bajamos menos (antes 400 era mucho)
	]

	task = """
	Objetivo: Reproducir "Daydreaming" de Radiohead (Oficial).
	
	1) IDENTIFICACION:
	   - El video que buscamos tiene el nombre de canal: "Radiohead" (Verificado).
	   - CUIDADO: Hay una versión de "SalvaMuñoz" o "[HQ]". ESA NO ES.
	   - Si ves "SalvaMuñoz", busca ARRIBA o ABAJO de ese video.
	   
	2) ACCION VISUAL:
	   - Ignora la cabecera (Anuncios/Banjo).
	   - Busca el bloque que diga "Radiohead" (el autor) y dale click al TITULO de ese video.
	   - Si el ratón falla, intenta usar TAB hasta llegar al título y pulsar Enter.
	   
	3) VERIFICACION:
	   - El video debe empezar a sonar.
	   - Si no suena, pulsa 'k'.
	"""

	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		use_vision=True,               # permitir vision para identificar thumbnails
		vision_detail_level="high",    # mas detalle para identificar titulos/canal
		include_attributes=["aria-label", "title", "href", "data", "innerText"],
		initial_actions=initial_actions,
		max_history_items=6,
		max_steps=25,
		max_failures=5,
		max_actions_per_step=10,
		step_timeout=240,
		llm_timeout=120,
	)

	await agent.run()
	# keep_alive=True mantiene la ventana abierta.


if __name__ == "__main__":
	asyncio.run(main())
