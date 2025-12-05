# Guia de Usuario para Agente Browser-Use

Esta guia te ayudara a utilizar el agente de navegacion web automatizado que hemos configurado. Este programa utiliza inteligencia artificial para controlar un navegador web y realizar tareas por ti.

## Como Iniciar

### 1. Ejecutar el Agente
En la carpeta del proyecto:
```powershell
.\venv\Scripts\python agent.py
```
Se abrira el navegador Chromium y el programa esperara tus instrucciones.

### 2. Modo Interactivo
El agente funciona en un **bucle infinito**:
1. Pide una tarea.
2. Ejecuta la tarea en el navegador.
3. Al terminar, no se cierra; pide la siguiente tarea.
4. Para salir, escribe `salir` o `exit`.

## Configuracion

### Claves API (.env)
El comportamiento del agente depende de tus claves en `.env`. Esta configurado con **fallback**:
1) **Primario:** Groq (modelo configurado en `.env`). Rapido y eficiente.
2) **Secundario:** OpenRouter, usado si Groq falla.
3) **Browser Use Cloud:** `BROWSER_USE_API_KEY` permite usar navegador en la nube (`use_cloud=True`) para menor latencia y sin depender de Chrome local.

Puedes editar las claves en `.env`.

## Solucion de Problemas

### "El navegador se abre y se cierra"
- Revisa la terminal.
- **Importacion:** Ejecuta Python dentro del entorno virtual (`.\venv\Scripts\python`).
- **API Key:** Verifica que las claves en `.env` sean correctas y tengan saldo/creditos.

### Reiniciar el entorno
Si hay comportamientos extranos, borrar `__pycache__` o reinstalar dependencias puede ayudar. A menudo basta con reiniciar el script.

## Ejemplo de Tareas
- "Ve a amazon.com y busca precios de 'teclado mecanico', guarda los 3 primeros en un archivo."
- "Entra a wikipedia, busca 'Inteligencia Artificial' y resume el primer parrafo."
- "Busca vuelos baratos de Madrid a Londres para la proxima semana en Google Flights."

---
**Nota:** El agente controla el navegador como un humano. En tareas complejas, dale tiempo para pensar y navegar.

## Backlog / Tareas futuras
- Disenar failover manual de multiples API keys por proveedor (Groq, OpenRouter):
  - Guardar claves alternativas en `.env` (`GROQ_API_KEY_ALT_*`, `OPENROUTER_API_KEY_ALT_*`).
  - Implementar rotacion en el cliente: ante 401/403/429 recrear el LLM con la siguiente clave disponible.
  - Registrar metricas de fallos y clave activa para auditoria.
  - Evitar rotacion circular infinita; detener tras agotar pool y reportar error estructurado.
