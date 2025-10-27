<#  Switch-Python.ps1 (auto-install, robust, ASCII-safe)
    Usage:
      .\Switch-Python.ps1 -Version 3.13
      .\Switch-Python.ps1 -Version 3.9
    Notes:
      - Auto-installs the requested version via winget if missing.
      - Open a NEW PowerShell after it finishes to see PATH changes.
      - Turn OFF python/python3 aliases in Settings -> Apps -> App execution aliases.
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [ValidatePattern('^\d+\.\d+$')]
  [string]$Version,
  [switch]$KeepOtherPythonsInPath
)

$ErrorActionPreference = 'Stop'
$logPath   = Join-Path $env:USERPROFILE ("Desktop\SwitchPython_log_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
$mustPause = $true
try { Start-Transcript -Path $logPath -ErrorAction SilentlyContinue | Out-Null } catch {}

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "[ OK ] $m" -ForegroundColor Green }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Err($m){ Write-Host "[ERR ] $m" -ForegroundColor Red }

function Test-PyVersion {
  param([string]$Ver)
  try { & py -$Ver -V | Out-Null; return $true } catch { return $false }
}

function Ensure-PythonVersion {
  param([string]$Ver)
  if (Test-PyVersion $Ver) { return $true }

  Info "Python $Ver not detected. Attempting to install with winget..."
  $installed = $false
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($winget) {
    try {
      winget install --exact --id ("Python.Python.{0}" -f $Ver) --accept-source-agreements --accept-package-agreements
      Start-Sleep -Seconds 2
      if (Test-PyVersion $Ver) { $installed = $true }
    } catch {
      Warn "winget install failed or package not found for Python.Python.$Ver."
    }
  } else {
    Warn "winget not found; skipping winget install."
  }

  if (-not $installed) {
    Info "Trying py launcher auto-install path..."
    $env:PYLAUNCHER_ALLOW_INSTALL = "1"
    try { & py -$Ver -V | Out-Null } catch {}
    Start-Sleep -Seconds 2
    if (Test-PyVersion $Ver) { $installed = $true }
  }

  if (-not $installed) {
    Err  "Unable to install Python $Ver automatically."
    Warn "Install manually from https://www.python.org/downloads/windows/ and re-run the script."
    return $false
  }

  Ok "Python $Ver installed and detected."
  return $true
}

try {
  Info "Checking Python $Version availability..."
  if (-not (Ensure-PythonVersion -Ver $Version)) {
    throw "Python $Version not available after installation attempts."
  }

  Info "Setting py launcher default to $Version"
  [Environment]::SetEnvironmentVariable("PY_PYTHON",$Version,"User")
  [Environment]::SetEnvironmentVariable("PY_PYTHON3",$Version,"User")
  $pyIniPath = Join-Path $env:LOCALAPPDATA 'py.ini'
  Set-Content -Path $pyIniPath -Value ("[defaults]`npython={0}" -f $Version) -Encoding ASCII

  Info "Locating Python $Version executable..."
  $exe = & py -$Version -c "import sys; print(sys.executable)"
  if (-not $exe) { throw "Could not resolve sys.executable for Python $Version." }
  $pyDir      = Split-Path $exe
  $scriptsDir = Join-Path $pyDir 'Scripts'
  Ok "python.exe : $exe"

  $py3Exe = Join-Path $pyDir 'python3.exe'
  if (-not (Test-Path $py3Exe)) {
    Copy-Item (Join-Path $pyDir 'python.exe') $py3Exe -Force
    Ok "Created python3.exe next to python.exe"
  }

  Info "Re-ordering User PATH to prioritize Python $Version"
  $winApps  = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'
  $shimBin  = Join-Path $env:LOCALAPPDATA 'Python\bin'
  $userPathOld = [Environment]::GetEnvironmentVariable("Path","User")
  $backup   = Join-Path $env:USERPROFILE ("Desktop\PATH_backup_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
  Set-Content $backup $userPathOld
  Ok "PATH backed up to $backup"

  $parts = ($userPathOld -split ';' | Where-Object { $_ }) | ForEach-Object { $_.Trim() }
  $parts = $parts | Where-Object { $_ -ne $pyDir -and $_ -ne $scriptsDir -and $_ -ne $shimBin }
  if (-not $KeepOtherPythonsInPath) {
    $parts = $parts | Where-Object { $_ -notmatch 'Python3\d{2}(\\|$)' }
  }
  $noWinApps = $parts | Where-Object { $_ -ne $winApps }
  $newPath   = (@($pyDir,$scriptsDir) + $noWinApps + @($winApps) | Select-Object -Unique) -join ';'
  [Environment]::SetEnvironmentVariable("Path",$newPath,"User")
  Ok "User PATH updated."

  Warn "Check App execution aliases: turn OFF python.exe & python3.exe in Settings -> Apps -> App execution aliases."

  # ----------------------- Clean Summary -----------------------
  Write-Host ""
  Write-Host "============================================================" -ForegroundColor DarkCyan
  Write-Host (" PYTHON SWITCH COMPLETE  -  Default is now Python {0}" -f $Version) -ForegroundColor Cyan
  Write-Host "============================================================" -ForegroundColor DarkCyan
  Write-Host ""
  $finalVer = (& py -$Version -V)
  Write-Host (" Active Python Version : " + $finalVer) -ForegroundColor Green
  Write-Host ""
  Write-Host " IMPORTANT: Close and reopen PowerShell to load the new PATH." -ForegroundColor Magenta
  Write-Host " Then verify with:" -ForegroundColor Gray
  Write-Host "   python -V" -ForegroundColor Cyan
  Write-Host "   python3 -V" -ForegroundColor Cyan
  Write-Host "   where python" -ForegroundColor Cyan
  Write-Host ""
  Ok ("Log saved to: {0}" -f $logPath)
  Write-Host ""
  Write-Host "--------------------- Made with love -----------------------" -ForegroundColor DarkGray
  Write-Host "        *****       *****" -ForegroundColor Gray
  Write-Host "      *********   *********" -ForegroundColor Gray
  Write-Host "     ***********************" -ForegroundColor Gray
  Write-Host "      *********************" -ForegroundColor Gray
  Write-Host "        *****************" -ForegroundColor Gray
  Write-Host "          *************" -ForegroundColor Gray
  Write-Host "            *********" -ForegroundColor Gray
  Write-Host "              *****" -ForegroundColor Gray
  Write-Host "                *" -ForegroundColor Gray
  Write-Host "  by Aman Khan - The AI PM Playbook Team" -ForegroundColor Gray
  Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray

} catch {
  Err ("{0}" -f $_.Exception.Message)
  if ($_.ScriptStackTrace) { Warn $_.ScriptStackTrace }
} finally {
  try { Stop-Transcript | Out-Null } catch {}
  if ($mustPause) { Read-Host "Press Enter to close this window" | Out-Null }
}
