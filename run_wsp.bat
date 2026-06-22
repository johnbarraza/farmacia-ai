@echo off
echo 💊 SaludApp Peru — DEMO WHATSAPP REAL
echo ======================================
echo.
echo Este script inicia:
echo   1. FastAPI backend (puerto 8000)
echo   2. Streamlit web app (puerto 8501)
echo   3. WhatsApp Gateway con Baileys
echo.
echo ESCANEÁ el QR con tu WhatsApp personal.
echo MANDATE un mensaje o foto de receta a vos mismo.
echo El bot responde automáticamente.
echo.
echo Ctrl+C para detener todo.
echo.

start "SaludApp-API" cmd /c "cd E:\github\saludapp-peru && uvicorn backend.app.main:app --port 8000 --reload"
timeout /t 3 /nobreak >nul

start "SaludApp-Web" cmd /c "cd E:\github\saludapp-peru && streamlit run frontend/app.py"

echo.
echo 🔌 Iniciando WhatsApp Gateway...
echo.

cd E:\github\saludapp-peru\ai
node baileys_gateway.js

pause
