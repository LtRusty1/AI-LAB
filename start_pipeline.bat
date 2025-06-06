@echo off

:: Use the correct Ollama path from README
set OLLAMA_EXE=C:\Users\User\AppData\Local\Programs\Ollama\ollama.exe

echo Starting AI-Lab Pipeline...

:: Kill any existing Ollama processes
taskkill /F /IM ollama.exe 2>nul
timeout /t 2 /nobreak

:: Start Ollama server
echo Starting Ollama server...
start /B "" "%OLLAMA_EXE%" serve
timeout /t 5 /nobreak

:: Pull the Mistral model if not already present
echo Pulling Mistral model...
"%OLLAMA_EXE%" pull mistral

:: Activate the virtual environment and install dependencies
echo Setting up Python environment...
call win-venv\Scripts\activate.bat
pip install -r requirements.txt

:: Start the Streamlit web interface
echo Starting web interface...
start http://localhost:8501
streamlit run app.py

:: Keep the window open if there's an error
pause 