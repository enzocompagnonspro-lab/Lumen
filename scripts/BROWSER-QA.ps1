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
if (-not $candidates) { throw "BROWSER_QA_BLOCKED: Chrome ou Edge introuvable." }
$Browser = $candidates[0]

function To-FileUrl([string]$Path, [string]$Query="") {
  $u = ([System.Uri]::new((Resolve-Path $Path).Path)).AbsoluteUri
  if ($Query) { return "$u`?$Query" }
  return $u
}
function Compare-Bitmap([string]$PathA,[string]$PathB,[int]$Step=8) {
  Add-Type -AssemblyName System.Drawing
  $a = New-Object System.Drawing.Bitmap($PathA)
  $b = New-Object System.Drawing.Bitmap($PathB)
  try {
    if ($a.Width -ne $b.Width -or $a.Height -ne $b.Height) { throw "BROWSER_QA_FAIL: dimensions differentes: $PathA / $PathB" }
    $sum=[double]0; $count=[long]0
    for($y=0;$y -lt $a.Height;$y+=$Step){
      for($x=0;$x -lt $a.Width;$x+=$Step){
        $pa=$a.GetPixel($x,$y);$pb=$b.GetPixel($x,$y)
        $sum += [Math]::Abs([int]$pa.R-[int]$pb.R)+[Math]::Abs([int]$pa.G-[int]$pb.G)+[Math]::Abs([int]$pa.B-[int]$pb.B)
        $count += 3
      }
    }
    return $sum/$count
  } finally { $a.Dispose();$b.Dispose() }
}


function Measure-EdgeEnergy([string]$Path,[int]$Step=4) {
  Add-Type -AssemblyName System.Drawing
  $bmp = New-Object System.Drawing.Bitmap($Path)
  try {
    $sum=[double]0; $count=[long]0
    for($y=0;$y -lt ($bmp.Height-1);$y+=$Step){
      for($x=0;$x -lt ($bmp.Width-1);$x+=$Step){
        $p=$bmp.GetPixel($x,$y); $px=$bmp.GetPixel($x+1,$y); $py=$bmp.GetPixel($x,$y+1)
        $sum += [Math]::Abs([int]$p.R-[int]$px.R)+[Math]::Abs([int]$p.G-[int]$px.G)+[Math]::Abs([int]$p.B-[int]$px.B)
        $sum += [Math]::Abs([int]$p.R-[int]$py.R)+[Math]::Abs([int]$p.G-[int]$py.G)+[Math]::Abs([int]$p.B-[int]$py.B)
        $count += 6
      }
    }
    if($count -eq 0){ return 0.0 }
    return $sum/$count
  } finally { $bmp.Dispose() }
}

$Index = Join-Path $Project "index.html"
$CanonShot = Join-Path $Evidence "browser-canon-home-01r2.png"
$RestShot = Join-Path $Evidence "browser-live-home-rest-01r2.png"
$MotionShot = Join-Path $Evidence "browser-live-home-motion-01r2.png"
$LibraryShot = Join-Path $Evidence "browser-live-library-01r2.png"
$common = @("--headless=new","--disable-gpu","--hide-scrollbars","--window-size=1672,941","--force-device-scale-factor=1","--virtual-time-budget=1800")

& $Browser @common "--screenshot=$CanonShot" (To-FileUrl $Index "qa=canon") | Out-Null
& $Browser @common "--screenshot=$RestShot" (To-FileUrl $Index "qa=rest&scene=home") | Out-Null
& $Browser @common "--screenshot=$MotionShot" (To-FileUrl $Index "qa=motion&scene=home") | Out-Null
& $Browser @common "--screenshot=$LibraryShot" (To-FileUrl $Index "qa=rest&scene=library") | Out-Null
foreach($f in @($CanonShot,$RestShot,$MotionShot,$LibraryShot)){
  if(-not(Test-Path $f) -or (Get-Item $f).Length -lt 10000){throw "BROWSER_QA_FAIL: capture manquante/vide: $f"}
}

$canonPath = Join-Path $Root "assets\canon\01_SANCTUAIRE.png"
$canonMae = Compare-Bitmap $canonPath $CanonShot 8
$restMae = Compare-Bitmap $CanonShot $RestShot 8
$motionDelta = Compare-Bitmap $RestShot $MotionShot 8
$canonEdge = Measure-EdgeEnergy $CanonShot 4
$restEdge = Measure-EdgeEnergy $RestShot 4
$sharpnessRatio = if($canonEdge -gt 0){$restEdge/$canonEdge}else{0}

$canonPass = $canonMae -le 3.0
$restPass = $restMae -le 2.5
$motionPass = ($motionDelta -ge 0.20 -and $motionDelta -le 12.0)
$sharpPass = $sharpnessRatio -ge 0.90
$result = if($canonPass -and $restPass -and $motionPass -and $sharpPass){"PASS"}else{"ITERATE"}
$report=[ordered]@{
  ts=[DateTimeOffset]::UtcNow.ToString("o")
  result=$result
  iteration="LUMEN-SCENE-ENGINE-01R2"
  browser=$Browser
  viewport=@(1672,941)
  canon_sampled_mae=[Math]::Round($canonMae,4)
  live_rest_vs_canon_sampled_mae=[Math]::Round($restMae,4)
  live_motion_delta_sampled_mae=[Math]::Round($motionDelta,4)
  canon_edge_energy=[Math]::Round($canonEdge,4)
  rest_edge_energy=[Math]::Round($restEdge,4)
  rest_sharpness_ratio=[Math]::Round($sharpnessRatio,4)
  checks=[ordered]@{
    canon_exact=$canonPass
    live_remains_close_to_canon=$restPass
    differential_motion_observed=$motionPass
    sharpness_preserved=$sharpPass
  }
  captures=@(
    "evidence/browser-canon-home-01r2.png",
    "evidence/browser-live-home-rest-01r2.png",
    "evidence/browser-live-home-motion-01r2.png",
    "evidence/browser-live-library-01r2.png"
  )
  note="Observed Chrome/Edge browser QA. Motion screenshot uses deterministic multi-layer parallax state; particles are disabled in QA modes."
}
$report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 (Join-Path $Evidence "browser-qa-local-01r2.json")
$report | ConvertTo-Json -Depth 6
if($result -ne "PASS"){throw "BROWSER_QA_ITERATE_01R2: canon=$canonMae rest=$restMae motionDelta=$motionDelta"}
