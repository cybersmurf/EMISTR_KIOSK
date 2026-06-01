# Analýza projektu KIOSK_EMISTR

## Stručné shrnutí

Projekt je malý generátor kioskových aplikací pro Windows založený na Pythonu. Má dvě hlavní vrstvy:

1. `browser_engine.py` a `browser_template.py` tvoří samotný kioskový prohlížeč postavený na `PyQt6` a `QtWebEngine`.
2. `factory.py` slouží jako grafický generátor výsledné aplikace přes `customtkinter` a zapisuje konfigurační data na konec hotového EXE.

Výstupem je samostatná aplikace typu `onefile`, sestavená přes `PyInstaller`.

## Co projekt dělá

Uživatel zadá název aplikace a cílovou URL. Generator vytvoří nový spustitelný soubor, který:

- otevře zadanou webovou stránku v celoobrazovkovém režimu,
- používá vlastní ikonu a branding,
- podporuje více panelů,
- zjednodušuje kontextové menu jen na obnovení stránky,
- v template režimu umí číst konfiguraci přímo z připojeného JSON payloadu na konci binárky.

## Architektura

### `browser_template.py`

Šablona kiosk browseru.

- Má placeholder URL `"%URL%"`.
- Při spuštění kontroluje, jestli byl soubor vygenerován přes creator.
- Konfiguruje `QTWEBENGINE_CHROMIUM_FLAGS` pro výkon.
- Zobrazuje hlavní okno s taby a podporou otevírání nových oken přes `createWindow`.

### `browser_engine.py`

Generovaná nebo distribuovaná verze browseru.

- Načítá konfiguraci z vlastního EXE za oddělovačem `<<<KIOSK_CONFIG>>>`.
- Používá nastavení pro výkon Chromium enginu.
- Přidává vlastní ikonku z `favicon.ico`.
- Má jednoduché pravidlo pro zavírání tabů: poslední tab se nezavírá.

### `factory.py`

GUI generátor aplikace.

- Používá `customtkinter` pro moderní formulář.
- Získává vstupy: název aplikace a cílovou URL.
- Najde template EXE buď v aktuálním adresáři, nebo v `dist/`.
- Vytvoří nový soubor a přidá za něj JSON konfiguraci.

### `creator.py`

Starší nebo alternativní generátor na bázi textové šablony.

- Čte `browser_template.py`.
- Nahrazuje placeholder URL.
- Pokouší se přepsat titulek okna podle názvu aplikace.
- Spouští `PyInstaller` nad dočasným skriptem.

## Build a balení

### PyInstaller specifikace

- `browser_engine.spec` sestavuje samostatný kioskový browser z `browser_engine.py`.
- `KioskGenerator.spec` sestavuje GUI generátor z `factory.py`.
- Oba spec soubory přidávají ikonu `favicon.ico`.
- `KioskGenerator.spec` navíc přidává `agerit_logo.png`, `emistr_logo.png` a `dist/browser_engine.exe` jako datové soubory.

### Použitý model distribuce

Distribuce je postavená na dvou binárkách:

- `browser_engine.exe` jako runtime kiosk browser.
- `KioskGenerator.exe` jako nástroj pro vytvoření konkrétní kioskové aplikace.

## Důležité technické detaily

- Projekt cílí na Windows, protože pracuje s `.exe` a `PyInstaller` výstupem.
- Konfigurace se neukládá do odděleného souboru, ale přímo do binárky za značku `<<<KIOSK_CONFIG>>>`.
- Template browser očekává, že vygenerovaný soubor už nebude obsahovat placeholder `"%URL%"`.
- Browser používá `PyQt6.WebEngine`, takže je potřeba přítomnost odpovídajících Qt WebEngine balíčků.

## Rizika a slabá místa

1. `creator.py` a `browser_template.py` používají jiný model předání URL než `browser_engine.py`. Jeden zapisuje do textové šablony, druhý čte JSON z binárky. To je funkční, ale dvojí mechanismus je náchylný na drift.
2. `browser_engine.py` závisí na tom, že data za separátorem budou validní UTF-8 JSON. Jakákoli změna balení může načítání konfigurace rozbít.
3. `factory.py` očekává, že `dist/browser_engine.exe` existuje. Build postup tedy není zcela samostatný a vyžaduje předchozí vytvoření runtime EXE.
4. Projekt neobsahuje centrální dokumentaci pro build, testování ani strukturu customizací Copilotu.

## Doporučená dokumentace

Pro tento repozitář dává smysl přidat tyto soubory:

- `README.md` s rychlým startem a build postupem.
- `docs/architecture.md` s vysvětlením vztahu mezi `browser_engine.py`, `browser_template.py`, `factory.py` a `creator.py`.
- `docs/build.md` s přesnými kroky pro PyInstaller build.
- `.github/copilot-instructions.md` s projektovými pravidly pro budoucí úpravy.

## Návrh Copilot customizací

### Agenty

V tomto projektu dává smysl mít specializované agenty jen tam, kde je potřeba úzký kontext.

- `kiosk-builder.agent.md`: agent pro úpravy browser runtime, PyQt6 a PyInstaller balení.
- `ui-polish.agent.md`: agent pro zásahy do `customtkinter` UI v `factory.py`.
- `packaging.agent.md`: agent pro spec soubory, icon assets a release build postup.

### Instrukce

Instrukce by měly být obecné a vždy dostupné.

- Preferovat minimální změny a zachovat stávající Windows-centric packaging.
- Při úpravách browser runtime nepřidávat zbytečnou složitost do tab managementu.
- Při práci s buildem vždy ověřit, zda změna nepoškodí PyInstaller spec soubory.

### Skilly

Skilly mají smysl pro opakovaně používané workflow.

- `pyinstaller-build`: vytvoření a validace obou EXE.
- `browser-runtime-debug`: diagnostika `PyQt6` / `QtWebEngine` chování.
- `branding-assets`: kontrola ikon, log a jejich vazby na packaging.

## Praktický závěr

Repozitář je malý, ale má jasně oddělenou odpovědnost mezi runtime browserem a generátorem. Největší přínos má jedna sjednocující dokumentace a primární agentový soubor [AGENTS.md](AGENTS.md), který drží konzistenci mezi šablonou, generátorem a PyInstaller balením.