# Migrační plán: Python kiosk -> C# + WPF

## 1. Cíl migrace

Cílem je nahradit současné Python řešení stabilní desktop aplikací na .NET 8 + WPF + WebView2.

Hlavní priority:

- stabilita
- výkon
- jednodušší distribuce
- standardní konfigurace mimo binárku
- možnost později rozšířit na lepší servisní a update model

## 2. Fázový postup

### Fáze A: Funkční parita

Přepsat pouze to, co je nutné pro ekvivalentní chování.

- otevření startovní URL
- nový tab nebo nové okno
- titul okna
- základní context menu
- zavírání panelů
- nastavení zoomu
- čtení konfigurace z JSON

### Fáze B: Stabilizační vrstva

Po dosažení parity doplnit:

- robustní error handling
- logging
- recovery po pádu WebView2 instance
- validaci konfigurace
- bezpečné ukládání user dat

### Fáze C: Produktizace

- installer nebo MSIX
- branding assets
- update workflow
- případně policy management pro kiosk režim

## 3. Mapování současných souborů

- `browser_engine.py` -> WPF runtime shell
- `browser_template.py` -> už nebude potřeba v dnešní podobě
- `factory.py` -> buď se přepíše na C# generátor, nebo se nahradí jednoduchým setup nástrojem
- `creator.py` -> kandidát na odstranění nebo archivaci
- `browser_engine.spec` a `KioskGenerator.spec` -> nahradit standardním .NET buildem

## 4. Doporučená pořadí práce

1. vytvořit nový WPF runtime shell
2. přidat JSON configuration model
3. přidat WebView2 host s tab managementem
4. přenést branding a icony
5. připravit build a distribuci
6. až potom řešit případný generátor kiosk variant

## 5. Rizika migrace

- přepis WebView2 hostu může odhalit rozdíly v chování oproti Qt WebEngine
- kiosk režim na Windows může vyžadovat konkrétní policy nastavení
- je potřeba hlídat, aby se nepřenesla stejná křehkost konfigurace jako v Pythonu
- pokud se zachová příliš mnoho původní logiky, ztratí se výhody migrace

## 6. Rozhodovací pravidlo

Když je změna malá a čistě Windows, C# + WPF je správná cílová cesta.
Když by se znovu objevil požadavek na multiplatformu, je lepší přehodnotit architekturu už v této fázi a nebuildit další Windows-only vrstvy nad Pythonem.