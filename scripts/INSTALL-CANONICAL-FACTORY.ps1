param([Parameter(Mandatory=$true)][string]$RepoPath)
$ErrorActionPreference = "Stop"
$overlay = Resolve-Path (Join-Path $PSScriptRoot "..")
$repo = Resolve-Path $RepoPath
$canon = Join-Path $repo "assets\canon\01_SANCTUAIRE.png"
if (-not (Test-Path $canon)) { throw "INSTALL_REFUSED: canonical asset missing" }
$expected = "e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1"
$actual = (Get-FileHash -Algorithm SHA256 $canon).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "INSTALL_REFUSED: Golden Sanctuary hash mismatch" }

Copy-Item (Join-Path $overlay "AGENTS.md") (Join-Path $repo "AGENTS.md") -Force
foreach ($d in @(".lumen\architecture",".lumen\contracts",".lumen\tasks",".github\workflows")) {
  New-Item -ItemType Directory -Path (Join-Path $repo $d) -Force | Out-Null
}
Copy-Item (Join-Path $overlay ".lumen\architecture\*") (Join-Path $repo ".lumen\architecture") -Force
Copy-Item (Join-Path $overlay ".lumen\contracts\*") (Join-Path $repo ".lumen\contracts") -Force
Copy-Item (Join-Path $overlay ".lumen\tasks\*") (Join-Path $repo ".lumen\tasks") -Force
Copy-Item (Join-Path $overlay ".github\workflows\*") (Join-Path $repo ".github\workflows") -Force
Write-Host "LUMEN_ARCH_01_OVERLAY_INSTALLED"
Write-Host "Golden Sanctuary preserved: $actual"
