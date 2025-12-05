# Snowflake Cortex como proveedor LLM para Browser Use Studio

## Objetivo
Aprovechar los $400 USD de créditos Snowflake para inferencia LLM vía Cortex y reducir costos en OpenRouter/Groq.

## ¿Qué es Snowflake Cortex?
- Servicio administrado de Snowflake que expone modelos vía SQL (SQL functions) y API externas.
- Permite usar modelos propios de Snowflake y enrutar hacia proveedores externos desde el mismo entorno de datos.

## Estrategia de Integración
1) **Autenticación**  
   - Crear un usuario/API key o usar autenticación por nombre de usuario/contraseña + role con permisos para invocar funciones Cortex.  
   - Guardar credenciales en `.env` como `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`.

2) **Cliente Python**  
   - Dependencia: `snowflake-connector-python`.  
   - Conexión típica:
     ```python
     import snowflake.connector
     conn = snowflake.connector.connect(
         user=USER,
         password=PASSWORD,
         account=ACCOUNT,
         warehouse=WAREHOUSE,
         database=DATABASE,
         schema=SCHEMA,
     )
     ```

3) **Invocar modelos Cortex**  
   - Vía SQL, por ejemplo:
     ```sql
     select snowflake.cortex.complete(
       'llama3-70b',
       {'messages': [{'role':'user','content':'Dime el clima en Madrid'}]}
     ) as resp;
     ```
   - Modelos soportados incluyen variantes de Llama, Mistral, etc. (ver docs actualizadas en Snowflake).

4) **Integración en el Hub de Motores**  
   - Crear `SnowflakeEngine` heredando de `AutomationEngine` que:
     - `is_available`: verifica que el conector está instalado y que las variables Snowflake están presentes.
     - `execute_task`: abre conexión, ejecuta el SQL `snowflake.cortex.complete` y devuelve el texto de la respuesta.
   - Incluirlo en `99_engine_lab.py` y en el Builder como motor experimental.

5) **Costos y Límites**  
   - Los créditos se consumen por tiempo/uso de warehouse y llamadas a Cortex.  
   - Configurar warehouse pequeño (XS) para pruebas.  
   - Monitorear consumo en el panel de Snowflake para no exceder los $400.

6) **Ventajas**  
   - Menor latencia si los datos están ya en Snowflake.  
   - Centralizar facturación en Snowflake en lugar de múltiples proveedores.

7) **Riesgos**  
   - Requiere warehouse activo (costo por tiempo).  
   - Posible latencia extra si se usa desde fuera de la región del warehouse.  
   - Modelos y límites cambian con el tiempo; validar lista de modelos antes de exponer en UI.

## Próximos pasos
- Añadir `snowflake-connector-python` de manera opcional (instalación condicional).
- Implementar `SnowflakeEngine` y exponerlo en el Hub con detección suave.
- Agregar en el Key Tester una sección para probar credenciales y hacer un `snowflake.cortex.complete` de 1 token como ping.
