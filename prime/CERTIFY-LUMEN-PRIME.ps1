$ErrorActionPreference = 'Stop'
Write-Host '[LUMEN PRIME] Validate'
python .\runtime\lumen_prime.py validate
Write-Host '[LUMEN PRIME] Tests'
python -m unittest discover -s .\tests -p 'test_*.py' -v
Write-Host 'LUMEN PRIME CERTIFICATION COMPLETE'
