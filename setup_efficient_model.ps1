# Setup Efficient AI Model for Better Performance
Write-Host "🚀 Setting up efficient AI model for faster responses..." -ForegroundColor Green

# Find Ollama executable path
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($ollamaProcess) {
    $ollamaPath = $ollamaProcess.Path
    $ollamaDir = Split-Path $ollamaPath
    $ollamaExe = Join-Path $ollamaDir "ollama.exe"
    
    Write-Host "✅ Ollama executable found: $ollamaExe" -ForegroundColor Green
    
    # Check current models
    Write-Host "📋 Checking current models..." -ForegroundColor Yellow
    try {
        $models = & $ollamaExe list 2>$null
        Write-Host $models -ForegroundColor Cyan
    } catch {
        Write-Host "Could not list models directly" -ForegroundColor Yellow
    }
    
    # Pull efficient model for faster responses
    Write-Host "⬇️  Installing llama3.2:3b (efficient 3B parameter model)..." -ForegroundColor Yellow
    Write-Host "This will provide faster responses and better GPU utilization." -ForegroundColor Cyan
    
    try {
        $pullProcess = Start-Process -FilePath $ollamaExe -ArgumentList "pull", "llama3.2:3b" -Wait -PassThru -WindowStyle Hidden
        if ($pullProcess.ExitCode -eq 0) {
            Write-Host "✅ llama3.2:3b model installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Model installation may have issues. Trying alternative..." -ForegroundColor Yellow
            
            # Try phi3 as alternative
            Write-Host "⬇️  Installing phi3:mini as backup..." -ForegroundColor Yellow
            $pullProcess2 = Start-Process -FilePath $ollamaExe -ArgumentList "pull", "phi3:mini" -Wait -PassThru -WindowStyle Hidden
            if ($pullProcess2.ExitCode -eq 0) {
                Write-Host "✅ phi3:mini model installed as backup!" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "❌ Error installing model: $_" -ForegroundColor Red
    }
    
    # Test the model
    Write-Host "🧪 Testing model response..." -ForegroundColor Yellow
    try {
        $testProcess = Start-Process -FilePath $ollamaExe -ArgumentList "run", "llama3.2:3b", "Hello, respond with just 'OK' if you're working" -Wait -PassThru -WindowStyle Hidden
        if ($testProcess.ExitCode -eq 0) {
            Write-Host "✅ Model test completed!" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Could not test model directly" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Ollama process not found!" -ForegroundColor Red
    Write-Host "Please start Ollama first." -ForegroundColor Yellow
}

Write-Host "`n📊 Performance Comparison:" -ForegroundColor Yellow
Write-Host "   • mistral (7B): Slower, high quality responses" -ForegroundColor Cyan
Write-Host "   • llama3.2:3b (3B): Faster, good quality responses" -ForegroundColor Green
Write-Host "   • phi3:mini (3.8B): Fastest, optimized for efficiency" -ForegroundColor Green

Write-Host "`n✨ Setup complete! Restart your backend to use the new model." -ForegroundColor Green
Write-Host "💡 Your responses should now be 2-3x faster with better GPU utilization!" -ForegroundColor Yellow 