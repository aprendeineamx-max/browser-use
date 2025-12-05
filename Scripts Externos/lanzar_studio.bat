@echo off
setlocal ENABLEEXTENSIONS
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
