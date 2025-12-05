"""
Demostracion basica: abre youtube.com usando Browser-Use con Groq (primario) y Browser Use Cloud.

Requisitos:
- Variables en .env: BROWSER_USE_API_KEY, GROQ_API_KEY (y opcional OPENROUTER_API_KEY como fallback).
- Entorno virtual activado.

Ejecucion:
    venv\Scripts\python run_youtube_demo.py
"""

from __future__ import annotations

import asyncio
import logging
import sys

from dotenv import load_dotenv

from browser_use import Agent, Browser
from browser_use.llm import ChatGroq


def configure_logging() -> None:
	try:
		sys.stdout.reconfigure(encoding="utf-8", errors="replace")
		sys.stderr.reconfigure(encoding="utf-8", errors="replace")
	except Exception:
		pass

	logging.basicConfig(
		level=logging.WARNING,  # menos ruido
		format="%(levelname)s %(name)s - %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
		force=True,
	)
	# Silencia logs con emojis/ANSI del paquete para evitar OSError en consolas Windows
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

	# Navegador local (usa Chromium/Chrome local). Si prefieres nube, pon use_cloud=True y añade créditos.
	browser = Browser(
		use_cloud=False,
		headless=False,
		wait_for_network_idle_page_load_time=0.75,
		minimum_wait_page_load_time=0.5,
	)

	task = "Abre youtube.com y termina."

	agent = Agent(
		task=task,
		llm=llm,
		browser=browser,
		use_vision=False,
		vision_detail_level="low",
		max_history_items=6,
		max_steps=4,
		max_failures=2,
		step_timeout=90,
		llm_timeout=60,
	)

	await agent.run()


if __name__ == "__main__":
	asyncio.run(main())
