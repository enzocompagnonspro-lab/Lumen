$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$port = 8765
Write-Host "[LUMEN] Golden Journey"
Write-Host "Open: http://127.0.0.1:$port/golden-journey/"
Start-Process "http://127.0.0.1:$port/golden-journey/"
& python "$root\app\real_server.py" --port $port
