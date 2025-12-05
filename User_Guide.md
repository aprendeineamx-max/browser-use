# Guía de Usuario para Agente Browser-Use

Esta guía te ayudará a utilizar el agente de navegación web automatizado que hemos configurado. Este programa utiliza inteligencia artificial para controlar un navegador web y realizar tareas por ti.

## 🚀 Cómo Iniciar

### 1. Ejecutar el Agente
Para iniciar el programa, abre tu terminal (PowerShell o CMD) en la carpeta del proyecto y ejecuta:

```powershell
.\venv\Scripts\python agent.py
```

Al hacerlo, verás que se abre una ventana del navegador Chromium y el programa esperará tus instrucciones.

### 2. Modo Interactivo
Hemos actualizado el agente para que funcione en un **bucle infinito**. Esto significa que:
1.  El agente te pedirá una tarea.
2.  Ejecutará la tarea en el navegador.
3.  Al terminar, no se cerrará; te pedirá la siguiente tarea.
4.  Para salir, simplemente escribe `salir` o `exit`.

## ⚙️ configuración

### Claves API (.env)
El comportamiento del agente depende de tus claves API configuradas en el archivo `.env`.
Actualmente está configurado con un sistema de **Respaldo (Fallback)**:

1.  **Principal (Primario):** Intenta usar **Groq** (Modelo Llama 3). Es muy rápido y eficiente.
2.  **Respaldo (Secundario):** Si Groq falla o encuentra un error, cambia automáticamente a **OpenRouter** (Modelo Claude 3.5 Sonnet). Esto asegura que tus tareas se completen incluso si un proveedor tiene problemas.

Puedes editar estas claves abriendo el archivo `.env` en cualquier editor de texto.

## 🛠️ Solución de Problemas

### "El navegador se abre y se cierra"
Si el script termina inesperadamente, revisa el error en la terminal.
*   **Error de Importación:** Asegúrate de estar ejecutando el python dentro del entorno virtual (`.\venv\Scripts\python`).
*   **Error de API Key:** Verifica que las claves en `.env` sean correctas y tengan saldo/créditos.

### Reiniciar el entorno
Si notas comportamientos extraños, a veces ayuda borrar las carpetas `__pycache__` o reinstalar las dependencias, pero por lo general reiniciar el script es suficiente.

## 📝 Ejemplo de Tareas
Aquí hay algunas ideas de qué pedirle al agente:
*   "Ve a amazon.com y busca precios de 'teclado mecánico', guarda los 3 primeros en un archivo."
*   "Entra a wikipedia, busca 'Inteligencia Artificial' y resume el primer párrafo."
*   "Busca vuelos baratos de Madrid a Londres para la próxima semana en Google Flights."

---
**Nota:** El agente controla el navegador como un humano. Si le pides algo complejo, permítele tiempo para "pensar" y navegar paso a paso.
