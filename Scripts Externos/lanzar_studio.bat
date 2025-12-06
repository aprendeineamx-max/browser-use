@echo off
setlocal ENABLEEXTENSIONS

echo Limpiando procesos Streamlit (puerto 8501)...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Streamlit*" >NUL 2>&1
echo Limpieza de puerto/procesos completada.

set "SCRIPT_DIR=%~dp0"
echo.
echo =============================================
echo   INICIANDO BROWSER USE STUDIO...
echo =============================================
pushd "%SCRIPT_DIR%.."
start "" /B ".\.venv\Scripts\streamlit" run studio/app.py --server.port 8501
if errorlevel 1 (
  echo Hubo un error al lanzar Streamlit.
  pause
)
popd
pause
