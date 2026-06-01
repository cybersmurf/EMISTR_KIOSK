# Analýza výkonu Python řešení a doporučení migrace

## Závěr předem

Současné řešení v Pythonu lze vylepšit, ale většina výkonových zisků bude jen inkrementální. Pokud je cílem co nejvyšší výkon, maximální stabilita a zároveň možnost multiplatformy, je dlouhodobě lepší nový stack než hlubší optimalizace současného Python GUI.

## Co je dnes na Python řešení problematické

Projekt je postavený na kombinaci `PyQt6`, `QtWebEngine`, `customtkinter`, `PyInstaller` a vlastního embedování konfigurace do EXE. To znamená:

- vyšší paměťovou režii při startu i běhu,
- citlivější build a packaging flow,
- složitější reprodukovatelnost výsledné binárky,
- dva odlišné generátory pro podobný cíl,
- část konfigurace je uložena křehkým způsobem přímo na konec binárky.

## Co má smysl optimalizovat v Pythonu

### 1. Zjednodušit runtime cestu

Místo dvou mechanismů pro generování aplikace držet jeden.

- Zrušit duplicitu mezi `creator.py` a `factory.py`.
- Zachovat jen jeden build flow.
- Oddělit runtime browser od generátoru binárky.

### 2. Přestat embedovat konfiguraci do EXE

Největší křehkost není samotný Python, ale způsob balení konfigurace.

- Místo `SEPARATOR + JSON` použít vedlejší `config.json`.
- Případně ukládat do `%AppData%` nebo jiného standardního user data umístění.
- Tím se zjednoduší update i diagnostika.

### 3. Omezit zbytečné závislosti v UI vrstvě

`customtkinter` je pro generátor použitelný, ale není důvod ho držet jako kritickou součást runtime aplikace.

- Generátor může být oddělený nástroj.
- Runtime kiosk browser by měl mít co nejméně UI logiky navíc.

### 4. Zpřesnit Qt WebEngine nastavení

U browseru dává smysl vyhodit vše, co nepřináší měřitelný přínos.

- Nechat jen ověřené `QTWEBENGINE_CHROMIUM_FLAGS`.
- Minimalizovat experimentální přepínače.
- Omezit nadbytečné tab/window chování, pokud není nutné.

### 5. Redukovat startovní práci

Při startu aplikace dělat co nejméně práce mimo vytvoření hlavního okna.

- Nepřidávat zbytečné synchronní I/O.
- Nenahrávat assety nebo konfigurační data víckrát.
- Zkrátit úvodní inicializaci na minimum.

## Co už Python pravděpodobně nevyřeší dost dobře

I po optimalizacích zůstane několik limitů:

- PyInstaller packaging bude stále citlivější než nativní build.
- WebEngine runtime bude pořád těžký, protože skutečný frontend engine je Chromium.
- Multiplatforma v Python desktop stacku bude prakticky slabší než u cíleného nativního stacku.
- Dlouhodobá údržba více generátorů a embedovaných binárních dat bude složitější než standardní desktop architektura.

## Doporučení

Pokud má být cílem nový produkt, doporučení je:

1. Pro Windows-first řešení zvolit C# + WPF + WebView2.
2. Pokud má být skutečně multiplatforma, zvažovat Qt 6 nebo Rust + Tauri.
3. Současný Python použít nanejvýš jako referenční prototyp, ne jako finální cílovou platformu.

## Praktický přepis priorit

Nejlepší investice času v tuto chvíli je spíš do migrace než do dalšího ladění Pythonu. Optimalizace Pythonu může zlepšit komfort, ale nezmění základní vlastnosti stacku.

Naopak C# + WPF dá pro Windows kioskový scénář velmi dobrý poměr mezi:

- stabilitou,
- výkonem,
- jednoduchostí distribuce,
- údržbou,
- a nízkým rizikem při přepisu.