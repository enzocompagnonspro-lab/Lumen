$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$evidence = Join-Path $root "evidence\real-01\windows"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
Write-Host "[LUMEN] REAL-01 technical validation"
& python "$root\app\validate_real01.py" | Tee-Object -FilePath (Join-Path $evidence "technical-validation.json")
if ($LASTEXITCODE -ne 0) { throw "REAL01_TECHNICAL_FAIL" }
# Windows PowerShell 5.1 turns native STDERR into ErrorRecord objects.
# Python unittest writes normal verbose progress to STDERR, so piping 2>&1 under
# $ErrorActionPreference = "Stop" can abort a successful test run.
# Run it as a child process with explicit stdout/stderr files, then evaluate ONLY
# the real process exit code. This preserves a strict gate without false failure.
$testStdout = Join-Path $evidence "unit-tests.stdout.txt"
$testStderr = Join-Path $evidence "unit-tests.stderr.txt"
$testCombined = Join-Path $evidence "unit-tests.txt"
Remove-Item $testStdout,$testStderr,$testCombined -Force -ErrorAction SilentlyContinue
$testProc = Start-Process -FilePath python -ArgumentList @(
  "-m","unittest","discover",
  "-s",(Join-Path $root "tests"),
  "-p","test_real01.py",
  "-v"
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $testStdout -RedirectStandardError $testStderr
@($testStdout,$testStderr) | ForEach-Object {
  if (Test-Path $_) { Get-Content $_ }
} | Tee-Object -FilePath $testCombined
if ($testProc.ExitCode -ne 0) { throw "REAL01_TEST_FAIL: exit=$($testProc.ExitCode)" }
Write-Host "REAL-01 UNIT TESTS PASS"
$expectedCanon = "e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1"
$canonPath = Join-Path $root "projects\golden-journey\assets\sanctuaire.png"
$canonHash = (Get-FileHash -Algorithm SHA256 $canonPath).Hash.ToLowerInvariant()
if ($canonHash -ne $expectedCanon) { throw "REAL01_CANON_HASH_FAIL: $canonHash" }
Write-Host "[LUMEN] Golden Sanctuary hash PASS"
$chromeCandidates = @("C:\Program Files\Google\Chrome\Application\chrome.exe","C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { throw "REAL01_CHROME_NOT_FOUND" }
$port = 8765
$serverLog = Join-Path $evidence "server.log"
$serverErr = Join-Path $evidence "server-error.log"
$server = Start-Process python -ArgumentList @("$root\app\real_server.py","--port",$port) -PassThru -WindowStyle Hidden -RedirectStandardOutput $serverLog -RedirectStandardError $serverErr
try {
 $health = "http://127.0.0.1:$port/api/real/health"
 $ready = $false
 for ($i=0; $i -lt 30; $i++) {
   try { $r = Invoke-WebRequest -UseBasicParsing -Uri $health -TimeoutSec 2; if ($r.StatusCode -eq 200) { $ready=$true; break } } catch {}
   Start-Sleep -Milliseconds 300
 }
 if (-not $ready) { throw "REAL01_SERVER_NOT_READY" }
 $base = "http://127.0.0.1:$port/golden-journey/"
 $profile = Join-Path $env:TEMP ("lumen-real01-" + [guid]::NewGuid().ToString("N"))
 New-Item -ItemType Directory -Force -Path $profile | Out-Null
 $seedDom = Join-Path $evidence "e2e-seed-dom.html"
 $verifyDom = Join-Path $evidence "e2e-verify-dom.html"
 $seedErr = Join-Path $evidence "e2e-seed-chrome.stderr.txt"
 $verifyErr = Join-Path $evidence "e2e-verify-chrome.stderr.txt"

 function Invoke-LumenChromeDump([string]$Url,[string]$Out,[string]$Err,[int]$Budget) {
   Remove-Item $Out,$Err -Force -ErrorAction SilentlyContinue
   $args = @(
     "--headless=new",
     "--disable-gpu",
     "--no-first-run",
     "--no-default-browser-check",
     "--user-data-dir=$profile",
     "--virtual-time-budget=$Budget",
     "--dump-dom",
     $Url
   )
   $proc = Start-Process -FilePath $chrome -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput $Out -RedirectStandardError $Err
   if ($proc.ExitCode -ne 0) { throw "REAL01_CHROME_DUMP_FAIL: exit=$($proc.ExitCode) url=$Url" }
   if (-not (Test-Path $Out)) { throw "REAL01_CHROME_DUMP_MISSING: $Out" }
   return (Get-Content -Raw -Path $Out)
 }

 try {
   # Phase 1: execute the complete journey. The current page may dynamically
   # navigate to ?qa=e2e-verify; dump-dom is not used as the persistence proof.
   $seedHtml = Invoke-LumenChromeDump ($base+"?qa=e2e-seed") $seedDom $seedErr 12000
   if ($seedHtml -match "REAL01_E2E_FAIL") {
     throw "REAL01_E2E_SEED_FAIL - inspect evidence\\real-01\\windows\\e2e-seed-dom.html"
   }

   # Let Chrome release the profile cleanly. Then start a NEW Chrome process
   # with the SAME profile. Persistence across browser restart is a stricter
   # proof than an in-page reload.
   Start-Sleep -Milliseconds 1200
   $verifyHtml = Invoke-LumenChromeDump ($base+"?qa=e2e-verify") $verifyDom $verifyErr 5000
   if ($verifyHtml -notmatch "REAL01_E2E_PASS") {
     throw "REAL01_E2E_PERSISTENCE_FAIL - inspect evidence\\real-01\\windows\\e2e-verify-dom.html"
   }
   Write-Host "REAL-01 BROWSER E2E + PERSISTENCE ACROSS BROWSER RESTART PASS"
 } finally {
   Start-Sleep -Milliseconds 500
   Remove-Item $profile -Recurse -Force -ErrorAction SilentlyContinue
 }
 $shots = @(
   @{n="desktop-canon.png"; size="1672,941"; url=$base+"?qa=canon"},
   @{n="desktop-lesson.png"; size="1672,941"; url=$base+"?qa=lesson3"},
   @{n="desktop-workshop.png"; size="1672,941"; url=$base+"?qa=workshop"},
   @{n="desktop-transmission.png"; size="1672,941"; url=$base+"?qa=transmission"},
   @{n="mobile-sanctuary.png"; size="390,844"; url=$base+"?qa=canon"},
   @{n="mobile-lesson.png"; size="390,844"; url=$base+"?qa=lesson3"},
   @{n="mobile-workshop.png"; size="390,844"; url=$base+"?qa=workshop"},
   @{n="mobile-transmission.png"; size="390,844"; url=$base+"?qa=transmission"}
 )
 function Invoke-LumenChromeScreenshot([string]$Url,[string]$Size,[string]$Out,[string]$Name) {
   if (Test-Path $Out) { Remove-Item $Out -Force }

   $stdout = Join-Path $evidence ($Name + ".chrome.stdout.txt")
   $stderr = Join-Path $evidence ($Name + ".chrome.stderr.txt")
   Remove-Item $stdout,$stderr -Force -ErrorAction SilentlyContinue

   $args = @(
     "--headless=new",
     "--hide-scrollbars",
     "--disable-gpu",
     "--no-first-run",
     "--no-default-browser-check",
     "--window-size=$Size",
     "--screenshot=$Out",
     $Url
   )

   $proc = Start-Process -FilePath $chrome `
     -ArgumentList $args `
     -NoNewWindow -Wait -PassThru `
     -RedirectStandardOutput $stdout `
     -RedirectStandardError $stderr

   if ($proc.ExitCode -ne 0) {
     throw "REAL01_CAPTURE_CHROME_FAIL: name=$Name exit=$($proc.ExitCode)"
   }

   $deadline = (Get-Date).AddSeconds(12)
   while ((-not (Test-Path $Out)) -and (Get-Date) -lt $deadline) {
     Start-Sleep -Milliseconds 250
   }

   if (-not (Test-Path $Out)) {
     throw "REAL01_CAPTURE_MISSING: $Name"
   }

   if ((Get-Item $Out).Length -lt 10000) {
     throw "REAL01_CAPTURE_TOO_SMALL: $Name bytes=$((Get-Item $Out).Length)"
   }
 }

 foreach ($s in $shots) {
   $p = Join-Path $evidence $s.n
   Invoke-LumenChromeScreenshot $s.url $s.size $p $s.n
 }
 Write-Host "REAL-01 DESKTOP/MOBILE CAPTURES PASS"
 $manifest = [ordered]@{
   mission = "LUMEN-REAL-01"
   browser = "Google Chrome"
   canon_sha256 = $canonHash
   desktop = @("desktop-canon.png","desktop-lesson.png","desktop-workshop.png","desktop-transmission.png")
   mobile = @("mobile-sanctuary.png","mobile-lesson.png","mobile-workshop.png","mobile-transmission.png")
   result = "READY_FOR_INDEPENDENT_REVIEW"
   note = "Screenshots prove browser rendering. E2E persistence is verified across a fresh Chrome process using the same profile. User actions and return remain self-reported; no publication is approved."
 }
 $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $evidence "browser-manifest.json") -Encoding UTF8
 $pack = Join-Path $root "LUMEN-REVIEW-PACK-REAL-01.zip"
 if (Test-Path $pack) { Remove-Item $pack -Force }
 $packFiles = @(
   (Join-Path $evidence "*.png"),
   (Join-Path $evidence "browser-manifest.json"),
   (Join-Path $evidence "technical-validation.json"),
   (Join-Path $evidence "unit-tests.txt"),
   (Join-Path $evidence "e2e-seed-dom.html"),
   (Join-Path $evidence "e2e-verify-dom.html"),
   (Join-Path $root "LUMEN-REAL-01-REPORT.md"),
   (Join-Path $root "release.json"),
   (Join-Path $root "state\real-program.json"),
   (Join-Path $root "content\catalog.json"),
   (Join-Path $root "content\sources\sources.json"),
   (Join-Path $root "content\lessons\*.json"),
   (Join-Path $root "projects\golden-journey\index.html"),
   (Join-Path $root "projects\golden-journey\styles.css"),
   (Join-Path $root "projects\golden-journey\app.js")
 )
 Compress-Archive -Path $packFiles -DestinationPath $pack -Force
 Write-Host "REVIEW PACK READY: $pack"
} finally {
 if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force }
}

