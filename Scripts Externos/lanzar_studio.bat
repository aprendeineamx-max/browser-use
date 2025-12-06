@echo off
setlocal enabledelayedexpansion

TITLE Browser Use Studio Launcher

echo =============================================
echo   LIMPIEZA DE PUERTOS Y PROCESOS...
echo =============================================

:: 1. Matar proceso especifico en el puerto 8501
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501" ^| find "LISTENING"') do (
    echo Matando proceso en puerto 8501 (PID: %%a)...
    taskkill /F /PID %%a >NUL 2>&1
)

:: 2. Matar ventanas de Streamlit fantasmas
taskkill /F /FI "WINDOWTITLE eq Streamlit*" /IM python.exe >NUL 2>&1

:: 3. ESPERA OBLIGATORIA (Para que Windows libere el puerto)
echo Esperando liberacion de sockets...
timeout /t 3 /nobreak >NUL

echo.
echo =============================================
echo   INICIANDO BROWSER USE STUDIO...
echo =============================================
echo.

:: Detectar ruta del script y activar entorno
cd /d "%~dp0\.."
call .venv\Scripts\activate

:: Lanzar app (Si falla, pausa para ver el error)
streamlit run studio/app.py --server.port 8501 || pause
