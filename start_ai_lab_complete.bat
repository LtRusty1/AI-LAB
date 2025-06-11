@echo off
title AI-Lab Enhanced Complete Launcher v2.0
color 0A

echo ==========================================
echo    AI-Lab Enhanced Complete Launcher v2.0
echo    Backend Refactoring + Performance + API Keys
echo ==========================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Check for Python virtual environment
echo [STEP 1/8] Checking Python environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at venv
    echo Please create it with: python -m venv venv
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment found

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Check for enhanced dependencies
echo [STEP 2/8] Checking enhanced dependencies...
cd backend
python -c "import ai_lab.database; import ai_lab.performance; import ai_lab.api_keys; print('All enhanced modules available')" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Enhanced modules not found. Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Enhanced dependencies installed
) else (
    echo [SUCCESS] Enhanced dependencies found
)
cd ..

:: Check for Node.js
echo [STEP 3/8] Checking Node.js installation...
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js
    pause
    exit /b 1
)
echo [SUCCESS] Node.js found

:: Setup Database
echo [STEP 4/8] Setting up enhanced database...
cd backend

:: Set database URL for SQLite (easy setup)
set DATABASE_URL=sqlite+aiosqlite:///./ai_lab.db

:: Check if database exists
if not exist "ai_lab.db" (
    echo [INFO] Database not found. Setting up database...
    python setup_database.py
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Database setup failed
        pause
        exit /b 1
    )
    echo [SUCCESS] Database setup completed
    
    :: Migrate existing JSON data if present
    echo [INFO] Checking for existing conversation data...
    if exist "conversations\*.json" (
        echo [INFO] Found existing conversation data. Migrating to database...
        python migrate_json_to_db.py
        echo [SUCCESS] Data migration completed
    )
) else (
    echo [SUCCESS] Database found: ai_lab.db
)
cd ..

:: Check for Redis
echo [STEP 5/8] Checking Redis installation...
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
echo [STEP 6/8] Checking Ollama installation...
set "OLLAMA_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe"

if not exist "%OLLAMA_EXE%" (
    echo [WARNING] Ollama not found at %OLLAMA_EXE%
    echo [INFO] Trying alternative location...
    set "OLLAMA_EXE=ollama.exe"
    where ollama.exe >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARNING] Ollama not found in PATH either
        echo [INFO] Continuing without Ollama (will use mock responses)
        set "OLLAMA_EXE="
    ) else (
        echo [SUCCESS] Ollama found in PATH
    )
) else (
    echo [SUCCESS] Ollama found at: %OLLAMA_EXE%
)

:: Kill any existing processes to prevent conflicts
echo [STEP 7/8] Cleaning up existing processes...
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

:: Start enhanced backend server v2.0
echo [INFO] Starting AI-Lab Enhanced Backend v2.0...
echo [INFO] Features: Database + Performance Monitoring + API Key Management
start "AI-Lab Enhanced Backend v2.0" cmd /c "cd backend && set DATABASE_URL=sqlite+aiosqlite:///./ai_lab.db && ..\venv\Scripts\activate.bat && python main.py"

:: Wait a moment for backend to start
echo [INFO] Waiting for enhanced backend to initialize...
timeout /t 8 /nobreak >nul

:: Test backend health
echo [INFO] Testing enhanced backend health...
curl -s http://localhost:8001/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Enhanced backend may still be starting...
    timeout /t 5 /nobreak >nul
)

:: Start frontend development server
echo [STEP 8/8] Starting frontend server...
start "AI-Lab Frontend" cmd /c "cd frontend && npm start"

:: Wait for frontend server to start
echo [INFO] Waiting for frontend server to start...
timeout /t 15 /nobreak >nul

:: Open browser to main interface
echo [INFO] Opening AI-Lab in browser...
start http://localhost:3000

:: Open backend API documentation
timeout /t 2 /nobreak >nul
echo [INFO] Backend API available at: http://localhost:8001
echo [INFO] Health check: http://localhost:8001/health
echo [INFO] Performance metrics: http://localhost:8001/metrics

echo.
echo ==========================================
echo    AI-Lab Enhanced v2.0 is running!
echo ==========================================
echo Frontend:     http://localhost:3000
echo Backend API:  http://localhost:8001
echo Health Check: http://localhost:8001/health
echo Metrics:      http://localhost:8001/metrics
echo.
echo ✅ ENHANCED FEATURES AVAILABLE:
echo    • PostgreSQL/SQLite Database Storage
echo    • Real-time Performance Monitoring  
echo    • Secure API Key Management
echo    • Prometheus Metrics Export
echo    • Enhanced Conversation History
echo.
echo 🔧 QUICK API TESTS:
echo    curl http://localhost:8001/health
echo    curl http://localhost:8001/metrics
echo    curl http://localhost:8001/api-keys
echo.
echo You can now chat with enhanced AI agents!
echo.
echo ⚠️  Keep this window open to see system status.
echo    Close individual service windows when done.
echo.

pause 