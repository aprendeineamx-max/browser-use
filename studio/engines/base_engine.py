from __future__ import annotations

import abc
from typing import Any, Dict


class AutomationEngine(abc.ABC):
    """
    Contrato base para motores de automatizacion.
    Cada motor (Browser-Use, Skyvern, Stagehand, LaVague) debe implementar estos metodos.
    """

    @abc.abstractmethod
    async def start(self) -> None:
        """Inicializa recursos (browser, cliente HTTP, etc.)."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Libera recursos."""

    @abc.abstractmethod
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una tarea de navegacion/automatizacion.
        Debe devolver un dict con al menos: {"success": bool, "result": str, "errors": list[str]}.
        """

    @abc.abstractmethod
    async def get_screenshot(self) -> bytes | None:
        """Devuelve una captura de pantalla en bytes si aplica; de lo contrario None."""
