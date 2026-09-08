$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "[LUMEN] Browser QA 01R2 - fidelity-first" -ForegroundColor Cyan
& .\scripts\BROWSER-QA.ps1
Write-Host "[LUMEN] Control plane" -ForegroundColor Cyan
& .\scripts\AUTO-LUMEN.ps1
Write-Host "[LUMEN] Status" -ForegroundColor Cyan
& .\scripts\STATUS-LUMEN.ps1
if (Test-Path .\LUMEN-REVIEW-PACK-T007R2.zip) {
  Write-Host ""; Write-Host "REVIEW PACK READY:" -ForegroundColor Green
  Write-Host (Resolve-Path .\LUMEN-REVIEW-PACK-T007R2.zip).Path
}
