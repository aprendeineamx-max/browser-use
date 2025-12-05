from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, ValidationError

from .base_engine import AutomationEngine
from .browser_use_engine import BrowserUseEngine
from .stagehand_engine import StagehandEngine
from .snowflake_engine import SnowflakeEngine
from .lavague_engine import LaVagueEngine
from studio.utils.sentinel import ensure_config, check_vital_signs
from browser_use.llm import ChatGroq, ChatOpenRouter
from browser_use.llm.google.chat import ChatGoogle
from studio.utils.planner_settings import load_config

LOG_FILE = Path("Registro_de_logs.txt")
MAX_RETRIES = 3
RETRY_SLEEP = 2  # seconds


def log_line(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[Engine:Orchestrator][{ts}] {message}"
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


class EngineStep(BaseModel):
    engine: Literal["BrowserUseEngine", "SnowflakeEngine", "StagehandEngine", "LaVagueEngine"]
    task: str = Field(description="Tarea específica para el motor seleccionado.")
    context_key: str = Field(description="Clave para guardar el resultado de este paso en el contexto global.")


class EnginePlan(BaseModel):
    plan: List[EngineStep]


class OrchestratorEngine(AutomationEngine):
    """
    Planificador que genera un plan con LLM y ejecuta motores disponibles en secuencia.
    """

    @classmethod
    def is_available(cls) -> bool:
        try:
            import langchain_core  # noqa: F401
            import pydantic  # noqa: F401
        except Exception:
            return False
        return True

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    def available_engines(self) -> Dict[str, Any]:
        engines = {}
        if BrowserUseEngine.is_available():
            engines["BrowserUseEngine"] = BrowserUseEngine
        if StagehandEngine.is_available():
            engines["StagehandEngine"] = StagehandEngine
        if SnowflakeEngine.is_available():
            engines["SnowflakeEngine"] = SnowflakeEngine
        if LaVagueEngine.is_available():
            engines["LaVagueEngine"] = LaVagueEngine
        return engines

    def build_plan_prompt(self, user_task: str, engines: Dict[str, Any]) -> str:
        desc = []
        if "StagehandEngine" in engines:
            desc.append("StagehandEngine: MOTOR PRINCIPAL para navegación, extraccion de datos y acciones rapidas. (Usar para el primer paso).")
        if "BrowserUseEngine" in engines:
            desc.append("BrowserUseEngine: Usar solo para tareas de agentes visuales complejos o si Stagehand falla.")
        if "SnowflakeEngine" in engines:
            desc.append("SnowflakeEngine: consultas SQL y snowflake.cortex.complete.")
        if "LaVagueEngine" in engines:
            desc.append("LaVagueEngine: razonamiento Python con LaVague (soft).")
        available_text = "\n".join(f"- {d}" for d in desc)
        return (
            "Eres un planificador. Devuelve solo JSON con la clave 'plan' que es una lista de pasos.\n"
            "Cada paso tiene: engine (BrowserUseEngine, StagehandEngine, SnowflakeEngine, LaVagueEngine), "
            "task (texto), context_key (identificador para almacenar resultado).\n"
            "Motores disponibles:\n"
            f"{available_text}\n"
            "Reglas:\n"
            "- Usa el menor número de pasos posible.\n"
            "- Usa context_key para encadenar resultados.\n"
            "- Responde SOLO JSON válido.\n"
            f"Tarea del usuario: {user_task}"
        )

    def load_planner_llm(self):
        cfg = load_config()
        planner = cfg.get("orchestrator_planner", "groq:llama-3.1-8b-instant")
        try:
            provider, model = planner.split(":", 1)
        except ValueError:
            provider, model = "groq", "llama-3.1-8b-instant"
        if provider == "openrouter":
            return ChatOpenRouter(model=model, temperature=0.0)
        if provider == "google":
            return ChatGoogle(model=model)
        return ChatGroq(model=model, temperature=0.0)

    async def generate_plan(self, user_task: str, engines: Dict[str, Any]) -> EnginePlan:
        prompt = self.build_plan_prompt(user_task, engines)
        log_line("Generando plan con LLM configurado (structured JSON)")
        llm = self.load_planner_llm()
        completion_obj = await llm.ainvoke(prompt)
        completion = completion_obj.content if hasattr(completion_obj, "content") else str(completion_obj)
        try:
            data = json.loads(completion)
            plan = EnginePlan(**data)
            log_line(f"Plan generado: {plan.json()}")
            return plan
        except (json.JSONDecodeError, ValidationError) as exc:
            log_line(f"Error parseando plan: {exc}; se usa plan simple")
            fallback_engine = "BrowserUseEngine" if "BrowserUseEngine" in engines else next(iter(engines.keys()))
            return EnginePlan(plan=[EngineStep(engine=fallback_engine, task=user_task, context_key="final")])

    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        cfg = ensure_config()
        check_vital_signs(cfg.get("profile", "estandar"))
        engines = self.available_engines()
        if not engines:
            msg = "No hay motores disponibles para orquestar"
            log_line(f"[Error] {msg}")
            return {"success": False, "result": "", "errors": [msg]}

        plan = await self.generate_plan(task, engines)
        global_ctx: Dict[str, Any] = {}
        results = []
        for step in plan.plan:
            engine_cls = engines.get(step.engine)
            if not engine_cls:
                log_line(f"Motor {step.engine} no disponible en tiempo de ejecución")
                results.append({"engine": step.engine, "error": "no disponible"})
                continue
            eng = engine_cls()
            updated_task = step.task
            for key, val in global_ctx.items():
                placeholder = f"{{{key}}}"
                if placeholder in updated_task:
                    updated_task = updated_task.replace(placeholder, str(val))
            attempt_result = None
            for i in range(MAX_RETRIES):
                log_line(f"Ejecutando paso con {step.engine} (intento {i+1}/{MAX_RETRIES}): {updated_task}")
                res = await eng.execute_task(updated_task, context)
                if res.get("success"):
                    attempt_result = res
                    break
                else:
                    log_line(f"Intento {i+1} fallido en {step.engine}: {res.get('errors')}")
                    if i < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_SLEEP)
            await eng.stop()
            if attempt_result:
                global_ctx[step.context_key] = attempt_result.get("result")
                results.append({"engine": step.engine, "result": attempt_result})
            else:
                results.append({"engine": step.engine, "result": res})
                log_line(f"Paso fallido definitivo en {step.engine}: {res.get('errors')}")
                return {"success": False, "result": res, "errors": res.get("errors"), "plan": plan.dict(), "trace": results}

        final_result = results[-1]["result"] if results else {}
        return {"success": True, "result": final_result, "errors": [], "plan": plan.dict(), "trace": results}

    async def get_screenshot(self) -> bytes | None:
        return None
