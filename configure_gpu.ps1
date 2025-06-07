# Configure Ollama for GPU Acceleration
Write-Host "🚀 Configuring Ollama for GPU Acceleration..." -ForegroundColor Green

# Check if NVIDIA GPU is available
$nvidia = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" }
if ($nvidia) {
    Write-Host "✅ NVIDIA GPU detected: $($nvidia.Name)" -ForegroundColor Green
    
    # Set CUDA environment variables for Ollama
    $env:OLLAMA_GPU_LAYERS = "999"  # Use all available GPU layers
    $env:OLLAMA_CUDA_VERSION = "12"  # Use CUDA 12
    $env:OLLAMA_GPU_MEMORY = "8GB"  # Adjust based on your GPU memory
    
    Write-Host "🔧 Set GPU environment variables:" -ForegroundColor Yellow
    Write-Host "   OLLAMA_GPU_LAYERS = $env:OLLAMA_GPU_LAYERS"
    Write-Host "   OLLAMA_CUDA_VERSION = $env:OLLAMA_CUDA_VERSION"
    Write-Host "   OLLAMA_GPU_MEMORY = $env:OLLAMA_GPU_MEMORY"
} else {
    Write-Host "⚠️  No NVIDIA GPU detected. Checking for other GPUs..." -ForegroundColor Yellow
    $allGpus = Get-WmiObject Win32_VideoController
    foreach ($gpu in $allGpus) {
        Write-Host "   Found: $($gpu.Name)" -ForegroundColor Cyan
    }
}

# Find Ollama executable
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($ollamaProcess) {
    $ollamaPath = $ollamaProcess.Path
    $ollamaDir = Split-Path $ollamaPath
    Write-Host "✅ Ollama found at: $ollamaPath" -ForegroundColor Green
    
    # Stop Ollama
    Write-Host "🛑 Stopping current Ollama processes..." -ForegroundColor Yellow
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    
    # Restart Ollama with GPU configuration
    Write-Host "🚀 Restarting Ollama with GPU acceleration..." -ForegroundColor Green
    
    # Create a batch file to start Ollama with GPU settings
    $batchContent = @"
@echo off
set OLLAMA_GPU_LAYERS=999
set OLLAMA_CUDA_VERSION=12
set OLLAMA_GPU_MEMORY=8GB
set OLLAMA_HOST=127.0.0.1:11434
cd /d "$ollamaDir"
start "" "$ollamaPath" serve
"@
    
    $batchFile = "start_ollama_gpu.bat"
    $batchContent | Out-File -FilePath $batchFile -Encoding ASCII
    
    # Start Ollama with GPU settings
    Start-Process -FilePath $batchFile -WindowStyle Hidden
    
    Write-Host "✅ Ollama restarted with GPU acceleration!" -ForegroundColor Green
    Write-Host "📋 Batch file created: $batchFile" -ForegroundColor Cyan
    
} else {
    Write-Host "❌ Ollama process not found!" -ForegroundColor Red
}

# Check GPU utilization
Write-Host "`n🔍 Checking GPU utilization..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>$null
    if ($gpuInfo) {
        Write-Host "GPU Status:" -ForegroundColor Green
        $gpuInfo | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
    }
} catch {
    Write-Host "⚠️  nvidia-smi not available. Install NVIDIA drivers and CUDA toolkit." -ForegroundColor Yellow
}

Write-Host "`n✨ Configuration complete! Test your AI responses now." -ForegroundColor Green
Write-Host "💡 If responses are still slow, try using a smaller model like llama3.2:3b" -ForegroundColor Yellow 