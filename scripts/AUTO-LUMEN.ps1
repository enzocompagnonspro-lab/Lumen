$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python .\app\lumen_os.py auto
python .\app\lumen_os.py review-pack
