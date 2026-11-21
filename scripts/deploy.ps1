# ==============================================================================
# JobPilot Windows PowerShell Production Deployment Script
# ==============================================================================
[CmdletBinding()]
param (
    [switch]$ForceRebuild = $false
)

$ErrorActionPreference = "Stop"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting JobPilot Production Deployment (Windows)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $PSScriptRoot
$DockerDir = Join-Path $RootDir "docker"
$ComposeFile = Join-Path $DockerDir "docker-compose.prod.yml"

Set-Location $RootDir

# Verify .env
if (-not (Test-Path "$DockerDir\.env") -and -not (Test-Path "$RootDir\.env")) {
    Write-Warning "Production .env file not found. Copying .env.production.example to .env..."
    Copy-Item "$RootDir\.env.production.example" "$RootDir\.env"
}

Write-Host "🔨 1/4 Building production microservices..." -ForegroundColor Yellow
if ($ForceRebuild) {
    docker compose -f $ComposeFile build --no-cache
} else {
    docker compose -f $ComposeFile build
}

Write-Host "💾 2/4 Initializing persistence layer..." -ForegroundColor Yellow
docker compose -f $ComposeFile up -d postgres redis minio

Write-Host "⏳ 3/4 Running database migrations..." -ForegroundColor Yellow
docker compose -f $ComposeFile run --rm migration

Write-Host "🚀 4/4 Starting API cluster, workers, frontend and Nginx..." -ForegroundColor Green
docker compose -f $ComposeFile up -d --remove-orphans

Write-Host "🩺 Verifying health probes..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$healthy = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost/health" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($res.status -eq "healthy") {
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 3
    }
}

if ($healthy) {
    Write-Host "✅ Deployment Successful! API is operational at http://localhost" -ForegroundColor Green
} else {
    Write-Warning "⚠️ Could not confirm health probe within timeout. Check logs with: docker compose -f docker\docker-compose.prod.yml logs"
}
