@echo off
title AI-Lab Project Launcher
color 0A

echo ========================================
echo    AI-Lab Project One-Click Launcher
echo ========================================
echo.

:: Check for common Ollama installation paths
set "OLLAMA_EXE="

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"
    goto :ollama_found
)

if exist "C:\Program Files\Ollama\ollama.exe" (
    set "OLLAMA_EXE=C:\Program Files\Ollama\ollama.exe"
    goto :ollama_found
)

if exist "C:\Program Files (x86)\Ollama\ollama.exe" (
    set "OLLAMA_EXE=C:\Program Files (x86)\Ollama\ollama.exe"
    goto :ollama_found
)

echo [ERROR] Ollama not found! Please install Ollama from https://ollama.ai
echo        Or update the OLLAMA_EXE path in this script.
pause
exit /b 1

:ollama_found
echo [INFO] Found Ollama at: %OLLAMA_EXE%

:: Kill any existing Ollama processes
echo [STEP 1/6] Stopping existing Ollama processes...
taskkill /F /IM ollama.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Ollama server
echo [STEP 2/6] Starting Ollama server...
start /B "" "%OLLAMA_EXE%" serve
timeout /t 5 /nobreak >nul

:: Test Ollama connection
echo [STEP 3/6] Testing Ollama connection...
powershell -command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 10 | Out-Null; Write-Host '[SUCCESS] Ollama server is running' -ForegroundColor Green } catch { Write-Host '[ERROR] Failed to connect to Ollama server' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Ollama server failed to start. Please check your installation.
    pause
    exit /b 1
)

:: Pull the Mistral model
echo [STEP 4/6] Ensuring Mistral model is available...
echo [INFO] Pulling/updating Mistral model...
"%OLLAMA_EXE%" pull mistral

:: Activate virtual environment and install dependencies
echo [STEP 5/6] Setting up Python environment...
if not exist "win-venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found! Please run: python -m venv win-venv
    pause
    exit /b 1
)

call win-venv\Scripts\activate.bat
echo [INFO] Installing/updating dependencies...
python -m pip install --user -r requirements.txt >nul 2>&1

:: Start the Streamlit web interface
echo [STEP 6/6] Launching AI-Lab interface...
echo.
echo ========================================
echo    Starting AI-Lab Web Interface...
echo    URL: http://localhost:8501
echo ========================================
echo.

:: Open browser after a short delay
timeout /t 3 /nobreak >nul
start http://localhost:8501

:: Run Streamlit (this will keep the window open)
streamlit run app.py --server.headless=true

:: If we get here, Streamlit has stopped
echo.
echo [INFO] AI-Lab interface has stopped.
pause