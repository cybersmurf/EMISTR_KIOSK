# KIOSK_EMISTR — C# + WPF + WebView2

Windows kiosk runtime + generátor kiosk aplikací. .NET 8.

## Projekty

| Projekt | Výstup | Popis |
|---|---|---|
| `KioskEmistr.Wpf` | `KioskEmistr.exe` | Kiosk browser runtime |
| `KioskEmistr.Generator.Wpf` | `KioskGenerator.exe` | GUI generátor — 2 pole + tlačítko |
| `KioskEmistr.Generator` | `kiosk-generator.exe` | CLI generátor |
| `KioskEmistr.Core` | library | Sdílený model + GeneratorService |

## Build

```powershell
# Debug build (všechny projekty)
dotnet build KioskEmistr.sln

# Release — self-contained win-x64 single-file EXE
.\publish.ps1
# výstup: release/runtime/, release/generator/, release/generator-cli/
```

## Konfigurace runtime (`KioskEmistr.Wpf`)

Načítá se v tomto pořadí:
1. `%AppData%/KIOSK_EMISTR/config.json`
2. `appsettings.json` vedle EXE

Klíčové properties: `Title`, `StartUrl`, `KioskMode`, `AllowedOrigins[]`, `AllowNewTabs`, `EnableDevTools`, `Zoom`.

`AllowedOrigins` podporuje:
- přesný origin: `https://example.com`
- wildcard subdomény: `*.example.com`
- URL prefix: `https://example.com/path/*`

## Admin exit

Ctrl+Shift+Q ukončí kiosk runtime.
