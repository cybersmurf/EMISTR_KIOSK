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
    KioskEmistr.Generator.Wpf/  ← GUI generátor (přepis factory.py): 2 pole + tlačítko
    KioskEmistr.Generator/      ← CLI generátor (přepis creator.py)
    KioskEmistr.Core/           ← sdílená logika (GeneratorOptions, GeneratorService)

browser_engine.py               ← Python legacy, neupravuj
factory.py                      ← Python legacy, neupravuj
creator.py                      ← Python legacy, neupravuj
```

## Klíčová pravidla

- **Minimální změny.** Nepřidávej vrstvy navíc, pokud to kód nevyžaduje.
- **GUI generátor je záměrně jednoduchý**: 2 textboxy + 1 tlačítko. Nepřidávej checkboxy, FolderBrowserDialog ani progress bar.
- **KioskPolicy** v `KioskEmistr.Wpf` je zdroj pravdy pro allowlist navigace. Podporuje přesné originy, `*.example.com` a `https://example.com/path/*`.
- **Config** se načítá z `%AppData%/KIOSK_EMISTR/config.json` nebo z `appsettings.json` vedle exe. Neměň toto pořadí.
- **`KioskEmistr.Core`** je flat — žádné podsložky. Oba soubory jsou přímo v kořeni projektu.
- Build: `dotnet build KioskEmistr.sln` z `csharp-wpf/`. Release: `.\publish.ps1`.

## Co nedělat

- Nepřidávej DI kontejner, ILogger ani Microsoft.Extensions do Wpf projektu — není to potřeba.
- Nepřidávej `UseWindowsForms` do Generator.Wpf — FolderBrowserDialog tam nechceme.
- Nerozpitvávej `KioskEmistr.Core` na Models/ a Services/ podsložky — jsou tam 2 soubory.
- Nepřepisuj Python kód v kořeni repozitáře.

## Python legacy (kořen repozitáře)

Soubory `browser_engine.py`, `factory.py`, `creator.py` jsou starý kód. Slouží jako referenční implementace pro chování, které C# kód přepisuje. Neupravuj je.
- Konfiguraci je vhodné držet v normálním JSON souboru nebo ve standardním user-data umístění, ne připojovat ji na konec binárky.

Pokud by se později ukázala skutečná potřeba multiplatformy, pak je vhodnější zvažovat Qt 6 nebo Rust + Tauri než zůstávat u Python GUI stacku.
