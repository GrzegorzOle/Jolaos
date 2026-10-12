# Buduje Jolaos.exe (PyInstaller) i instalator (Inno Setup).
# Uzycie: powershell -ExecutionPolicy Bypass -File build\build.ps1
# Wymagania: Python 3.11+, pip install pyinstaller, Inno Setup 6 (winget install JRSoftware.InnoSetup)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$version = (python -c "import jolaos; print(jolaos.__version__)").Trim()
Write-Host "Jolaos $version"

Write-Host "[1/4] Ikona"
python build\make_icon.py

Write-Host "[2/4] Testy"
python -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw "Testy nie przeszly." }

Write-Host "[3/4] PyInstaller"
python -m PyInstaller build\jolaos.spec --noconfirm --clean --distpath dist --workpath build\work
if ($LASTEXITCODE -ne 0) { throw "PyInstaller zakonczyl sie bledem." }

Write-Host "[4/4] Inno Setup"
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if (-not $iscc) {
    $candidates = @(
        "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $found = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $found) { throw "Nie znaleziono ISCC.exe. Zainstaluj Inno Setup 6." }
    $iscc = $found
} else {
    $iscc = $iscc.Source
}
& $iscc "build\installer.iss" "/DAppVersion=$version" /Q
if ($LASTEXITCODE -ne 0) { throw "Inno Setup zakonczyl sie bledem." }

Write-Host ""
Write-Host "Gotowe:"
Get-ChildItem dist\Jolaos-Setup-*.exe | ForEach-Object { Write-Host "  $($_.FullName)  ($([math]::Round($_.Length/1MB,1)) MB)" }
