@echo off
title Lexis AI Launcher

:: ===================================================
:: OPTIONAL: If you haven't set your NVIDIA API key 
:: as a Windows System Variable, you can paste it here.
:: Otherwise, leave it as is, and Windows will use your system variable!
:: set NVIDIA_API_KEY=nvapi-your-key-here
:: ===================================================

echo ===================================================
echo               LEXIS AI ENGINE
echo ===================================================
echo.
echo Starting Backend (API)...
start "Lexis AI Backend" cmd /k "cd /d D:\Lexis Backend\LEXIS_AI && powershell -ExecutionPolicy Bypass -File .\start_backend.ps1"

echo Starting Frontend (UI)...
start "Lexis AI Frontend" cmd /k "cd /d D:\legal-research-engine\frontend && npm run dev"

echo.
echo [!] Both services are starting in separate windows.
echo [!] The frontend will be available at http://localhost:5173
echo.
pause
