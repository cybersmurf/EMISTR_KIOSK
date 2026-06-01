# KIOSK_EMISTR - analyza projektu a mapa Copilot customizace

## Strucne shrnuti

Repozitar je maly desktopovy produkt pro generovani kiosk aplikaci nad webem. Jadrem je PyQt6 web browser s taby a minimalistickym UI, kolem ktereho je PyInstaller build pipeline. Druhy vstupni bod je graficky generator v CustomTkinter, ktery vezme sablonu, prida konfiguraci na konec EXE souboru a vytvori samostatnou kiosk aplikaci.

## Co projekt dela

- `browser_engine.py` je runtime browser. Nacte konfiguraci, otevre hlavni URL a resi nove tably, titulky, ikony a zakladni context menu.
- `browser_template.py` je template verze browseru. Obsahuje placeholder URL a je urcena pro generovani konkretni aplikace.
- `creator.py` je CLI generator. Cte template, nahradi URL a spusti PyInstaller pro vygenerovani EXE.
- `factory.py` je graficky generator. Vytvari novy kiosk EXE tak, ze pripoji JSON konfiguraci za separator k existujicimu `browser_engine.exe`.
- `browser_engine.spec` a `KioskGenerator.spec` popisuji PyInstaller baleni obou binarek.

## Technicka architektura

### Runtime browser

Browser pouziva PyQt6 `QWebEngineView` a `QTabWidget`. Chovani je postavene takto:

- nova okna z JS nebo target=_blank se prepinaji na novy tab
- tab bar je skryty, pokud je otevren jen jeden panel
- zavirani posledniho tabu je blokovane
- povolene jsou vykonove volby WebEngine jako WebGL, accelerated canvas a DNS prefetch
- startovni konfigurace se nacita z konce EXE souboru pomoci separatoru `<<<KIOSK_CONFIG>>>`

### Generator EXE

`factory.py` slouzi jako produktovy generator. Vstupem je nazev aplikace a cilova URL. Vystupem je novy EXE soubor, ktery obsahuje:

- binarni template `browser_engine.exe`
- icony `favicon.ico`, `agerit_logo.png`, `emistr_logo.png`
- JSON konfiguraci s `title`, `url` a `zoom`

## Soucasne soubory a role

| Soubor | Role | Poznamka |
|---|---|---|
| `browser_engine.py` | hlavni kiosk browser | cte config ze sebe sameho |
| `browser_template.py` | template browser | placeholder URL a title |
| `creator.py` | CLI builder | generuje app z template |
| `factory.py` | GUI builder | sklada EXE s configem |
| `browser_engine.spec` | PyInstaller spec | build browseru |
| `KioskGenerator.spec` | PyInstaller spec | build generatoru |
| `favicon.ico` | ikona | pouzita v obou binarkach |
| `agerit_logo.png` | logo | v GUI generatoru |
| `emistr_logo.png` | logo | v GUI generatoru |

## Pozorovane zavislosti a rizika

- `factory.py` predpoklada existenci `browser_engine.exe` v `dist/` nebo v aktualnim adresari. To je pevny build contract.
- `creator.py` dela string replacement nad presnym literalem `title='Kiosk Browser'`. Kdyz se text v template zmeni, generator prestane spravne prepisovat title.
- Embedded config je ulozena jako surovy JSON za separator na konci EXE. To je jednoduche, ale krehke pri ruce upravenych binarkach nebo pri antivirovych/packaging zasazich.
- V repu nejsou zadne testy, docs ani definovane Copilot customization soubory, takze znalost procesu je zatim roztrousena jen v kodu.

## Mapa Copilot customizace

V repozitari by mel byt primarni customizacni soubor [AGENTS.md](../AGENTS.md), ktery nese zakladni pravidla. Ostatni customizace maji byt jen doplnkove. Pro tento projekt dava smysl je rozdelit takto:

### 1. Agent instructions

Ucely: pravidla, ktera maji platit stale pro cely projekt.

Navrhovany obsah:

- preferovat `apply_patch` pro zmeny souboru
- nemenit build contract mezi `factory.py`, `browser_engine.exe` a `dist/`
- pri praci s PyInstaller aktualizovat i odpovidajici `.spec` soubor
- nerozbijet string-based replacement bez navazne upravy generatoru
- drzet se ASCII v novych technickych souborech, pokud neni duvod jinak

Navrhovana umisteni:

- `copilot-instructions.md` nebo `AGENTS.md` v rootu repozitare

### 2. File instructions

Ucely: pravidla vazana na konkretni typy souboru nebo slozky.

Navrhy:

- `*.py` pro obecne Python style a build pravidla
- `browser_engine.py` pro pravidla kolem WebEngine a runtime konfigurace
- `factory.py` pro pravidla kolem bundlovani, assetu a separatoru konfigurace
- `*.spec` pro PyInstaller pravidla

Navrhovana umisteni:

- `.github/instructions/python-build.instructions.md`
- `.github/instructions/browser-runtime.instructions.md`
- `.github/instructions/pyinstaller.instructions.md`

### 3. Custom agents

Ucely: specializovane role pro opakovane ulohy.

Navrhy agentu:

- `kiosk-packager.agent.md` pro build, PyInstaller, asset bundling a kontrolu `spec` souboru
- `browser-runtime.agent.md` pro logiku tabu, WebEngine a konfiguraci browseru
- `ui-generator.agent.md` pro CustomTkinter GUI generator a jeho vizualni konzistenci

Navrhovana umisteni:

- `.github/agents/kiosk-packager.agent.md`
- `.github/agents/browser-runtime.agent.md`
- `.github/agents/ui-generator.agent.md`

### 4. Skills

Ucely: on-demand workflow balicky pro konkretni technicke postupy.

Navrhy skillu:

- `kiosk-packaging` pro PyInstaller build, assety a kontrolu vystupu
- `browser-runtime-debug` pro ladeni WebEngine tab chovani a nacitani URL
- `config-embedding` pro praci se separator-based JSON konfiguraci
- `ui-theme-and-branding` pro sjednoceni vzhledu generatoru

Navrhovana umisteni:

- `.github/skills/kiosk-packaging/SKILL.md`
- `.github/skills/browser-runtime-debug/SKILL.md`
- `.github/skills/config-embedding/SKILL.md`

## Doporučeny dalsi krok

Pokud je cil nejen dokumentace, ale i realna Copilot customizace, dalsi rozumny krok je vytvorit tyto soubory postupne:

1. `copilot-instructions.md` s globalnimi pravidly repozitare
2. jeden file instruction pro `factory.py` a `browser_engine.py`
3. jeden specializovany agent pro build a packaging
4. jeden skill pro opakovatelny postup generovani kiosk binarek

Tato struktura by pokryla soucasny stav projektu bez zbytecneho pretezovani repozitare.