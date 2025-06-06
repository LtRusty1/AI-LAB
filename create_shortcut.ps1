# PowerShell script to create a desktop shortcut for AI-Lab Project One-Click Launcher
# This creates a shortcut that automatically starts Ollama, installs dependencies, and launches the Streamlit interface

Write-Host "Creating AI-Lab Project Desktop Shortcut..." -ForegroundColor Green

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$ProjectPath = "C:\AI-lab"
$ShortcutPath = "$DesktopPath\AI-Lab Project.lnk"

# Check if the project directory exists
if (-not (Test-Path $ProjectPath)) {
    Write-Host "ERROR: Project directory not found at $ProjectPath" -ForegroundColor Red
    Write-Host "Please update the ProjectPath variable in this script to match your installation." -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway..."
}

# Create the shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Set shortcut properties
$Shortcut.TargetPath = "$ProjectPath\start_ai_lab_one_click.bat"
$Shortcut.WorkingDirectory = $ProjectPath
$Shortcut.Description = "AI-Lab Project - One-Click Launcher (Starts Ollama + Streamlit Interface)"
$Shortcut.Arguments = ""

# Set an attractive icon (robot/AI-like icon from Windows)
$Shortcut.IconLocation = "C:\Windows\System32\SHELL32.dll,238"

# Save the shortcut
$Shortcut.Save()

# Verify the shortcut was created
if (Test-Path $ShortcutPath) {
    Write-Host "SUCCESS: Desktop shortcut created!" -ForegroundColor Green
    Write-Host "Location: $ShortcutPath" -ForegroundColor Cyan
    Write-Host "Target: $ProjectPath\start_ai_lab_one_click.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "How to use:" -ForegroundColor Yellow
    Write-Host "  1. Double-click the 'AI-Lab Project' shortcut on your desktop"
    Write-Host "  2. Wait for all services to start (Ollama + Streamlit)"
    Write-Host "  3. Your browser will automatically open to http://localhost:8501"
    Write-Host "  4. Start chatting with your AI agents!"
    Write-Host ""
    Write-Host "What the shortcut does:" -ForegroundColor Magenta
    Write-Host "  - Automatically finds and starts Ollama server"
    Write-Host "  - Downloads Mistral model if needed"
    Write-Host "  - Activates Python virtual environment"
    Write-Host "  - Installs/updates required packages"
    Write-Host "  - Launches Streamlit web interface"
    Write-Host "  - Opens your browser to the application"
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor Yellow
    Write-Host "  - Ollama must be installed (https://ollama.ai)"
    Write-Host "  - Python virtual environment (win-venv) must exist"
    Write-Host "  - Internet connection for first-time model download"
} else {
    Write-Host "ERROR: Failed to create shortcut" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 