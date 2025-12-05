from __future__ import annotations

from typing import Any, Dict, Optional

from browser_use import Agent, Browser
from browser_use.llm import ChatGroq

from .base_engine import AutomationEngine


class BrowserUseEngine(AutomationEngine):
    """
    Implementacion de AutomationEngine usando browser-use (motor actual).
    Nota: Esta clase no esta cableada en la UI aun; sirve como primer ladrillo para multi-motor.
    """

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

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.browser:
            await self.start()

        llm = ChatGroq(model=self.model, temperature=0.0)
        agent = Agent(
            task=task,
            llm=llm,
            browser=self.browser,
            use_vision=self.use_vision,
            include_attributes=[],
            max_history_items=6,
            flash_mode=True,
        )
        history = await agent.run()
        success = bool(history.is_successful())
        result_text = ""
        try:
            result_text = history.last_result[-1].extracted_content  # type: ignore
        except Exception:
            result_text = ""

        return {
            "success": success,
            "result": result_text,
            "errors": [] if success else ["execution failed"],
        }

    async def get_screenshot(self) -> bytes | None:
        # browser-use guarda capturas en history; aqui devolvemos None para simplificar
        return None
