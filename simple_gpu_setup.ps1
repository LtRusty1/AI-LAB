Write-Host "Configuring Ollama for GPU Acceleration..." -ForegroundColor Green

# Check for NVIDIA GPU
$nvidia = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
if ($nvidia) {
    Write-Host "NVIDIA GPU detected: $($nvidia.Name)" -ForegroundColor Green
} else {
    Write-Host "No NVIDIA GPU detected. Checking all GPUs..." -ForegroundColor Yellow
    $allGpus = Get-WmiObject Win32_VideoController
    foreach ($gpu in $allGpus) {
        Write-Host "Found: $($gpu.Name)" -ForegroundColor Cyan
    }
}

# Find and restart Ollama with GPU settings
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($ollamaProcess) {
    $ollamaPath = $ollamaProcess.Path
    $ollamaDir = Split-Path $ollamaPath
    Write-Host "Ollama found at: $ollamaPath" -ForegroundColor Green
    
    # Stop current processes
    Write-Host "Stopping Ollama processes..." -ForegroundColor Yellow
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    
    # Create batch file with GPU environment variables
    $batchContent = @"
@echo off
set OLLAMA_GPU_LAYERS=999
set CUDA_VISIBLE_DEVICES=0
set OLLAMA_HOST=127.0.0.1:11434
cd /d "$ollamaDir"
"$ollamaPath" serve
"@
    
    $batchFile = "start_ollama_gpu.bat"
    $batchContent | Out-File -FilePath $batchFile -Encoding ASCII -Force
    
    # Start Ollama with GPU
    Write-Host "Starting Ollama with GPU acceleration..." -ForegroundColor Green
    Start-Process -FilePath $batchFile -WindowStyle Hidden
    
    Write-Host "Ollama restarted with GPU configuration!" -ForegroundColor Green
    Write-Host "Batch file created: $batchFile" -ForegroundColor Cyan
    
} else {
    Write-Host "Ollama process not found!" -ForegroundColor Red
}

Write-Host "Configuration complete!" -ForegroundColor Green 