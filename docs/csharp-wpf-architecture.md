# C# + WPF architektura pro KIOSK_EMISTR

## Doporučený stack

- .NET 8
- WPF pro desktop shell
- WebView2 pro embedded web obsah
- System.Text.Json pro konfiguraci
- Microsoft.Extensions.DependencyInjection pro jednoduché skládání služeb

## Cíle architektury

- maximalizovat stabilitu na Windows
- minimalizovat startovní režii a počet závislostí
- mít čistý a standardní build bez embedování konfigurace do binárky
- oddělit runtime browser od konfigurace a od případného generátoru

## Navržené vrstvy

### 1. Presentation

WPF okna, view modely a bindingy. Tady patří jen UI logika a reakce na události.

### 2. Application

Orchestrace chování browseru, práce s konfigurací a rozhodování o tom, co se má načíst při startu.

### 3. Infrastructure

Ukládání a čtení JSON konfigurace, práce se soubory, případně přístup k uživatelskému profilu.

### 4. Browser host

Izolovaná vrstva pro WebView2, navigaci, nové panely a omezené kiosk chování.

## Doporučený model konfigurace

Konfiguraci nedávat do EXE. Místo toho použít:

- `appsettings.json` pro výchozí nastavení
- per-user konfiguraci v `%AppData%\KIOSK_EMISTR\config.json`
- případně instalační `config.json` vedle EXE pro jednodušší servis

## Komponenty

### MainWindow

Hostí hlavní shell, menu a hlavní WebView2 zónu.

### BrowserTabHost

Spravuje otevřené taby, nová okna a pravidla pro zavírání.

### BrowserConfig

Nese titul, startovní URL, zoom a kiosk preference.

### ConfigStore

Čte a zapisuje JSON konfiguraci do standardního umístění.

### KioskPolicy

Obsahuje pravidla pro navigaci, blokování nechtěných oken a chování na posledním tabu.

## Proč tato varianta

- WPF je vynikající pro Windows kiosk scénáře.
- WebView2 je standardní a stabilní embed web engine.
- .NET 8 má dobrý runtime výkon, jednoduchý build a čisté balení.
- C# přinese výrazně lepší dlouhodobou údržbu než současný Python + PyInstaller model.

## Co nepřevádět doslova

- nepřenášet vlastní embedding konfigurace do binárky
- nepřenášet duplicitu generátorů `creator.py` a `factory.py`
- nepřenášet přepínače z Chromium flags bez měření
- nepřenášet křehké vazby na jména stringů v template

## Minimální cílový stav

Jeden WPF shell, jeden WebView2 host, jedna JSON konfigurace a případně samostatný build nástroj pro tvorbu branded variant aplikace.