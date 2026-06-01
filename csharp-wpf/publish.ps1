#Requires -Version 5.1
<#
.SYNOPSIS
    Sestavi a publikuje KIOSK_EMISTR solution pro Windows x64.

.DESCRIPTION
    Publikuje KioskEmistr.Wpf (runtime) a KioskEmistr.Generator.Wpf (GUI generator)
    jako self-contained exe pro win-x64, pak sestaví release adresár.

.PARAMETER Configuration
    Debug nebo Release (výchozí: Release)

.PARAMETER OutputDir
    Cílová složka pro hotový release (výchozí: .\release)

.EXAMPLE
    .\publish.ps1
    .\publish.ps1 -Configuration Debug -OutputDir C:\Temp\kiosk-release
#>

[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',

    [string]$OutputDir = "$PSScriptRoot\release"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SolutionFile = "$PSScriptRoot\KioskEmistr.sln"
$WpfProject   = "$PSScriptRoot\src\KioskEmistr.Wpf\KioskEmistr.Wpf.csproj"
$GenProject   = "$PSScriptRoot\src\KioskEmistr.Generator.Wpf\KioskEmistr.Generator.Wpf.csproj"
$CliProject   = "$PSScriptRoot\src\KioskEmistr.Generator\KioskEmistr.Generator.csproj"

$RuntimeOut   = "$OutputDir\runtime"
$GeneratorOut = "$OutputDir\generator"
$CliOut       = "$OutputDir\generator-cli"

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host ">>> $msg" -ForegroundColor Cyan
}

function Invoke-Publish([string]$project, [string]$outputFolder, [string]$label) {
    Write-Step "Publish: $label"
    $args = @(
        'publish', $project,
        '--configuration', $Configuration,
        '--runtime', 'win-x64',
        '--self-contained', 'true',
        '-p:PublishSingleFile=true',
        '-p:EnableCompressionInSingleFile=true',
        '-p:IncludeNativeLibrariesForSelfExtract=true',
        '--output', $outputFolder,
        '--nologo'
    )
    & dotnet @args
    if ($LASTEXITCODE -ne 0) { throw "Publish selhal pro $label (exit $LASTEXITCODE)" }
    Write-Host "  OK -> $outputFolder" -ForegroundColor Green
}

# --- Kontrola prerekvizit ---
Write-Step "Kontrola prerekvizit"
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw ".NET SDK nebylo nalezeno. Nainstaluj z https://dotnet.microsoft.com/download"
}
$sdkVersion = & dotnet --version
Write-Host "  .NET SDK: $sdkVersion"
if (-not (Test-Path $SolutionFile)) {
    throw "Solution soubor nenalezen: $SolutionFile"
}

# --- Restore ---
Write-Step "Restore NuGet balicku"
& dotnet restore $SolutionFile --nologo
if ($LASTEXITCODE -ne 0) { throw "Restore selhal" }

# --- Publish ---
if (Test-Path $OutputDir) {
    Write-Step "Cisteni stare release slozky"
    Remove-Item $OutputDir -Recurse -Force
}

Invoke-Publish $WpfProject   $RuntimeOut   "KioskEmistr.Wpf (runtime browser)"
Invoke-Publish $GenProject   $GeneratorOut "KioskEmistr.Generator.Wpf (GUI generator)"

# Generator ocekava runtime v podslozce 'runtime/' vedle sebe (AppContext.BaseDirectory + "runtime")
Write-Step "Kopirovani runtime pro generator"
Copy-Item -Path $RuntimeOut -Destination "$GeneratorOut\runtime" -Recurse -Force
Write-Host "  OK -> $GeneratorOut\runtime" -ForegroundColor Green

Invoke-Publish $CliProject   $CliOut       "KioskEmistr.Generator CLI"

# --- Zkopírovat assets ---
Write-Step "Kopirování assetu"
$SrcAssets = "$PSScriptRoot\src\KioskEmistr.Generator.Wpf\Assets"
if (Test-Path $SrcAssets) {
    Copy-Item -Path "$SrcAssets\*" -Destination $GeneratorOut -Recurse -Force
    Write-Host "  Assety zkopírovány do $GeneratorOut"
}

# --- README ---
Write-Step "Generování release README"
$ReadmePath = "$OutputDir\README.txt"
@"
KIOSK_EMISTR Release
=====================
Konfigurace: $Configuration
Datum:        $(Get-Date -Format 'yyyy-MM-dd HH:mm')

Obsah release:
  runtime\          - KioskEmistr.Wpf.exe (browser runtime pro kiosk)
  generator\        - KioskEmistr.Generator.Wpf.exe (GUI generator kiosk balicku)
  generator-cli\    - KioskEmistr.Generator.exe (CLI generator pro scripty a CI)

Pouziti:
  1. Spusti generator\KioskEmistr.Generator.Wpf.exe
  2. Vyplň název aplikace, URL a cestu k runtime\ složce
  3. Klikni VYGENEROVAT — vznikne složka s hotovým kioskerm

CLI generator:
  KioskEmistr.Generator.exe --app-name MujKiosk --url https://example.com \
    --runtime-dir .\runtime --output-dir C:\kiosky
"@ | Set-Content -Encoding UTF8 $ReadmePath

# --- Výsledek ---
Write-Host ""
Write-Host ('=' * 60) -ForegroundColor Cyan
Write-Host "  RELEASE HOTOV: $OutputDir" -ForegroundColor Green
Write-Host ""
Write-Host "  Soubory:" -ForegroundColor Gray
Get-ChildItem $OutputDir -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($OutputDir.Length + 1)
    $size = '{0,8:N0} KB' -f ([math]::Round($_.Length / 1024, 0))
    Write-Host "    $size  $rel" -ForegroundColor Gray
}
Write-Host ('=' * 60) -ForegroundColor Cyan
