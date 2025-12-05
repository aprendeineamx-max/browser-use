from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from browser_use import Agent, Browser
from browser_use.llm import ChatGroq

from .base_engine import AutomationEngine
from studio.utils.sentinel import ensure_config, check_vital_signs

LOG_FILE = Path("Registro_de_logs.txt")


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:BrowserUse][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class BrowserUseEngine(AutomationEngine):
    """
    Implementacion de AutomationEngine usando browser-use.
    Incluye manejo de fallback cuando el proveedor devuelve errores de JSON/schema.
    """

    @classmethod
    def is_available(cls) -> bool:
        return True

    def __init__(
        self,
        model: str = "meta-llama/llama-4-maverick-17b-128e-instruct",
        headless: bool = False,
        use_vision: bool = False,
        keep_alive: bool = False,
    ) -> None:
        self.model = model
        self.headless = headless
        self.use_vision = use_vision
        self.keep_alive = keep_alive
        self.browser: Optional[Browser] = None

    async def start(self) -> None:
        self.browser = Browser(
            headless=self.headless,
            keep_alive=self.keep_alive,
            accept_downloads=False,
        )

    async def stop(self) -> None:
        if self.browser:
            await self.browser.stop()
            self.browser = None

    async def _run_agent(
        self,
        task: str,
        browser: Browser,
        model: str,
        flash_mode: bool = True,
        initial_actions: Optional[list] = None,
    ):
        llm = ChatGroq(model=model, temperature=0.0)
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=self.use_vision,
            include_attributes=[],
            max_history_items=6,
            initial_actions=initial_actions or [],
            max_steps=2,
            max_failures=2,
            max_actions_per_step=1,
            step_timeout=45,
            llm_timeout=25,
            flash_mode=flash_mode,
            override_system_message="Eres un navegador. Cumple la tarea.",
        )
        history = await agent.run()
        return history

    async def _fallback_plain(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Modo degradado: headless, sin vision, prompt minimo y modelo chico."""
        browser_fb = Browser(
            headless=True,
            keep_alive=False,
            accept_downloads=False,
            wait_for_network_idle_page_load_time=0.5,
            minimum_wait_page_load_time=0.25,
        )
        task_fb = (
            f"{task}\n"
            "Devuelve solo el primer dato visible en texto plano. "
            "No uses JSON. Responde breve."
        )
        history_fb = await self._run_agent(
            task=task_fb,
            browser=browser_fb,
            model="llama-3.1-8b-instant",
            flash_mode=True,
            initial_actions=context.get("initial_actions") if context else None,
        )
        success_fb = bool(history_fb.is_successful())
        try:
            result_fb = history_fb.last_result[-1].extracted_content  # type: ignore
        except Exception:
            result_fb = ""
        if success_fb:
            log_line("[Fallback] Exito degradado")
            return {"success": True, "result": result_fb, "errors": ["degradado"]}
        log_line("[Fallback] tambien fallo")
        return {"success": False, "result": result_fb, "errors": ["fallback failed"]}

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.browser:
            await self.start()
        assert self.browser is not None

        cfg = ensure_config()
        health = check_vital_signs(cfg.get("profile", "estandar"))

        log_line(f"[Start] Tarea: {task}")
        try:
            history = await self._run_agent(
                task=task,
                browser=self.browser,
                model=self.model,
                flash_mode=True,
                initial_actions=context.get("initial_actions") if context else None,
            )
            success = bool(history.is_successful())
            if success:
                log_line("[Success] Ejecucion primaria completada")
                try:
                    result_text = history.last_result[-1].extracted_content  # type: ignore
                except Exception:
                    result_text = ""
                return {"success": True, "result": result_text, "errors": []}
            # Si no hubo exito, forzamos fallback aunque no haya exception Python
            log_line(f"[Fallback] Forzado por success={history.is_successful()}")
            return await self._fallback_plain(task, context)
        except Exception as exc:
            msg = str(exc)
            schema_err = re.search(r"(response_format|json_schema|Invalid JSON|structured)", msg, re.IGNORECASE)
            if schema_err or "timed out" in msg.lower():
                log_line(f"[Fallback] degradado por error: {exc}")
                return await self._fallback_plain(task, context)
            log_line(f"[Error] no manejado: {exc}")
            return {"success": False, "result": "", "errors": [msg]}

    async def get_screenshot(self) -> bytes | None:
        # browser-use guarda capturas en history; aqui devolvemos None para simplificar
        return None
