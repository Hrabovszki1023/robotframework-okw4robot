# build.ps1 – Build distribution packages for robotframework-okw4robot
# Usage: .\scripts\build.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root

Write-Host "=== Build: robotframework-okw4robot ===" -ForegroundColor Cyan

# Clean old dist
if (Test-Path "dist") {
    Write-Host "Cleaning dist/..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "dist"
}

# Build
Write-Host "Building wheel and sdist..." -ForegroundColor Yellow
python -m build

Write-Host ""
Write-Host "Build artifacts:" -ForegroundColor Green
Get-ChildItem dist | ForEach-Object { Write-Host "  $_" }

Pop-Location
