@echo off
title AI-Lab Complete Launcher
color 0A

echo ========================================
echo    AI-Lab Complete One-Click Launcher
echo ========================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Check for Python virtual environment
echo [STEP 1/6] Checking Python environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at venv
    echo Please create it with: python -m venv venv
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment found

:: Check for Node.js
echo [STEP 2/6] Checking Node.js installation...
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js
    pause
    exit /b 1
)
echo [SUCCESS] Node.js found

:: Check for Redis
echo [STEP 3/6] Checking Redis installation...
if not exist "redis\redis-server.exe" (
    echo [INFO] Redis not found. Installing Redis...
    
    :: Create Redis directory
    mkdir "redis" 2>nul
    
    :: Download Redis using PowerShell
    echo [INFO] Downloading Redis...
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip' -OutFile 'redis\redis.zip'}"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to download Redis
        pause
        exit /b 1
    )
    
    :: Extract Redis using PowerShell
    echo [INFO] Extracting Redis...
    powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('redis\redis.zip', 'redis')}"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to extract Redis
        pause
        exit /b 1
    )
    
    :: Move files from subdirectory to main directory
    echo [INFO] Setting up Redis...
    move "redis\Redis-x64-3.0.504\*" "redis\"
    rmdir "redis\Redis-x64-3.0.504"
    
    :: Clean up zip file
    del "redis\redis.zip"
    
    echo [SUCCESS] Redis installed
) else (
    echo [SUCCESS] Redis found
)

:: Check for Ollama
echo [STEP 4/6] Checking Ollama installation...
set "OLLAMA_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"

if not exist "%OLLAMA_EXE%" (
    echo [WARNING] Ollama not found at %OLLAMA_EXE%
    echo [INFO] Trying alternative location...
    set "OLLAMA_EXE=ollama.exe"
    where ollama.exe >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] Ollama not found in PATH either
        echo [INFO] Continuing without Ollama (will use echo responses)
        set "OLLAMA_EXE="
    ) else (
        echo [SUCCESS] Ollama found in PATH
    )
) else (
    echo [SUCCESS] Ollama found at: %OLLAMA_EXE%
)

:: Kill any existing processes to prevent conflicts
echo [STEP 5/6] Cleaning up existing processes...
taskkill /F /IM redis-server.exe >nul 2>&1
taskkill /F /IM ollama.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Redis in background
echo [INFO] Starting Redis server...
start "Redis" cmd /c "redis\redis-server.exe"

:: Start Ollama in background if available
if defined OLLAMA_EXE (
    if not "%OLLAMA_EXE%"=="" (
        echo [INFO] Starting Ollama server...
        start "Ollama" cmd /c "%OLLAMA_EXE% serve"
    )
)

:: Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 3 /nobreak >nul

:: Start backend server
echo [INFO] Starting backend server...
start "AI-Lab Backend" cmd /c "cd backend && ..\venv\Scripts\activate.bat && python run_server_direct.py"

:: Wait a moment for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend development server
echo [INFO] Starting frontend server...
start "AI-Lab Frontend" cmd /c "cd frontend && npm start"

:: Wait for frontend server to start
echo [INFO] Waiting for frontend server to start...
timeout /t 15 /nobreak >nul

:: Open browser
echo [INFO] Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo    AI-Lab Project is running!
echo ========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo.
echo You can now chat with the CEO agent!
echo.
echo Close this window when you're done to keep
echo the services running in the background.
echo.

pause 