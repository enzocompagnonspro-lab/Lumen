$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Write-Host "[LUMEN] Living System 01 certification" -ForegroundColor Cyan
& (Join-Path $PSScriptRoot "BROWSER-QA-LIVING.ps1")
Write-Host "[LUMEN] Control plane" -ForegroundColor Cyan
python (Join-Path $Root "app\lumen_os.py") auto
Write-Host "[LUMEN] Status" -ForegroundColor Cyan
python (Join-Path $Root "app\lumen_os.py") status
$pack = python (Join-Path $Root "app\lumen_os.py") living-review-pack | ConvertFrom-Json
if($pack.ok){Write-Host "";Write-Host "REVIEW PACK READY:" -ForegroundColor Green;Write-Host $pack.path -ForegroundColor Green}else{Write-Host "REVIEW PACK NOT READY" -ForegroundColor Yellow;Write-Host ($pack|ConvertTo-Json -Depth 4)}
