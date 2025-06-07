# PowerShell script to create desktop shortcut for AI-Lab
Write-Host "Creating AI-Lab Desktop Shortcut..." -ForegroundColor Green

# Get the current script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchFilePath = Join-Path $scriptPath "start_ai_lab_complete.bat"

# Check if batch file exists
if (-not (Test-Path $batchFilePath)) {
    Write-Host "Error: start_ai_lab_complete.bat not found in $scriptPath" -ForegroundColor Red
    Write-Host "Please make sure the batch file exists in the same directory as this script." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Get desktop path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "AI-Lab Launcher.lnk"

# Create WScript Shell object
$wshShell = New-Object -ComObject WScript.Shell

# Create shortcut object
$shortcut = $wshShell.CreateShortcut($shortcutPath)

# Set shortcut properties
$shortcut.TargetPath = $batchFilePath
$shortcut.WorkingDirectory = $scriptPath
$shortcut.Description = "AI-Lab Complete Launcher - Starts backend, frontend, and opens browser"
$shortcut.WindowStyle = 1

# Set icon
$shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"

# Save the shortcut
$shortcut.Save()

# Verify shortcut was created
if (Test-Path $shortcutPath) {
    Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host "Shortcut location: $shortcutPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now double-click 'AI-Lab Launcher' on your desktop to start everything!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The shortcut will:" -ForegroundColor White
    Write-Host "  - Check and install Redis if needed" -ForegroundColor Gray
    Write-Host "  - Start Ollama (if available)" -ForegroundColor Gray  
    Write-Host "  - Start the backend server on port 8001" -ForegroundColor Gray
    Write-Host "  - Start the frontend server on port 3000" -ForegroundColor Gray
    Write-Host "  - Open your browser to http://localhost:3000" -ForegroundColor Gray
} else {
    Write-Host "Failed to create desktop shortcut" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"