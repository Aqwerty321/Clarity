# Clarity Local Demo Startup Script (Windows PowerShell)

Write-Host "🔍 Starting Clarity Local Demo..." -ForegroundColor Cyan

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed" -ForegroundColor Red
    exit 1
}

# Check if Node is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js is not installed" -ForegroundColor Red
    exit 1
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Set-Location $ProjectRoot

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  No .env file found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ Please edit .env with your Auth0 credentials before continuing." -ForegroundColor Green
    exit 1
}

# Start local backend
Write-Host "📦 Starting Local Backend..." -ForegroundColor Blue
Set-Location local_backend

if (-not (Test-Path venv)) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

# Start backend in background
Write-Host "Starting FastAPI server on port 5000..."
$BackendJob = Start-Job -ScriptBlock {
    param($Path)
    Set-Location $Path
    .\venv\Scripts\Activate.ps1
    uvicorn app.main:app --host 0.0.0.0 --port 5000
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 3

Set-Location $ProjectRoot

# Start frontend
Write-Host "🎨 Starting Frontend..." -ForegroundColor Blue
Set-Location frontend

if (-not (Test-Path node_modules)) {
    Write-Host "Installing npm dependencies..."
    npm install
}

Write-Host "Starting Vite dev server on port 5173..."
$FrontendJob = Start-Job -ScriptBlock {
    param($Path)
    Set-Location $Path
    npm run dev
} -ArgumentList (Get-Location).Path

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Clarity is running!" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Wait and monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        if ($BackendJob.State -eq "Failed") {
            Write-Host "Backend job failed!" -ForegroundColor Red
            break
        }
        
        if ($FrontendJob.State -eq "Failed") {
            Write-Host "Frontend job failed!" -ForegroundColor Red
            break
        }
    }
}
finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job $BackendJob, $FrontendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob, $FrontendJob -ErrorAction SilentlyContinue
}
