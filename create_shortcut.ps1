# PowerShell script to create a desktop shortcut for running the AI-Lab project (backend + frontend)
# This script is for local development, but the structure is cloud-ready.
# Backend: Python FastAPI (to be implemented)
# Frontend: React (Cytoscape.js)

$DesktopPath = [Environment]::GetFolderPath('Desktop')
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\AI-Lab Project.lnk")
$Shortcut.TargetPath = "C:\AI-lab\start_ai_lab.bat"
$Shortcut.WorkingDirectory = "C:\AI-lab"
$Shortcut.Description = "Start AI-Lab Project (Backend + Frontend)"
$Shortcut.IconLocation = "C:\Windows\System32\SHELL32.dll,21"
$Shortcut.Save()

Write-Host "Shortcut created on desktop: 'AI-Lab Project'"

# For cloud deployment:
# - Backend can be containerized (Docker) and deployed to any cloud (AWS, Azure, GCP, etc.)
# - Frontend can be built (npm run build) and served via CDN or cloud static hosting 