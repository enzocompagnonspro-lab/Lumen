$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $Root "projects\golden-sanctuary"
$Evidence = Join-Path $Root "evidence"
New-Item -ItemType Directory -Force -Path $Evidence | Out-Null

$candidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { $_ -and (Test-Path $_) }
if (-not $candidates) { throw "BROWSER_QA_BLOCKED: Chrome or Edge not found." }
$Browser = $candidates[0]
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) { throw "BROWSER_QA_BLOCKED: python not found in PATH." }

function Get-FreeTcpPort {
  $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback,0)
  $listener.Start()
  try { return ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port }
  finally { $listener.Stop() }
}

function Wait-Http([string]$Url,[int]$TimeoutMs=10000) {
  $elapsed = 0
  while ($elapsed -lt $TimeoutMs) {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
      if ($r.StatusCode -eq 200) { return }
    } catch {}
    Start-Sleep -Milliseconds 200
    $elapsed += 200
  }
  throw "BROWSER_QA_BLOCKED: local HTTP server did not become ready at $Url"
}

function Wait-Capture([string]$Path,[int]$MinBytes=10000,[int]$TimeoutMs=15000) {
  $elapsed = 0
  while ($elapsed -lt $TimeoutMs) {
    if ((Test-Path $Path) -and ((Get-Item $Path).Length -ge $MinBytes)) { return }
    Start-Sleep -Milliseconds 200
    $elapsed += 200
  }
  throw "BROWSER_QA_FAIL: missing capture $Path"
}

function Compare-Bitmap([string]$PathA,[string]$PathB,[int]$Step=8) {
  Add-Type -AssemblyName System.Drawing
  $a = New-Object System.Drawing.Bitmap($PathA)
  $b = New-Object System.Drawing.Bitmap($PathB)
  try {
    if ($a.Width -ne $b.Width -or $a.Height -ne $b.Height) { throw "DIMENSION_MISMATCH" }
    $sum = [double]0
    $count = [long]0
    for ($y=0; $y -lt $a.Height; $y += $Step) {
      for ($x=0; $x -lt $a.Width; $x += $Step) {
        $pa = $a.GetPixel($x,$y); $pb = $b.GetPixel($x,$y)
        $sum += [Math]::Abs([int]$pa.R-[int]$pb.R) + [Math]::Abs([int]$pa.G-[int]$pb.G) + [Math]::Abs([int]$pa.B-[int]$pb.B)
        $count += 3
      }
    }
    return $sum/$count
  } finally { $a.Dispose(); $b.Dispose() }
}

$Golden = Join-Path $Evidence "browser-golden-rest-living-02.png"
$Journey = Join-Path $Evidence "browser-journey-idle-living-02.png"
$Vision = Join-Path $Evidence "browser-journey-vision-living-02.png"
$Persist = Join-Path $Evidence "browser-journey-persist-living-02.png"
$PersistDom = Join-Path $Evidence "browser-e2e-persist-dom-living-02.html"
$ServerOut = Join-Path $Evidence "http-server-living-02.out.log"
$ServerErr = Join-Path $Evidence "http-server-living-02.err.log"
foreach ($f in @($Golden,$Journey,$Vision,$Persist,$PersistDom,$ServerOut,$ServerErr)) { Remove-Item $f -Force -ErrorAction SilentlyContinue }

$Profile = Join-Path $env:TEMP ("lumen-e2e-http-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Profile | Out-Null
$Port = Get-FreeTcpPort
$BaseUrl = "http://127.0.0.1:$Port/index.html"
$Server = $null

$common = @(
  "--headless=new",
  "--disable-gpu",
  "--disable-background-mode",
  "--no-first-run",
  "--no-default-browser-check",
  "--hide-scrollbars",
  "--window-size=1672,941",
  "--force-device-scale-factor=1",
  "--run-all-compositor-stages-before-draw",
  "--virtual-time-budget=7000",
  "--user-data-dir=$Profile"
)

try {
  $Server = Start-Process -FilePath $PythonCmd.Source -ArgumentList @("-m","http.server",$Port,"--bind","127.0.0.1") -WorkingDirectory $Project -WindowStyle Hidden -RedirectStandardOutput $ServerOut -RedirectStandardError $ServerErr -PassThru
  Wait-Http $BaseUrl

  & $Browser @common "--screenshot=$Golden" "$BaseUrl`?qa=rest&scene=home" | Out-Null
  Wait-Capture $Golden

  & $Browser @common "--screenshot=$Journey" "$BaseUrl`?qa=journey-idle&scene=journey" | Out-Null
  Wait-Capture $Journey

  & $Browser @common "--screenshot=$Vision" "$BaseUrl`?qa=journey-vision&scene=journey" | Out-Null
  Wait-Capture $Vision

  # One Chrome process seeds Journey state, reloads the same HTTP origin, then verifies LocalStorage.
  $persistDomRaw = & $Browser @common "--dump-dom" "--screenshot=$Persist" "$BaseUrl`?qa=e2e-persist"
  $persistText = ($persistDomRaw -join "`n")
  [System.IO.File]::WriteAllText($PersistDom,$persistText,[System.Text.UTF8Encoding]::new($false))
  Wait-Capture $Persist
  $persistPass = $persistText -match 'data-e2e="persist-ok"'

  $canonHome = Join-Path $Root "assets\canon\01_SANCTUAIRE.png"
  $canonJourney = Join-Path $Root "assets\canon\02_CARTE_DU_VOYAGE.png"
  $homeMae = Compare-Bitmap $canonHome $Golden 8
  $journeyMae = Compare-Bitmap $canonJourney $Journey 8
  $visionDelta = Compare-Bitmap $Journey $Vision 8

  $homePass = $homeMae -le 2.5
  $journeyPass = $journeyMae -le 1.0
  $interactionPass = $visionDelta -ge 0.15
  $result = if ($homePass -and $journeyPass -and $interactionPass -and $persistPass) { "PASS" } else { "ITERATE" }

  $report = [ordered]@{
    ts = [DateTimeOffset]::UtcNow.ToString("o")
    result = $result
    iteration = "LUMEN-LIVING-SYSTEM-02"
    hotfix = "V1.5.2 localhost HTTP + in-browser reload persistence QA"
    browser = $Browser
    origin = "http://127.0.0.1:$Port"
    viewport = @(1672,941)
    golden_rest_mae = [Math]::Round($homeMae,4)
    journey_idle_mae = [Math]::Round($journeyMae,4)
    journey_interaction_delta = [Math]::Round($visionDelta,4)
    checks = [ordered]@{
      golden_rest_fidelity = $homePass
      journey_idle_fidelity = $journeyPass
      journey_interaction_rendered = $interactionPass
      e2e_seed = $persistPass
      persistence_after_reload = $persistPass
    }
    captures = @(
      "evidence/browser-golden-rest-living-02.png",
      "evidence/browser-journey-idle-living-02.png",
      "evidence/browser-journey-vision-living-02.png",
      "evidence/browser-journey-persist-living-02.png"
    )
    diagnostics = @(
      "evidence/browser-e2e-persist-dom-living-02.html",
      "evidence/http-server-living-02.out.log",
      "evidence/http-server-living-02.err.log"
    )
    note = "Observed browser QA over localhost HTTP. Persistence is seeded through article-section click handlers and verified after a real in-browser reload on the same origin."
  }
  $report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $Evidence "browser-qa-living-02.json")
  $report | ConvertTo-Json -Depth 6

  if ($result -ne "PASS") {
    throw "BROWSER_QA_ITERATE_LIVING_02: home=$homeMae journey=$journeyMae delta=$visionDelta persist=$persistPass. Inspect evidence/browser-e2e-persist-dom-living-02.html and HTTP logs."
  }
}
finally {
  if ($Server -and -not $Server.HasExited) { Stop-Process -Id $Server.Id -Force -ErrorAction SilentlyContinue }
  Remove-Item -Recurse -Force $Profile -ErrorAction SilentlyContinue
}
