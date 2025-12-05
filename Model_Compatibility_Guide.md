# Guía de Compatibilidad de Modelos para Browser Use

Esta guía detalla los modelos de Inteligencia Artificial probados y recomendados para usar con el repositorio `browser-use`. Se centra en la estabilidad, costo y capacidad de visión.

---

## 🏆 Modelos Verificados (Recomendados)

Estos modelos han sido probados en nuestro entorno y funcionan correctamente con la librería instalada.

### 1. **Gemini 2.0 Flash (`gemini-2.0-flash`)**  🌟 **RECOMENDADO**
- **Estado:** ✅ Estable
- **Proveedor:** Google (Gratis con límites generosos)
- **Ventajas:**
  - **Visión Nativa:** Entiende capturas de pantalla a la perfección.
  - **Velocidad:** Muy rápida respuesta.
  - **Estabilidad:** No sufre de los errores de cuota (`429`) tan frecuentes como la versión "Experimental".
  - **Costo:** Gratuito (Free Tier) para uso moderado.
- **Desventajas:**
  - Ligeramente menos capaz en razonamiento complejo que modelos "Pro".
- **Uso:** Ideal para la mayoría de scripts de automatización.

### 2. **Gemini 1.5 Flash (`gemini-1.5-flash`)**
- **Estado:** ⚠️ Condicional
- **Problema:** En versiones recientes de la librería, usar el string exacto `gemini-1.5-flash` puede dar error `404 NOT_FOUND` si no está mapeado internamente.
- **Solución:** Usar `gemini-2.0-flash` o verificar la lista de modelos soportados en `browser_use/llm/google/chat.py`.

### 3. **Gemini 2.0 Flash Experimental (`gemini-2.0-flash-exp`)**
- **Estado:** ❌ Inestable (Cuotas)
- **Problema:** Aunque es muy capaz, Google impone límites de tasa muy bajos (Requests Per Minute). Es común recibir errores `429 RESOURCE_EXHAUSTED` en scripts largos.
- **Uso:** Solo para pruebas unitarias muy cortas.

---

## 🌍 Otros Proveedores (Requieren sus propias API Keys)

Si tienes claves de pago, estos modelos son excelentes alternativas.

### 1. **OpenAI GPT-4o (`gpt-4o`)**
- **Estado:** ✅ Excelente
- **Proveedor:** OpenAI
- **Ventajas:** El estándar de oro en razonamiento y visión. Muy fiable para tareas complejas.
- **Desventajas:** Costo por token (no es gratis).
- **Configuración:** Requiere `OPENAI_API_KEY` en `.env`.

### 2. **Anthropic Claude 3.5 Sonnet (`claude-3-5-sonnet-20240620`)**
- **Estado:** ✅ Sobresaliente
- **Proveedor:** Anthropic
- **Ventajas:** Especializado en "Computer Use". A menudo supera a GPT-4 en navegación web.
- **Desventajas:** Costo por token.
- **Configuración:** Requiere `ANTHROPIC_API_KEY` en `.env`.

---

## ⚙️ Guía de Configuración

### 1. Dónde poner las Keys (`.env`)
El archivo `.env` es donde guardas tus secretos. Nunca lo compartas.

```bash
# Archivo: .env
# Google (Gemini) - GRATIS y Recomendado
GOOGLE_API_KEY=AIzaSy...

# OpenAI (Opcional)
OPENAI_API_KEY=sk-...

# Anthropic (Opcional)
ANTHROPIC_API_KEY=sk-ant-...

# Groq (Opcional - Cuidado con falta de visión)
GROQ_API_KEY=gsk_...
```

### 2. Cómo configurar el Modelo en Python
Para cambiar de modelo, solo debes cambiar la clase `llm` que instancias en tu script (ej. `agent.py` o scripts automáticos).

#### **Opción A: Usar Google Gemini (Gratis)**
```python
from browser_use.llm.google.chat import ChatGoogle
import os

llm = ChatGoogle(
    model="gemini-2.0-flash", # <--- CAMBIA EL NOMBRE AQUÍ
    api_key=os.getenv("GOOGLE_API_KEY"),
)
```

#### **Opción B: Usar OpenAI (GPT-4o)**
```python
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)
```

#### **Opción C: Usar Anthropic (Claude)**
```python
from langchain_anthropic import ChatAnthropic
import os

llm = ChatAnthropic(
    model_name="claude-3-5-sonnet-20240620",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
```

---

## 🚨 Resumen de Capacidades

| Modelo | Visión? | Gratis? | Estabilidad | Recomendado para... |
| :--- | :---: | :---: | :---: | :--- |
| **Gemini 2.0 Flash** | ✅ Sí | ✅ Sí | Alta | **Todo uso general** |
| Gemini 2.0 Flash Exp | ✅ Sí | ✅ Sí | Baja (429) | Pruebas rápidas |
| GPT-4o | ✅ Sí | ❌ No | Muy Alta | Tareas críticas/complejas |
| Claude 3.5 Sonnet | ✅ Sí | ❌ No | Muy Alta | Navegación experta |
| Llama 3 (Groq) | ❌ No* | ✅ Sí | Alta | Tareas solo texto (limitado) |

*\*Nota: Los modelos de Groq suelen ser muy rápidos pero a menudo carecen de capacidad de visión nativa (analizar capturas de pantalla), lo que dificulta mucho la navegación web.*
