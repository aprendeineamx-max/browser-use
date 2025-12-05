"""
Diagnostic runner for Browser-Use with Groq.
- Configura logging sin caracteres especiales para evitar errores de consola en Windows.
- Valida claves y limita contexto para reducir errores 413 (TPM exceeded).
- Reporta causa y resolucion cuando el proveedor devuelve error.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

from browser_use import Agent
from browser_use.llm import ChatGroq
from browser_use.llm.exceptions import ModelProviderError, ModelRateLimitError


class FailureReport(BaseModel):
	stage: str
	error_type: str
	status_code: Optional[int]
	cause: str
	resolution: str
	raw: str


def configure_logging() -> None:
	try:
		sys.stdout.reconfigure(encoding='utf-8', errors='replace')
		sys.stderr.reconfigure(encoding='utf-8', errors='replace')
	except Exception:
		pass
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s %(levelname)s %(name)s - %(message)s',
		handlers=[logging.StreamHandler(sys.stdout)],
		force=True,
	)


def explain_provider_error(exc: ModelProviderError | ModelRateLimitError) -> FailureReport:
	status = getattr(exc, 'status_code', None)
	msg = str(exc)

	if status == 413 or 'TPM' in msg or 'Request too large' in msg:
		cause = 'Groq TPM limit exceeded; el mensaje o el contexto de pagina es demasiado grande.'
		resolution = (
			'Reduce max_history_items, desactiva vision/capturas, acorta la tarea o espera 60s antes de reintentar. '
			'Si persiste, usa un modelo de menor costo de tokens.'
		)
	elif status == 403:
		cause = 'Acceso denegado por Groq (clave o permisos de red/organizacion).'
		resolution = 'Verifica GROQ_API_KEY, permisos de la organizacion y que la red permita salir a api.groq.com.'
	else:
		cause = 'El proveedor rechazo la peticion.'
		resolution = 'Reintenta con contexto mas pequeno y valida el estado del servicio.'

	return FailureReport(
		stage='llm_call',
		error_type=exc.__class__.__name__,
		status_code=status,
		cause=cause,
		resolution=resolution,
		raw=msg,
	)


def build_agent(task: str) -> Agent:
	llm = ChatGroq(
		model=os.getenv('MODEL_NAME', 'meta-llama/llama-4-maverick-17b-128e-instruct'),
		temperature=0.0,
	)

	agent = Agent(
		task=task,
		llm=llm,
		use_vision=False,              # evita capturas y reduce tokens
		vision_detail_level='low',
		# Browser-Use requiere max_history_items > 5; usa 6 para recortar contexto sin violar el limite
		max_history_items=6,
		max_actions_per_step=2,
		max_steps=6,
		max_failures=2,
		step_timeout=90,
		llm_timeout=60,
	)
	return agent


async def run_with_diagnostics(task: str) -> None:
	groq_key = os.getenv('GROQ_API_KEY')
	if not groq_key:
		logging.error('Falta GROQ_API_KEY en el entorno; no se puede iniciar el agente.')
		return

	agent = build_agent(task)

	try:
		await agent.run()
	except (ModelProviderError, ModelRateLimitError) as exc:
		report = explain_provider_error(exc)
		logging.error('LLM error: %s', report.model_dump())
	except Exception as exc:  # pragma: no cover
		logging.exception('Error inesperado: %s', exc)


async def main() -> None:
	load_dotenv(dotenv_path='.env')
	configure_logging()

	task = "Abre youtube.com y termina."
	await run_with_diagnostics(task)


if __name__ == '__main__':
	asyncio.run(main())
