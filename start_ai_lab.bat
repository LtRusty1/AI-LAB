@echo off
echo Starting AI-Lab Project...

:: Start backend in a new window (activate venv first)
start "AI-Lab Backend" cmd /k "cd backend && ..\win-venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak

:: Start frontend in a new window
start "AI-Lab Frontend" cmd /k "cd frontend && npm start"

:: Open the browser
timeout /t 5 /nobreak
start http://localhost:3000

echo AI-Lab Project is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul 