$ErrorActionPreference = "Stop"
Write-Host "[LUMEN PRIME] Sync current LUMEN OS"
python .\prime\runtime\lumen_prime.py init-db
python .\prime\runtime\lumen_prime.py sync-os --root .
python .\prime\runtime\lumen_prime.py stats
