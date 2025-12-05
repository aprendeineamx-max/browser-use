# Browser Use Studio (Prometheus Edition)

Automatiza la web con agentes y navegador real, ahora con arquitectura multi‑motor y un generador de scripts basado en motores (BrowserUse estable, Skyvern experimental).

## Instalación rápida
```bash
python -m venv .venv
.\.venv\Scripts\activate  # en Windows
python -m pip install --upgrade pip
pip install -r requirements.txt  # o pip install browser-use streamlit
python -m playwright install chromium  # si usas playwright/skyvern más adelante
```

## Arquitectura
- `studio/engines/`: capa de motores.
  - `browser_use_engine.py`: motor estable con fallback y logging en `Registro_de_logs.txt`.
  - `skyvern_engine.py`: mock experimental (conexión Docker simulada).
- `studio/pages/`: UI Streamlit (Key Tester, Script Manager, Block Builder y Engine Lab).
- `Scripts Automaticos/`: scripts generados listos para ejecución por motor.

## Uso
```bash
.\.venv\Scripts\activate
streamlit run studio/app.py
```
UI principal:
- **Key tester**: valida llaves de LLM.
- **Script manager / Block builder**: diseña flujos y ahora genera scripts usando `BrowserUseEngine`.
- **Engine lab**: selecciona motor (BrowserUse/Skyvern mock) y ejecuta tareas rápidas.

### Requisito para motor Stagehand
- Necesitas **Node.js** instalado (ej. v18+; detectamos v24 en este entorno).
- El puente `studio/bridge_stagehand/` instala `@browserbasehq/stagehand`, `playwright`, `dotenv` y un `runner.js` que consume el motor desde Node.

## Generador basado en motores
El Block Builder ya no instancia `Agent` directo: los scripts nuevos importan `BrowserUseEngine` para heredar resiliencia, logging y fallback.

## Variables y datos
El builder soporta datos externos (CSV/Excel/JSON) e interpolación. Los scripts generados incluyen una recomendación de ejecutar via `BrowserUseEngine` para máxima robustez.

## Desarrollo
- Logs en `Registro_de_logs.txt`.
- Protocolos: adjunta últimas líneas de log en cada entrega y usa commits descriptivos en español.

## Futuro
Extender la arquitectura multi‑motor (Skyvern, Stagehand, LaVague) siguiendo `docs/ARCHITECTURE_FUTURE.md`.
