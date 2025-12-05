## Browser Use Studio Roadmap

### Estado (2025-12-05)
- [x] Refactor a `studio/` (app y pages reubicadas)
- [x] Builder base (navegar/scroll/click/input) y gestor de scripts
- [x] Integración de variables dinámicas en prompts (CSV/Excel/JSON vía builder)
- [x] Fase 4 E2E: validada con fallback degradado y logging centralizado

### Siguientes pasos
- Integrar soporte avanzado de bloques (XPath/CSS ya ok; agregar parsing inverso a bloques).
- UX híbrida: modo básico/avanzado, configuraciones de headers/proxy/anti-detect/trace.
- Probar modelos con soporte `response_format` o desactivar schema para evitar 400 en OpenRouter/Groq.

## PROTOCOLOS DE RESPUESTA OBLIGATORIOS
- Evidencia de logs: Toda respuesta técnica debe cerrar adjuntando las últimas líneas de `Registro_de_logs.txt`.
- Gestión de versiones: Si hubo cambios de código, siempre facilitar bloque listo para copiar/pegar con `git add .`, `git commit -m "... (en español)"`, `git push`.
- Idioma commits: Mensajes descriptivos en español.

## Fase 1-4 (Prometheus)
- [x] Refactor a studio/ (app y pages reubicadas)
- [x] Builder base + gestor de scripts
- [x] Variables dinámicas en prompts (CSV/Excel/JSON)
- [x] Resiliencia/Fallback en BrowserUseEngine y generación de scripts usando motor
- [x] Multi-motor base (Skyvern mock) y README Prometheus

## Fase 2: Integración LAM (Skyvern/Stagehand)
- [x] Stagehand nativo (Node) integrado y operativo
- [x] Skyvern mock standby (falta Docker, documentado en `docs/DOCKER_STRATEGY.md`)

## Fase 4: Integración LaVague
- [x] Detección suave e instalación condicional
- [x] Motor disponible en hub y UI

## Fase 4B: Sentinel y gestión de recursos
- [x] Perfiles (ligero/estándar/sin_límite) con psutil y GC
- [x] Config persistente en `studio/config.json` y UI en `98_settings.py`

## Arquitectura Hub Universal
- [x] Hub con motores BrowserUse, Stagehand, LaVague y Skyvern (standby por Docker)
- [x] Engine Lab y Builder seleccionan motor disponible dinámicamente

## Fase 6: Integración LangChain/Orquestación Compleja (futuro)
- [ ] Pendiente de diseño y priorización
