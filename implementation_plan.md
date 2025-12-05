## Browser Use Studio Roadmap
### Estado (2025-12-05)
- [x] Refactor a studio/ (app y pages reubicadas)
- [x] Builder base (blocks navegar/scroll/click/input) y gestor de scripts.
- [x] Integracion de variables dinamicas en prompts (CSV/Excel/JSON via builder)
- [ ] Fase 4 E2E: en progreso (fallos de provider: 400 json_schema y 413 Groq; se registraron en `Registro_de_logs.txt`)

### Siguientes pasos
- Integrar soporte avanzado de bloques (XPath/CSS ya ok; agregar fallback de proveedor y parsing inverso a bloques).
- UX hibrida: modo basico/avanzado, configuraciones de headers/proxy/anti-detect/trace.
- Integrar LAM emergentes (Skyvern, Stagehand, LaVague) como herramientas (investigacion).
- Investigar y probar modelos con soporte para `response_format` o desactivar schema para evitar 400 en OpenRouter/Groq.

## PROTOCOLOS DE RESPUESTA OBLIGATORIOS
- Evidencia de logs: Toda respuesta tecnica debe cerrar adjuntando las ultimas 5-10 lineas de `Registro_de_logs.txt`.
- Gestion de versiones: Si hubo cambios de codigo, siempre facilitar bloque listo para copiar/pegar con `git add .`, `git commit -m "... (en español)"`, `git push`.
- Idioma commits: Mensajes descriptivos en español.
