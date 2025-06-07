@echo off
set OLLAMA_GPU_LAYERS=999
set CUDA_VISIBLE_DEVICES=0
set OLLAMA_HOST=127.0.0.1:11434
cd /d "C:\Users\User\AppData\Local\Programs\Ollama"
"C:\Users\User\AppData\Local\Programs\Ollama\ollama.exe" serve
