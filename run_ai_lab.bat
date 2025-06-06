start cmd /k "cd /d C:\AI-lab && call win-venv\Scripts\activate.bat && uvicorn backend.main:app --reload --reload-dir backend"
start cmd /k "cd /d C:\AI-lab\frontend && npm start"
