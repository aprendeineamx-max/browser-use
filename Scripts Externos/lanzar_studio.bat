@echo off
setlocal ENABLEEXTENSIONS

echo Limpiando puerto 8501...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do taskkill /PID %%a /F >NUL 2>&1
echo Puerto 8501 liberado.

set "SCRIPT_DIR=%~dp0"
echo.
echo =============================================
echo   INICIANDO BROWSER USE STUDIO...
echo =============================================
pushd "%SCRIPT_DIR%.."
call ".venv\Scripts\activate.bat"
streamlit run studio/app.py --server.port 8501
if errorlevel 1 (
  echo Hubo un error al lanzar Streamlit.
  pause
)
popd
pause
