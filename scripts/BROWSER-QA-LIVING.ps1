$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $Root "projects\golden-sanctuary"
$Evidence = Join-Path $Root "evidence"
New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
$candidates = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe","${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe","$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe","${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe") | Where-Object { $_ -and (Test-Path $_) }
if (-not $candidates) { throw "BROWSER_QA_BLOCKED: Chrome or Edge not found." }
$Browser = $candidates[0]
function To-FileUrl([string]$Path,[string]$Query=""){ $u=([System.Uri]::new((Resolve-Path $Path).Path)).AbsoluteUri; if($Query){return "$u`?$Query"}; return $u }
function Compare-Bitmap([string]$PathA,[string]$PathB,[int]$Step=8){ Add-Type -AssemblyName System.Drawing; $a=New-Object System.Drawing.Bitmap($PathA);$b=New-Object System.Drawing.Bitmap($PathB);try{if($a.Width-ne$b.Width-or$a.Height-ne$b.Height){throw "DIMENSION_MISMATCH"};$sum=[double]0;$count=[long]0;for($y=0;$y-lt$a.Height;$y+=$Step){for($x=0;$x-lt$a.Width;$x+=$Step){$pa=$a.GetPixel($x,$y);$pb=$b.GetPixel($x,$y);$sum += [Math]::Abs([int]$pa.R-[int]$pb.R)+[Math]::Abs([int]$pa.G-[int]$pb.G)+[Math]::Abs([int]$pa.B-[int]$pb.B);$count+=3}};return $sum/$count}finally{$a.Dispose();$b.Dispose()} }
$Index=Join-Path $Project "index.html"
$Golden=Join-Path $Evidence "browser-golden-rest-living-01.png"
$Library=Join-Path $Evidence "browser-library-idle-living-01.png"
$Search=Join-Path $Evidence "browser-library-search-living-01.png"
$Article=Join-Path $Evidence "browser-article-living-01.png"
$common=@("--headless=new","--disable-gpu","--hide-scrollbars","--window-size=1672,941","--force-device-scale-factor=1","--virtual-time-budget=1800")
& $Browser @common "--screenshot=$Golden" (To-FileUrl $Index "qa=rest&scene=home") | Out-Null
& $Browser @common "--screenshot=$Library" (To-FileUrl $Index "qa=library-idle&scene=library") | Out-Null
& $Browser @common "--screenshot=$Search" (To-FileUrl $Index "qa=library-search&scene=library") | Out-Null
& $Browser @common "--screenshot=$Article" (To-FileUrl $Index "qa=article&scene=article") | Out-Null
foreach($f in @($Golden,$Library,$Search,$Article)){if(-not(Test-Path $f)-or(Get-Item $f).Length-lt10000){throw "BROWSER_QA_FAIL: missing capture $f"}}
$canonHome=Join-Path $Root "assets\canon\01_SANCTUAIRE.png";$canonLibrary=Join-Path $Root "assets\canon\03_BIBLIOTHEQUE.png";$canonArticle=Join-Path $Root "assets\canon\07_ARTICLE_MONDE_LUCIDE.png"
$homeMae=Compare-Bitmap $canonHome $Golden 8;$libraryMae=Compare-Bitmap $canonLibrary $Library 8;$articleMae=Compare-Bitmap $canonArticle $Article 8;$searchDelta=Compare-Bitmap $Library $Search 8
$homePass=$homeMae-le2.5;$libraryPass=$libraryMae-le1.0;$articlePass=$articleMae-le1.0;$searchPass=$searchDelta-ge0.15
$result=if($homePass-and$libraryPass-and$articlePass-and$searchPass){"PASS"}else{"ITERATE"}
$report=[ordered]@{ts=[DateTimeOffset]::UtcNow.ToString("o");result=$result;iteration="LUMEN-LIVING-SYSTEM-01";browser=$Browser;viewport=@(1672,941);golden_rest_mae=[Math]::Round($homeMae,4);library_idle_mae=[Math]::Round($libraryMae,4);article_idle_mae=[Math]::Round($articleMae,4);search_state_delta=[Math]::Round($searchDelta,4);checks=[ordered]@{golden_rest_fidelity=$homePass;library_idle_fidelity=$libraryPass;search_state_rendered=$searchPass;article_fidelity=$articlePass};captures=@("evidence/browser-golden-rest-living-01.png","evidence/browser-library-idle-living-01.png","evidence/browser-library-search-living-01.png","evidence/browser-article-living-01.png");note="Observed browser QA for LUMEN-LIVING-SYSTEM-01."}
$report|ConvertTo-Json -Depth 6|Set-Content -Encoding UTF8 (Join-Path $Evidence "browser-qa-living-01.json")
$report|ConvertTo-Json -Depth 6
if($result-ne"PASS"){throw "BROWSER_QA_ITERATE_LIVING_01: home=$homeMae library=$libraryMae article=$articleMae searchDelta=$searchDelta"}
