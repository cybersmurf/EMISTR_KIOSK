# AGENTS.md pro KIOSK_EMISTR

## Stav projektu

**Aktivní větev: `csharp-wpf/`** — C# + WPF + WebView2 přepis. Python kód v kořeni repozitáře je legacy.

## Struktura repozitáře

```
csharp-wpf/                     ← aktivní C# solution
  KioskEmistr.sln
  publish.ps1                   ← release build pro Windows
  src/
    KioskEmistr.Wpf/            ← kiosk browser runtime (přepis browser_engine.py)
      Models/
        BrowserConfig.cs        ← konfigurace runtime (Title, StartUrl, Zoom, KioskMode,
                                   AllowedOrigins, BarcodeScanner?, RfidReader?)
        BrowserTab.cs           ← INotifyPropertyChanged tab model
        Rs232DeviceConfig.cs    ← Port + BaudRate pro jednu čtečku (namespace Wpf.Models)
      Services/
        BrowserService.cs
        BrowserTabHost.cs       ← sdílené CoreWebView2Environment (Lazy<Task<>>), správa tabů
        ConfigStore.cs          ← načítá config.json z AppData nebo appsettings.json vedle exe
        DiagnosticsService.cs   ← logování do %AppData%/KIOSK_EMISTR/logs/kiosk.log
        KioskPolicy.cs          ← allowlist navigace (origin, *.wildcard, prefix)
        KioskShutdownService.cs
        KioskWindowService.cs
        Rs232Service.cs         ← otevírá SerialPort 8N1, line-buffer, event → ExecuteScriptAsync
    KioskEmistr.Generator.Wpf/  ← GUI generátor (přepis factory.py)
                                   6 polí: AppName, URL + 4× RS232 (port+baud pro každou čtečku)
    KioskEmistr.Generator/      ← CLI generátor (přepis creator.py)
    KioskEmistr.Core/           ← sdílená logika (flat — žádné podsložky)
      GeneratorOptions.cs       ← vstupní parametry generátoru vč. BarcodeScanner?, RfidReader?
      GeneratorService.cs       ← kopíruje runtime, zapisuje appsettings.json s RS232 sekcí
      Rs232DeviceConfig.cs      ← Port + BaudRate (namespace KioskEmistr.Core)

browser_engine.py               ← Python legacy (aktivně udržovaný souběžně)
factory.py                      ← Python legacy (aktivně udržovaný souběžně)
creator.py                      ← Python legacy, neupravuj
```

## Klíčová pravidla

- **Minimální změny.** Nepřidávej vrstvy navíc, pokud to kód nevyžaduje.
- **GUI generátor má 6 polí**: AppName, URL + 4 volitelná pole RS232. Nepřidávej checkboxy, FolderBrowserDialog ani progress bar.
- **KioskPolicy** v `KioskEmistr.Wpf` je zdroj pravdy pro allowlist navigace. Podporuje přesné originy, `*.example.com` a `https://example.com/path/*`.
- **Config** se načítá z `%AppData%/KIOSK_EMISTR/config.json` nebo z `appsettings.json` vedle exe. Neměň toto pořadí.
- **`KioskEmistr.Core`** je flat — žádné podsložky. Soubory jsou přímo v kořeni projektu.
- **`Rs232DeviceConfig`** existuje ve dvou namespace (`KioskEmistr.Core` a `KioskEmistr.Wpf.Models`) záměrně — projekty na sebe nemají referenci.
- **RS232 pole jsou volitelná** — prázdný `Port` (nebo chybějící sekce v JSON) = zařízení zakázáno.
- **JS rozhraní pro web**: `window.addEventListener('kioskInput', e => { e.detail.value; e.detail.source; })` — source je `'barcode'` nebo `'rfid'`.
- Build: `dotnet build KioskEmistr.sln` z `csharp-wpf/`. Release: `.\publish.ps1`.

## Co nedělat

- Nepřidávej DI kontejner, ILogger ani Microsoft.Extensions do Wpf projektu — není to potřeba.
- Nepřidávej `UseWindowsForms` do Generator.Wpf — FolderBrowserDialog tam nechceme.
- Nerozpitvávej `KioskEmistr.Core` na Models/ a Services/ podsložky — jsou tam 4 soubory.
- Nepřidávej třetí RS232 port — kiosk podporuje nejvýše 2 zařízení (barcode + RFID).
- Nevolej Qt/WebView metody z RS232 background threadu (Python) — vždy přes `queue.Queue` + `QTimer`.

## RS232 architektura

### C# (`Rs232Service`)
- `SerialPort` se otevírá v konstruktoru; `DataReceived` event přijímá data z OS threadu.
- Znaky se bufferují do `StringBuilder`; `\r` nebo `\n` ukončuje řádek a spustí callback.
- Callback zavolá `Dispatcher.InvokeAsync` → `ExecuteScriptAsync` s CustomEvent `kioskInput`.
- `Rs232Service.Dispose()` se volá v `MainWindow.Closing` (pouze pokud se okno skutečně zavírá).

### Python (`Rs232Reader` + `QTimer`)
- `Rs232Reader` je daemon thread — nevolá Qt přímo, pouze vkládá do `queue.Queue`.
- `QTimer` (50 ms interval) v hlavním vláknu vybírá frontu a volá `inject_scan_data`.
- `inject_scan_data` zavolá `page().runJavaScript()` s CustomEvent na aktuálním tabu.
- `closeEvent` v `CustomBrowser` stopuje všechny readery a timer.

## Python legacy (kořen repozitáře)

`browser_engine.py` a `factory.py` jsou aktivně udržovány souběžně s C# verzí — obsahují RS232 podporu.  
`creator.py` je pouze referenční — neupravuj.

- Konfiguraci je vhodné držet v normálním JSON souboru nebo ve standardním user-data umístění, ne připojovat ji na konec binárky.

Pokud by se později ukázala skutečná potřeba multiplatformy, pak je vhodnější zvažovat Qt 6 nebo Rust + Tauri než zůstávat u Python GUI stacku.
