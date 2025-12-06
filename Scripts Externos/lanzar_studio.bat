@echo off
setlocal enabledelayedexpansion

TITLE Browser Use Studio Launcher (Safe)

rem Guardar ruta del script y movernos a la raiz del proyecto
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."
echo Directorio de trabajo: %cd%

echo =============================================
echo   LIMPIEZA DE PUERTOS Y PROCESOS...
echo =============================================

rem 1) Matar proceso especifico en el puerto 8501 (salida silenciosa)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >NUL 2>&1
)

rem 2) Matar ventanas de Streamlit fantasmas (salida silenciosa)
taskkill /F /FI "WINDOWTITLE eq Streamlit*" /IM python.exe >NUL 2>&1

rem 3) Espera obligatoria para liberar sockets
echo Esperando liberacion de sockets...
timeout /t 3 /nobreak >NUL

echo =============================================
echo   VERIFICANDO ENTORNO...
echo =============================================

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR CRITICO: No encuentro el entorno virtual (.venv\Scripts\activate.bat)
    goto error
)

if not exist "studio\app.py" (
    echo ERROR CRITICO: No encuentro studio\app.py
    goto error
)

echo Activando entorno virtual...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Fallo al activar el entorno virtual.
    goto error
)

echo =============================================
echo   INICIANDO BROWSER USE STUDIO...
echo =============================================
echo.

streamlit run studio/app.py --server.port 8501
if errorlevel 1 (
    echo ERROR: Streamlit finalizo con codigo !errorlevel!
    goto error
)
goto end

:error
echo.
echo Presiona una tecla para cerrar...
pause >NUL
goto :eof

:end
echo.
echo Ejecucion finalizada. Cierra esta ventana si deseas.
pause >NUL
