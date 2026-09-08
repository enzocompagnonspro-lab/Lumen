$ErrorActionPreference = "Stop"
Write-Host "[LUMEN PRIME V2] Validate model layer"
python .\prime\runtime\lumen_prime.py validate
Write-Host "[LUMEN PRIME V2] Sync current OS"
python .\prime\runtime\lumen_prime.py init-db
python .\prime\runtime\lumen_prime.py sync-os --root .
Write-Host "[LUMEN PRIME V2] Stats"
python .\prime\runtime\lumen_prime.py stats
Write-Host "[LUMEN PRIME V2] Context smoke"
python .\prime\runtime\lumen_prime.py context "analyse la progression de Vision et propose la prochaine action"
Write-Host "[LUMEN PRIME V2] Unit tests"
python -m unittest discover -s .\prime\tests -p "test_*.py" -v
Write-Host "LUMEN PRIME V2 INTEGRATION CERTIFICATION COMPLETE"
