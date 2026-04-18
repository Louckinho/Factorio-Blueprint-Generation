# Factorio Blueprint Gen - Integrated Dev Launcher

$BackendPort = 8000
$FrontendPort = 5173

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Factorio Blueprint Gen - Integrated Dev" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# --- 1. Cleanup ---
Write-Host "[1/4] Port Cleanup..." -ForegroundColor Yellow

function Stop-ProcessOnPort($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        $processId = $conn.OwningProcess[0]
        $processName = (Get-Process -Id $processId).ProcessName
        Write-Host "Cleaning up port $port (Process: $processName, PID: $processId)..." -ForegroundColor Gray
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

Stop-ProcessOnPort $BackendPort
Stop-ProcessOnPort $FrontendPort

# --- 2. Backend Setup ---
Write-Host "[2/4] Setting up Backend..." -ForegroundColor Yellow

if (-not (Test-Path "backend\venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Gray
    python -m venv backend\venv
}

# Use & to run script and wait
Write-Host "Installing/Updating Backend Requirements..." -ForegroundColor Gray
& backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt

# --- 3. Frontend Setup ---
Write-Host "[3/4] Setting up Frontend..." -ForegroundColor Yellow

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "node_modules not found. Running npm install..." -ForegroundColor Gray
    Set-Location frontend
    npm install
    Set-Location ..
}

# --- 4. Launch ---
Write-Host "[4/4] Launching Services..." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:$BackendPort" -ForegroundColor DarkGray
Write-Host "Frontend: http://localhost:$FrontendPort" -ForegroundColor DarkGray
Write-Host "Press Ctrl+C to stop." -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Gray

# Launch Backend in background process (NoNewWindow keeps logs in this terminal)
$BackendProcess = Start-Process -FilePath "backend\venv\Scripts\python.exe" -ArgumentList "manage.py runserver" -WorkingDirectory "backend" -NoNewWindow -PassThru

# Run Frontend in foreground
Set-Location frontend
npm run dev

# Cleanup process on exit
Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue

