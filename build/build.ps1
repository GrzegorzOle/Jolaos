# Buduje Jolaos.exe (PyInstaller) i instalator (Inno Setup), opcjonalnie podpisuje oba.
#
# Uzycie:
#   powershell -ExecutionPolicy Bypass -File build\build.ps1
#   powershell -ExecutionPolicy Bypass -File build\build.ps1 -Sign -Thumbprint <odcisk SHA-1 certyfikatu>
#
# Wymagania: Python 3.11+, pip install -r requirements-dev.txt, Inno Setup 6.
# Do podpisu: signtool.exe z Windows SDK oraz certyfikat code signing w magazynie
# CurrentUser\My (karta Certum jest widoczna tam po uruchomieniu proCertum CardManager).
# Odcisk mozna tez podac w zmiennej srodowiskowej JOLAOS_SIGN_THUMBPRINT.

param(
    [switch]$Sign,
    [string]$Thumbprint = $env:JOLAOS_SIGN_THUMBPRINT,
    [string]$TimestampUrl = "http://time.certum.pl"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Find-Tool {
    param([string]$Name, [string[]]$Candidates)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $found = $Candidates | Where-Object { Test-Path $_ } | Sort-Object -Descending | Select-Object -First 1
    if (-not $found) { throw "Nie znaleziono $Name." }
    return $found
}

$version = (python -c "import jolaos; print(jolaos.__version__)").Trim()
Write-Host "Jolaos $version"

$signtool = $null
if ($Sign) {
    if (-not $Thumbprint) { throw "Podaj -Thumbprint albo ustaw JOLAOS_SIGN_THUMBPRINT." }
    $kits = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.*\x64\signtool.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | ForEach-Object { $_.FullName }
    $signtool = Find-Tool "signtool.exe" $kits
    Write-Host "Podpis: $signtool, certyfikat $Thumbprint"
}

$signArgs = @("sign", "/sha1", $Thumbprint, "/fd", "sha256", "/tr", $TimestampUrl, "/td", "sha256", "/d", "Jolaos")

function Sign-File {
    param([string]$Path)
    if (-not $Sign) { return }
    Write-Host "  podpisuje $Path (moze pojawic sie pytanie o PIN karty)"
    & $signtool @signArgs $Path
    if ($LASTEXITCODE -ne 0) { throw "Podpisywanie $Path nie powiodlo sie." }
    & $signtool verify /pa /q $Path
    if ($LASTEXITCODE -ne 0) { throw "Weryfikacja podpisu $Path nie powiodla sie." }
}

Write-Host "[1/5] Ikona"
python build\make_icon.py

Write-Host "[2/5] Testy"
python -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw "Testy nie przeszly." }

Write-Host "[3/5] PyInstaller"
python -m PyInstaller build\jolaos.spec --noconfirm --clean --distpath dist --workpath build\work
if ($LASTEXITCODE -ne 0) { throw "PyInstaller zakonczyl sie bledem." }
Sign-File "dist\Jolaos\Jolaos.exe"

Write-Host "[4/5] Inno Setup"
$iscc = Find-Tool "ISCC.exe" @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)
$isccArgs = @("build\installer.iss", "/DAppVersion=$version", "/Q")
if ($Sign) {
    # Inno Setup podpisuje deinstalator i sam instalator przez build\sign.cmd;
    # $p to parametry z dyrektywy SignTool w .iss, czyli nazwa pliku.
    $env:JOLAOS_SIGNTOOL = $signtool
    $env:JOLAOS_SIGN_THUMBPRINT = $Thumbprint
    $env:JOLAOS_SIGN_TSA = $TimestampUrl
    # Sciezka w postaci krotkiej (8.3), zeby polecenie nie wymagalo cudzyslowow.
    $fso = New-Object -ComObject Scripting.FileSystemObject
    $signCmd = $fso.GetFile("$PSScriptRoot\sign.cmd").ShortPath
    $isccArgs = $isccArgs | Where-Object { $_ -ne "/Q" }
    $isccArgs += "/DSign", "/Ssigntool=cmd /c $signCmd `$p"
}
& $iscc @isccArgs
if ($LASTEXITCODE -ne 0) { throw "Inno Setup zakonczyl sie bledem." }

Write-Host "[5/5] Sumy kontrolne"
$setup = Get-Item "dist\Jolaos-Setup-$version.exe"
if ($Sign) {
    & $signtool verify /pa /q $setup.FullName
    if ($LASTEXITCODE -ne 0) { throw "Instalator nie ma poprawnego podpisu." }
}
# certutil zamiast Get-FileHash: dziala tez w okrojonych instalacjach PowerShella.
$hash = (certutil -hashfile $setup.FullName SHA256 | Select-Object -Index 1).Trim().ToLower()
"$hash *$($setup.Name)" | Set-Content -Encoding ascii "$($setup.FullName).sha256"

Write-Host ""
Write-Host "Gotowe:"
Write-Host "  $($setup.FullName)  ($([math]::Round($setup.Length/1MB,1)) MB)"
Write-Host "  SHA-256: $hash"
if ($Sign) { Write-Host "  podpisano certyfikatem $Thumbprint" } else { Write-Host "  (bez podpisu)" }
