# libdoc.ps1 – Generate Robot Framework Libdoc HTML for OKW4RobotLibrary
# Usage: .\scripts\libdoc.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root

Write-Host "=== Libdoc: OKW4RobotLibrary ===" -ForegroundColor Cyan

# Ensure the package is installed (editable)
Write-Host "Installing package (editable)..." -ForegroundColor Yellow
pip install -e . --quiet

# Generate HTML
$outFile = "docs/OKW4RobotLibrary.html"
Write-Host "Generating $outFile ..." -ForegroundColor Yellow
python -m robot.libdoc okw4robot.library.OKW4RobotLibrary $outFile

$size = (Get-Item $outFile).Length
Write-Host ""
Write-Host "Generated: $outFile ($size bytes)" -ForegroundColor Green
Write-Host ""
Write-Host "Keyword count:" -ForegroundColor Cyan
python -m robot.libdoc okw4robot.library.OKW4RobotLibrary list | Measure-Object -Line | Select-Object -ExpandProperty Lines

Pop-Location
