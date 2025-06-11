# AI-Lab Enhanced Desktop Shortcut Creator v2.0
# Creates a desktop shortcut to launch AI-Lab Enhanced with all new features

param(
    [string]$ProjectPath = $PWD.Path
)

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  AI-Lab Enhanced Shortcut Creator v2.0" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Get desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "AI-Lab Enhanced v2.0.lnk"

Write-Host "🔧 Creating enhanced desktop shortcut..." -ForegroundColor Yellow
Write-Host "   Project Path: $ProjectPath" -ForegroundColor Gray
Write-Host "   Shortcut Path: $ShortcutPath" -ForegroundColor Gray

try {
    # Create WScript Shell object
    $WScriptShell = New-Object -ComObject WScript.Shell
    
    # Create shortcut
    $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
    
    # Set shortcut properties for enhanced launcher
    $Shortcut.TargetPath = Join-Path $ProjectPath "start_ai_lab_complete.bat"
    $Shortcut.WorkingDirectory = $ProjectPath
    $Shortcut.Description = "AI-Lab Enhanced v2.0 - Database + Performance + API Keys"
    $Shortcut.IconLocation = "shell32.dll,21"  # Computer icon
    
    # Save shortcut
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "✅ SUCCESS: Enhanced desktop shortcut created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 ENHANCED FEATURES AVAILABLE:" -ForegroundColor Cyan
    Write-Host "   • Database Storage (PostgreSQL/SQLite)" -ForegroundColor White
    Write-Host "   • Real-time Performance Monitoring" -ForegroundColor White
    Write-Host "   • Secure API Key Management" -ForegroundColor White
    Write-Host "   • Prometheus Metrics Export" -ForegroundColor White
    Write-Host "   • Enhanced Conversation History" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 QUICK START:" -ForegroundColor Yellow
    Write-Host "   1. Double-click 'AI-Lab Enhanced v2.0' on your desktop" -ForegroundColor White
    Write-Host "   2. Enhanced launcher will:" -ForegroundColor White
    Write-Host "      - Check enhanced dependencies" -ForegroundColor Gray
    Write-Host "      - Setup database automatically" -ForegroundColor Gray
    Write-Host "      - Migrate existing data" -ForegroundColor Gray
    Write-Host "      - Start all services" -ForegroundColor Gray
    Write-Host "      - Open browser with enhanced features" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 NEW API ENDPOINTS:" -ForegroundColor Yellow
    Write-Host "   • http://localhost:8001/health - System health + metrics" -ForegroundColor White
    Write-Host "   • http://localhost:8001/metrics - Performance monitoring" -ForegroundColor White
    Write-Host "   • http://localhost:8001/api-keys - API key management" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 DOCUMENTATION:" -ForegroundColor Yellow
    Write-Host "   • AI_LAB_ENHANCED_FEATURES.md - Complete feature guide" -ForegroundColor White
    Write-Host "   • backend/ROADMAP_IMPLEMENTATION.md - Technical details" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Your AI development environment is now enterprise-ready!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to create shortcut" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 MANUAL ALTERNATIVE:" -ForegroundColor Yellow
    Write-Host "   Right-click on start_ai_lab_complete.bat" -ForegroundColor White
    Write-Host "   Select 'Send to' > 'Desktop (create shortcut)'" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")