@echo off
REM SaludApp Peru — Windows Launcher
REM Set encoding y keys antes de ejecutar Streamlit

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Cargar keys desde .env si existe
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%b"=="" set %%a=%%b
    )
)

echo.
echo 💊 SaludApp Peru — Iniciando...
echo Local URL: http://localhost:8501
echo.

streamlit run frontend/app.py --server.port 8501 --server.headless=false

pause
