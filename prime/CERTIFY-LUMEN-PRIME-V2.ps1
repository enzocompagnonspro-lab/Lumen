$ErrorActionPreference = "Stop"
Write-Host "[LUMEN PRIME V2] Validate"
python .\runtime\lumen_prime.py validate
Write-Host "[LUMEN PRIME V2] Init memory"
python .\runtime\lumen_prime.py init-db
Write-Host "[LUMEN PRIME V2] Sync embedded LUMEN OS snapshot"
$tmp = Join-Path $PWD "_cert_os"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Force -Path "$tmp\config","$tmp\registry","$tmp\state" | Out-Null
Copy-Item .\bootstrap\config__canon.json "$tmp\config\canon.json"
Copy-Item .\bootstrap\registry__knowledge.json "$tmp\registry\knowledge.json"
Copy-Item .\bootstrap\registry__journey.json "$tmp\registry\journey.json"
Copy-Item .\bootstrap\state__status.json "$tmp\state\status.json"
python .\runtime\lumen_prime.py sync-os --root $tmp
python .\runtime\lumen_prime.py stats
Write-Host "[LUMEN PRIME V2] Model policy"
python .\runtime\lumen_prime.py model --task deep_research
python .\runtime\lumen_prime.py model --task deep_research --frontier-available
Write-Host "[LUMEN PRIME V2] Tests"
python -m unittest discover -s .\tests -p "test_*.py" -v
Remove-Item $tmp -Recurse -Force
Write-Host "LUMEN PRIME V2 CERTIFICATION COMPLETE"
