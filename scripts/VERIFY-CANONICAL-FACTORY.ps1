$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$expected = "e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1"
$canon = Join-Path $root "assets\canon\01_SANCTUAIRE.png"
if (-not (Test-Path $canon)) { throw "CANON_GUARD_FAIL: canonical asset missing" }
$actual = (Get-FileHash -Algorithm SHA256 $canon).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "CANON_GUARD_FAIL expected=$expected actual=$actual" }
Write-Host "CANON_GUARD_PASS $actual"

$stdout = Join-Path $env:TEMP "lumen-tests.stdout.txt"
$stderr = Join-Path $env:TEMP "lumen-tests.stderr.txt"
$p = Start-Process -FilePath "python" `
  -ArgumentList @("-m","unittest","discover","-s","tests","-v") `
  -WorkingDirectory $root `
  -NoNewWindow -Wait -PassThru `
  -RedirectStandardOutput $stdout `
  -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue
Get-Content $stderr -ErrorAction SilentlyContinue
if ($p.ExitCode -ne 0) { throw "UNIT_TESTS_FAIL exit=$($p.ExitCode)" }
Write-Host "UNIT_TESTS_PASS"
Write-Host "LUMEN_CANONICAL_FACTORY_VERIFY_PASS"
