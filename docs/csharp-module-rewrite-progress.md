# C# modulovy prepis - stav

## Co je uz prepsane

### Runtime browser cast (nahrada `browser_engine.py`)

- kiosk window policy
- allowlist navigacni policy s wildcard subdoménami a URL prefix patterny
- tab host oddeleny od hlavniho okna
- fallback/recovery pri WebView2 process failure
- zakladni diagnostika do `%AppData%/KIOSK_EMISTR/logs/kiosk.log`

### Sdilena Core knihovna (`KioskEmistr.Core`)

- `GeneratorOptions` model
- `GeneratorService` — kopírování runtime, zápis appsettings.json

### Generator cast (nahrada `creator.py` a `factory.py`)

- `KioskEmistr.Generator` — CLI generátor s argumenty
- `KioskEmistr.Generator.Wpf` — WPF GUI generátor (přepis vizuální části factory.py)
  - tmavý UI styl s EMISTR brandingem
  - formulář: název, URL, runtime složka, výstupní složka, volby
  - FolderBrowserDialog pro výběr složek
  - async generování s progress indikátorem

### Build a release

- `publish.ps1` — PowerShell skript pro self-contained win-x64 publish
  - publikuje runtime, GUI generator, CLI generator
  - generuje README.txt s instrukcemi

## Neni potreba resit

1. MSIX/installer — self-contained EXE výstup z publish.ps1 je dostatecný
2. Dalsi kiosk security — KioskPolicy pokryva vsechny potrebne scenare

## Prakticke pouziti

### GUI generator
```
KioskEmistr.Generator.Wpf.exe
```
- Vyplnit formulár, kliknout VYGENEROVAT

### CLI generator
```
KioskEmistr.Generator.exe \
  --app-name SkladKiosk \
  --url https://example.com \
  --runtime-dir C:\runtime\KioskEmistr.Wpf \
  --output-dir C:\kiosk-output
```

### Publish (Windows PowerShell)
```
.\publish.ps1
```
Vytvoří `release\` se vsemi EXE.

### KioskPolicy — vzorové AllowedOrigins
```json
"AllowedOrigins": [
  "https://example.com",
  "*.example.com",
  "https://cdn.example.com/assets/*"
]
```