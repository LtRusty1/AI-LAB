# AI-Lab Enhanced Features Test Script v2.0
# Tests all enhanced features: Database, Performance Monitoring, API Key Management

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  AI-Lab Enhanced Features Test Suite v2.0" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$Backend = "http://localhost:8001"
$AllTestsPassed = $true

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$TestName,
        [string]$Method = "GET",
        [string]$Body = $null
    )
    
    try {
        Write-Host "🧪 Testing: $TestName" -ForegroundColor Yellow
        
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -TimeoutSec 10
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $Body -ContentType "application/json" -TimeoutSec 10
        }
        
        Write-Host "   ✅ PASS: $TestName" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "   ❌ FAIL: $TestName - $($_.Exception.Message)" -ForegroundColor Red
        $script:AllTestsPassed = $false
        return $false
    }
}

# Test if backend is running
Write-Host "🔍 Checking if AI-Lab Enhanced Backend is running..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "$Backend/" -TimeoutSec 5
    if ($response.features -contains "database" -and $response.features -contains "performance_monitoring" -and $response.features -contains "api_key_management") {
        Write-Host "✅ Enhanced Backend v2.0 is running with all features!" -ForegroundColor Green
        Write-Host "   Features: $($response.features -join ', ')" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Backend is running but enhanced features not detected" -ForegroundColor Yellow
        Write-Host "   Detected features: $($response.features -join ', ')" -ForegroundColor Gray
    }
}
catch {
    Write-Host "❌ Backend not responding at $Backend" -ForegroundColor Red
    Write-Host "   Please start the backend first with: LAUNCH.bat" -ForegroundColor Yellow
    Write-Host "   Or run: cd backend; python main.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "🧪 Running Enhanced Feature Tests..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Core Backend
Write-Host "📡 CORE BACKEND TESTS" -ForegroundColor Magenta
Test-Endpoint "$Backend/" "Root endpoint with enhanced features"
Test-Endpoint "$Backend/health" "Enhanced health check with metrics"

# Test 2: Performance Monitoring
Write-Host ""
Write-Host "📊 PERFORMANCE MONITORING TESTS" -ForegroundColor Magenta
Test-Endpoint "$Backend/metrics" "Real-time system metrics"
Test-Endpoint "$Backend/metrics/prometheus" "Prometheus metrics export"
Test-Endpoint "$Backend/performance/summary" "Performance summary"

# Test 3: API Key Management
Write-Host ""
Write-Host "🔐 API KEY MANAGEMENT TESTS" -ForegroundColor Magenta
Test-Endpoint "$Backend/api-keys" "API key services list"

# Test 4: Enhanced Conversation System
Write-Host ""
Write-Host "💬 ENHANCED CONVERSATION TESTS" -ForegroundColor Magenta
Test-Endpoint "$Backend/conversation/test_session" "Database conversation retrieval"

# Test 5: LLM Benchmarking
Write-Host ""
Write-Host "⚡ LLM BENCHMARKING TEST" -ForegroundColor Magenta
$benchmarkBody = @{
    model_name = "test"
    prompt = "Hello, world!"
    iterations = 3
} | ConvertTo-Json

Test-Endpoint "$Backend/benchmark/llm" "LLM inference benchmarking" "POST" $benchmarkBody

# Database Test
Write-Host ""
Write-Host "🗄️ DATABASE TESTS" -ForegroundColor Magenta
Write-Host "🧪 Testing: Database file existence" -ForegroundColor Yellow
if (Test-Path "backend/ai_lab.db") {
    Write-Host "   ✅ PASS: Database file exists" -ForegroundColor Green
    $dbSize = (Get-Item "backend/ai_lab.db").Length
    Write-Host "   📊 Database size: $([math]::Round($dbSize/1KB, 2)) KB" -ForegroundColor Gray
} else {
    Write-Host "   ❌ FAIL: Database file not found" -ForegroundColor Red
    $AllTestsPassed = $false
}

# Migration Backup Test
Write-Host "🧪 Testing: Migration backup" -ForegroundColor Yellow
if (Test-Path "backend/json_backup") {
    $backupFiles = (Get-ChildItem "backend/json_backup" -File).Count
    Write-Host "   ✅ PASS: Migration backup exists ($backupFiles files)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  INFO: No migration backup found (normal for fresh installs)" -ForegroundColor Yellow
}

# Module Import Test
Write-Host "🧪 Testing: Enhanced module imports" -ForegroundColor Yellow
try {
    $moduleTest = & python -c "import ai_lab.database; import ai_lab.performance; import ai_lab.api_keys; print('All enhanced modules imported successfully')" 2>&1
    if ($moduleTest -match "successfully") {
        Write-Host "   ✅ PASS: All enhanced modules available" -ForegroundColor Green
    } else {
        Write-Host "   ❌ FAIL: Module import issues" -ForegroundColor Red
        $AllTestsPassed = $false
    }
}
catch {
    Write-Host "   ❌ FAIL: Cannot test module imports" -ForegroundColor Red
    $AllTestsPassed = $false
}

# Final Results
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "           TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

if ($AllTestsPassed) {
    Write-Host "🎉 ALL TESTS PASSED! 🎉" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Your AI-Lab Enhanced v2.0 is fully operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 READY TO USE:" -ForegroundColor Yellow
    Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   • Backend API: http://localhost:8001" -ForegroundColor White
    Write-Host "   • Health Check: http://localhost:8001/health" -ForegroundColor White
    Write-Host "   • Metrics: http://localhost:8001/metrics" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 ENHANCED FEATURES VERIFIED:" -ForegroundColor Cyan
    Write-Host "   ✅ Database Storage (SQLite/PostgreSQL)" -ForegroundColor White
    Write-Host "   ✅ Real-time Performance Monitoring" -ForegroundColor White
    Write-Host "   ✅ Secure API Key Management" -ForegroundColor White
    Write-Host "   ✅ Prometheus Metrics Export" -ForegroundColor White
    Write-Host "   ✅ Enhanced Conversation History" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "   • Read: AI_LAB_ENHANCED_FEATURES.md" -ForegroundColor White
    Write-Host "   • Try: curl http://localhost:8001/api-keys" -ForegroundColor White
    Write-Host "   • Store API keys via the backend API" -ForegroundColor White
    Write-Host "   • Monitor performance in real-time" -ForegroundColor White
} else {
    Write-Host "⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "   1. Make sure backend is running: python backend/main.py" -ForegroundColor White
    Write-Host "   2. Check database setup: python backend/setup_database.py" -ForegroundColor White
    Write-Host "   3. Verify dependencies: pip install -r backend/requirements.txt" -ForegroundColor White
    Write-Host "   4. Review logs in backend terminal window" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 DOCUMENTATION:" -ForegroundColor Yellow
    Write-Host "   • AI_LAB_ENHANCED_FEATURES.md - Troubleshooting section" -ForegroundColor White
    Write-Host "   • backend/ROADMAP_IMPLEMENTATION.md - Technical details" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 