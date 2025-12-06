@echo off
setlocal
cd /d "%~dp0\.."

echo ==================================================
echo   PROTOCOLO DE LIMPIEZA Y LANZAMIENTO (V3)
echo ==================================================

echo [1/4] Buscando procesos en puerto 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501" ^| find "LISTENING"') do (
    echo     - Matando PID: %%a
    taskkill /F /PID %%a >NUL 2>&1
)

echo [2/4] Limpiando procesos de Streamlit huerfanos...
taskkill /F /IM "streamlit.exe" >NUL 2>&1
taskkill /F /FI "WINDOWTITLE eq Streamlit*" /IM python.exe >NUL 2>&1

echo [3/4] Esperando liberacion de sockets (3s)...
timeout /t 3 /nobreak >NUL

echo [4/4] Iniciando Browser Use Studio...
call .venv\Scripts\activate
start "Browser Use Studio" /MAX streamlit run studio/app.py --server.port 8501

echo.
echo    [EXITO] La aplicacion se ha lanzado en una nueva ventana.
echo    Puedes cerrar esta consola.
echo.
pause
