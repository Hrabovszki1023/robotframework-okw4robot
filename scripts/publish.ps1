# publish.ps1 – Publish robotframework-okw4robot to PyPI
# Requires: PYPI_API_TOKEN environment variable or ~/.pypirc
# Usage: .\scripts\publish.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root

Write-Host "=== Publish: robotframework-okw4robot ===" -ForegroundColor Cyan

if (-not (Test-Path "dist")) {
    Write-Error "No dist/ directory found. Run .\scripts\build.ps1 first."
    exit 1
}

$wheels = Get-ChildItem dist -Filter "*.whl"
if ($wheels.Count -eq 0) {
    Write-Error "No .whl files found in dist/. Run .\scripts\build.ps1 first."
    exit 1
}

Write-Host "Uploading to PyPI..." -ForegroundColor Yellow
python -m twine upload dist/*

Write-Host ""
Write-Host "Published successfully." -ForegroundColor Green

Pop-Location
