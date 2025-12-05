## Estrategia Docker / Infra para Motores LAM (Skyvern, LaVague, Stagehand)

### Evaluación Rápida
- **Skyvern**: orientado a Playwright + contenedor propio. En Windows es preferible usar Docker; pip nativo suele requerir Node/Playwright y puede romperse por dependencias binarias. Recomendación: Docker Desktop + WSL2 habilitado.
- **LaVague**: Python-first pero depende de Playwright/Selenium. En Windows es viable con pip, pero la ruta más estable sigue siendo Docker/WSL2 para aislar navegadores y dependencias de sistema.
- **Stagehand**: similar a Playwright; en Windows es posible pero con riesgo de incompatibilidades de Chromium. Mejor en contenedor.

### Riesgos
- Playwright en Docker: el contenedor suele traer Chromium; si además instalas Playwright local, podrías duplicar descargas. Debe definirse un único runtime (contenedor).
- Recursos: navegadores en contenedores consumen más RAM/CPU; se necesita ajustar límites y limpiar sesiones.
- Red/bloqueos: Los contenedores necesitan salida a internet; proxys o firewalls pueden bloquear CDP/puertos expuestos.

### Recomendación de Preparación en Windows
1) Instalar Docker Desktop.
2) Habilitar WSL2 y asegurarse de que Docker usa el backend WSL.
3) Verificar virtualización (BIOS) y 4GB+ de RAM libre para contenedores con Chromium.
4) Probar `docker run hello-world` y `docker run mcr.microsoft.com/playwright/python:latest` para validar acceso a red y gráficos en modo headless.
5) Mantener `.env` con llaves LLM; no las hornees en la imagen.

### Pasos Siguientes (cuando se integre código)
- Definir imagen base (p.ej. `mcr.microsoft.com/playwright/python:latest`) con dependencias Skyvern/LaVague.
- Exponer puerto CDP o API del motor.
- Añadir scripts de arranque en `studio/engines/` para seleccionar motor remoto (Docker) vs local.
