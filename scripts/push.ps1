# push.ps1 – Push to both remotes: Gitea (origin) and GitHub
# Usage: .\scripts\push.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root

Write-Host "=== Push to both remotes ===" -ForegroundColor Cyan

Write-Host "Pushing to origin (Gitea)..." -ForegroundColor Yellow
git push origin main

Write-Host "Pushing to github (GitHub)..." -ForegroundColor Yellow
git push github main

Write-Host ""
Write-Host "Pushed to both remotes." -ForegroundColor Green

Pop-Location
