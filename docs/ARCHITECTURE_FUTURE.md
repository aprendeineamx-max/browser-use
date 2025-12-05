## Arquitectura Futura: Motores Múltiples (Browser-Use, Skyvern, Stagehand, LaVague)

### Objetivo
Evolucionar **Browser Use Studio** a una plataforma que permita seleccionar el motor de ejecución (Execution Engine) antes de lanzar un flujo: `Browser-Use` (actual), `Skyvern`, `Stagehand`, `LaVague` u otros LAM. La UI deberá ofrecer un selector de motor y parámetros específicos por motor sin duplicar lógica.

### Principios de Diseño
- **Abstracción por interfaz**: definir una capa `engine` con una interfaz común (p. ej. `run_task(task: str, config: EngineConfig) -> ExecutionResult`). Cada motor implementa la interfaz en un módulo aislado.
- **Configuración desacoplada**: los parámetros específicos de cada motor se declaran en esquemas Pydantic y se serializan/deserializan desde la UI (Streamlit) sin mezclar lógica de UI con lógica de ejecución.
- **Inyección de dependencias**: el builder genera scripts que importan la interfaz y resuelven el motor en tiempo de ejecución según la selección del usuario.
- **Fallback controlado**: permitir que un flujo intente un motor y, ante error recuperable, reintente con otro (p. ej. Browser-Use → LaVague).

### Estructura Propuesta
```
studio/
  engines/
    __init__.py
    browser_use_engine.py
    skyvern_engine.py
    stagehand_engine.py
    lavague_engine.py
  models/
    engine_config.py        # Pydantic: campos comunes (provider, model, headless, proxies, timeouts)
    browser_use_config.py   # Campos específicos (use_cloud, include_attributes, vision, etc.)
    skyvern_config.py       # Campos propios (playwright channel, docker target, auth)
    stagehand_config.py     # Campos propios (tool registry, server endpoints)
    lavague_config.py       # Campos propios (navigator settings, retries)
```

### Requisitos por Motor (altos niveles)
- **Browser-Use (actual)**: Python 3.11+, dependencia `browser-use`. Opcional: `chromium` instalado o `use_cloud=True`. Usa CDP; requiere permisos de red.
- **Skyvern**: tipicamente requiere Docker (levanta contenedor con Playwright y servidor). Depende de Playwright (Chromium/Firefox/WebKit). Python wrapper para llamar endpoints. Requiere puertos expuestos y manejo de sesiones.
- **Stagehand**: biblioteca Python; puede necesitar Playwright + Node en segundo plano. Revisar compatibilidad de versiones (Playwright 1.42+). Requiere credenciales de modelo LLM.
- **LaVague**: framework Python para navegación con LLM. Depende de Playwright o Selenium. Requiere Python ≥3.9 y model providers configurables.

### Ajustes en la UI
- Selector de motor: `st.selectbox(["Browser-Use", "Skyvern", "Stagehand", "LaVague"])`.
- Campos dinámicos: mostrar únicamente los parámetros del motor seleccionado (p. ej. `use_cloud`, `cdp_url` para Browser-Use; `server_url`, `api_token` para Skyvern).
- Validación: cada conjunto de campos se valida con su modelo Pydantic y devuelve errores en vivo.

### Flujo de Ejecución Unificado
1. El builder genera un `ExecutionConfig` (motor + parámetros + bloques + datos externos).
2. El `engine_router` resuelve el motor y llama al adaptador correspondiente.
3. Cada adaptador traduce los bloques a acciones del motor (p. ej. para Skyvern, construir un plan Playwright; para Browser-Use, crear `Agent`).
4. El resultado se normaliza en `ExecutionResult` (status, logs, errores, evidencia).

### Roadmap Inmediato
- Crear `studio/engines/browser_use_engine.py` como referencia (usa el código actual del runner).
- Agregar selector de motor en UI y pasar configuración a los scripts generados.
- Documentar dependencias externas requeridas (Docker/Playwright) antes de habilitar Skyvern/Stagehand/LaVague.

