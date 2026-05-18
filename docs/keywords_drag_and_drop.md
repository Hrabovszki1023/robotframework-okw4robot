# Drag & Drop Keywords

Diese Seite dokumentiert die Drag-&-Drop-Keywords und das
Collect-then-Execute-Pattern.

---

## Uebersicht

| Keyword | Parameter | Beschreibung |
|---|---|---|
| `DragTo` | `<Source>` `<Target>` | Shortcut: zieht Source direkt auf Target |
| `DragStart` | `<Name>` | Merkt Source-Element (vorbereitend) |
| `DragOver` | `<Name>` | Merkt Zwischenziel (wiederholbar, vorbereitend) |
| `Drop` | `<Name>` | Fuehrt gesamte Drag-Sequenz atomar aus |

---

## Collect → Execute Pattern

`DragStart` und `DragOver` fuehren **keine Aktion** aus. Sie sammeln
nur Element-Referenzen im Adapter. Erst `Drop` fuehrt die gesamte
Sequenz in einem Schritt aus:

1. `DragStart` → speichert Source-Element
2. `DragOver` → haengt Zwischenziel an Liste (wiederholbar)
3. `Drop` → feuert `dragstart` → `[dragenter+dragover+dragleave]*`
   → `dragenter+dragover+drop` → `dragend`

Dieses Pattern stellt sicher, dass die Event-Kette atomar und
konsistent ablaeuft — auch bei komplexen Drag-Pfaden.

---

## DragTo (Shortcut)

```
DragTo    <Source>    <Target>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Source` | ja | Logischer Name des Quell-Widgets (YAML-Key) |
| `Target` | ja | Logischer Name des Ziel-Widgets (YAML-Key) |

Der einfache Fall: Quell-Element direkt auf Ziel-Element ziehen,
ohne Zwischenstopps. Intern wird die gesamte Event-Kette in einem
Schritt ausgefuehrt.

```robot
SelectWindow   DragDropPage
DragTo         SpalteA    SpalteB
VerifyValue    SpalteA    B
VerifyValue    SpalteB    A
```

**Besonderheit:** `DragTo` nimmt **zwei** Widget-Namen entgegen.
Beide werden im aktuellen Fensterkontext aufgeloest.

---

## DragStart

```
DragStart    <Name>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Name` | ja | Logischer Name des Quell-Widgets (YAML-Key) |

Markiert ein Widget als Drag-Quelle. Es werden nur Vorbedingungen
geprueft (Element existiert) und die Element-Referenz gespeichert.
Keine Drag-Events werden gefeuert.

```robot
DragStart    SourceNode
```

---

## DragOver

```
DragOver    <Name>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Name` | ja | Logischer Name des Zwischenziel-Widgets (YAML-Key) |

Fuegt ein Zwischenziel zur Drag-Sequenz hinzu. Kann **mehrfach
hintereinander** aufgerufen werden, z.B. um in einem TreeView
Knoten aufzuklappen oder um ueber mehrere Elemente hinweg zu
navigieren.

Setzt `DragStart` voraus. Ohne vorherigen `DragStart` wirft der
Adapter einen `RuntimeError`.

```robot
DragStart    SourceNode
DragOver     FolderNode1     # erstes Zwischenziel
DragOver     FolderNode2     # zweites Zwischenziel
Drop         TargetNode
```

---

## Drop

```
Drop    <Name>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Name` | ja | Logischer Name des Ziel-Widgets (YAML-Key) |

Fuehrt die gesamte Drag-Sequenz aus und laesst das gegriffene
Element auf dem Ziel los. Die Event-Reihenfolge:

1. `dragstart` auf Source
2. Fuer jedes Zwischenziel: `dragenter` → `dragover` → `dragleave`
3. Auf Target: `dragenter` → `dragover` → `drop`
4. `dragend` auf Source

Nach der Ausfuehrung wird der Drag-Zustand im Adapter zurueckgesetzt.
Setzt `DragStart` voraus.

**Screenshots:** Vorher/Nachher werden automatisch im Robot Log geloggt.

---

## Beispiele

### Spalten tauschen (Column Swap)

```robot
*** Test Cases ***
Spalte A Nach B Ziehen
    VerifyValue    SpalteA    A
    VerifyValue    SpalteB    B
    DragTo         SpalteA    SpalteB
    VerifyValue    SpalteA    B
    VerifyValue    SpalteB    A

Doppelter Tausch
    DragTo         SpalteA    SpalteB
    DragTo         SpalteA    SpalteB
    VerifyValue    SpalteA    A
    VerifyValue    SpalteB    B
```

### Kreise in Zielbereich verschieben (DOM Move)

```robot
*** Test Cases ***
Alle Kreise In Zielbereich Ziehen
    DragTo         RoterKreis      Zielbereich
    DragTo         GruenerKreis    Zielbereich
    DragTo         BlauerKreis     Zielbereich
    VerifyExist    RoterKreis      NO
    VerifyExist    GruenerKreis    NO
    VerifyExist    BlauerKreis     NO
```

### TreeView mit Zwischenstopps

```robot
*** Test Cases ***
Datei In Unterordner Verschieben
    DragStart      Dokument
    DragOver       OrdnerProjekte       # klappt auf
    DragOver       OrdnerArchiv         # klappt auf
    Drop           Unterordner2026
```

---

## YAML-Locator

Drag-&-Drop-Elemente benoetigen **keine spezielle Widget-Klasse**.
Standard-Labels reichen — die Drag-Logik steckt im Keyword/Adapter,
nicht im Widget:

```yaml
SpalteA:
  class: okw_web_selenium.widgets.webse_label.WebSe_Label
  locator: { id: column-a }

SpalteB:
  class: okw_web_selenium.widgets.webse_label.WebSe_Label
  locator: { id: column-b }
```

Auch CSS-Klassen-basierte Locatoren (ohne IDs) funktionieren:

```yaml
RoterKreis:
  class: okw_web_selenium.widgets.webse_label.WebSe_Label
  locator: { css: '#source .red' }
```

---

## Technische Details

### HTML5 Drag Event Simulation

Selenium ActionChains loesen **keine** HTML5 Drag Events aus.
Der Selenium-Adapter verwendet daher JavaScript-basierte
Event-Simulation mit synthetischen `DragEvent`- und
`DataTransfer`-Objekten.

Die gesamte Event-Kette wird in **einem** `execute_script()`-Aufruf
gefeuert — atomar und ohne Timing-Probleme.

### Pre-Conditions

| Keyword | Intent | Pruefungen |
|---|---|---|
| `DragStart` | read | exists |
| `DragOver` | read | exists |
| `Drop` | read | exists |
| `DragTo` | — | exists fuer Source und Target |

### Adapter-Zustand

Der Adapter haelt zwei Instanzvariablen waehrend einer Drag-Sequenz:

- `_drag_source` — WebElement der Quelle
- `_drag_intermediates` — Liste der Zwischenziel-WebElements

Beide werden bei `Drop` zurueckgesetzt. Ein erneuter `DragStart`
ohne vorheriges `Drop` ueberschreibt den alten Zustand.

---

## Code-Referenzen

- Keywords: `src/okw4robot/keywords/widget_keywords.py` → `DragTo`, `DragStart`, `DragOver`, `Drop`
- Widget-Interface: `src/okw4robot/widgets/okw_widget.py` → `okw_drag_start()`, `okw_drag_over()`, `okw_drop()`
- Selenium Widget: `src/okw_web_selenium/widgets/webse_base.py` → Drag-Implementierung
- Selenium Adapter: `src/okw_web_selenium/adapters/selenium_web.py` → `_exec_drag()`, JS Event-Simulation
