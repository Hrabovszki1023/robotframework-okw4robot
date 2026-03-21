# OKW4Robot Execution Context – Dokumentation (sortiert nach Host / App / Window)

Diese Datei beschreibt die interne Zustandsverwaltung fuer das Framework **OKW4Robot**.
Die zentrale Instanz `context` verwaltet den Ablaufzustand fuer Host, Anwendung und Fenster.

---

## Grundsatz: „Ein Fenster ist das, was man als Fenster definiert."

Ein Fenster (Window) ist in OKW ein **logisches Konzept**, kein technischer
Typ. Jeder GUI-Bereich, den das Projekt als eigenstaendigen Kontext definiert,
ist ein Fenster — unabhaengig von der darunterliegenden Technologie:

- Java Swing: JFrame, JDialog, JPanel, ...
- HTML/Web: Browserfenster, `<div>`-Bereich, iFrame, ...
- Windows Desktop: Window, Dialog, UserControl, Panel, ...
- Mobile: Activity, Fragment, Screen, Modal, ...

Ein Fenster ist gleichzeitig ein **Widget** mit eigener `class` und eigenem
`locator`. Dadurch kann `SelectWindow` das Fenster nicht nur als Kontext setzen,
sondern auch aktiv pruefen und fokussieren.

Siehe **CONTRACT.md** (Abschnitt „Window-Modell") fuer die vollstaendige
Beschreibung.

---

## Klassenuebersicht

```python
class Context:
    def __init__(self):
        self._adapter: object | None            # Aktiver Treiber (z. B. SeleniumWebAdapter)
        self._app_name: str | None              # Name der aktiven App
        self._app_model: dict | None            # Geladene YAML-Modellstruktur der App
        self._window: str | None                # Aktueller Fensterkontext innerhalb der App
```

---

## Zustandsmatrix (nach Ebene sortiert)

### App-Ebene (empfohlen: StartApp mit __self__)

| Aktion                   | Adapter       | App           | Window      |
|--------------------------|---------------|---------------|-------------|
| `StartApp TestApp`       | auto-erzeugt¹ | TestApp       | None        |
| `StopApp`                | bleibt        | None          | None        |

¹ Falls YAML `__self__` enthaelt und kein Adapter aktiv ist.

### Host-Ebene (optional, rueckwaertskompatibel)

| Aktion                  | Adapter       | App     | Window  |
|-------------------------|---------------|---------|---------|
| `StartHost Chrome`      | gesetzt       | None    | None    |
| `SelectHost Chrome`     | bleibt        | None    | None    |
| `StopHost`              | None          | None    | None    |

### Window-Ebene (setzt App voraus)

| Aktion                        | Adapter       | App           | Window          |
|-------------------------------|---------------|---------------|-----------------|
| `SelectWindow LoginDialog`    | bleibt        | bleibt        | LoginDialog     |

`SelectWindow` loest das Fenster als Widget auf (class + locator) und kann
es ueber den Adapter aktiv selektieren/fokussieren.

---

## Kontextmethoden mit Validierung

| Methode                 | Voraussetzungen                            | Effekt                                      |
|------------------------|---------------------------------------------|---------------------------------------------|
| `set_adapter(a)`       | —                                           | Adapter gesetzt, App + Window geloescht     |
| `stop_adapter()`       | —                                           | Alle 3 Zustaende geloescht                 |
| `get_adapter()`        | Adapter muss gesetzt sein                   | Liefert aktuelle Adapterinstanz            |
| `set_app(name, model)` | —                                           | App geladen, Fensterkontext geloescht. Falls `__self__` und kein Adapter → Adapter auto-erzeugt. |
| `stop_app()`           | App muss aktiv sein                         | App + Window geloescht                      |
| `set_window(name)`     | App + Adapter muessen gesetzt sein          | Setzt Fensterkontext, loest Fenster als Widget auf |
| `get_current_window_model()` | Alle drei Zustaende muessen aktiv sein | Liefert Modell des aktiven Fensters         |
| `describe()`           | —                                           | Gibt aktuellen Kontextzustand zurueck      |

---

## Beispiel (empfohlen: StartApp uebernimmt alles)

```python
# StartApp laedt YAML, erkennt __self__, erzeugt Adapter automatisch
context.set_app("DemoApp", app_yaml)        # Adapter auto-start via __self__
context.set_window("MainFrame")             # Loest MainFrame als Widget auf

model = context.get_current_window_model()  # Liefert {class, locator, txtName, btnOk, ...}
```

## Beispiel (alt: separater Host-Start)

```python
context.set_adapter(SeleniumWebAdapter())
context.set_app("MeineApp", app_yaml)
context.set_window("LoginDialog")

model = context.get_current_window_model()
```

---

## Fenster-Widget-Aufloesung

Wenn `set_window("MainFrame")` aufgerufen wird, enthaelt das Window-Modell
sowohl die eigene Widget-Definition (`class`, `locator`) als auch die
Kind-Widgets:

```yaml
MainFrame:
  class: remotesw_frame.RemoteSw_Frame       # ← Fenster-Widget
  locator: { name: "MainFrame" }             # ← Fenster-Locator

  txtName:                                    # ← Kind-Widget
    class: remotesw_textfield.RemoteSw_TextField
    locator: { name: "txtName" }
```

Reservierte Keys (`class`, `locator`, `__self__`) werden von Kind-Widgets
unterschieden. Alles andere auf derselben Ebene ist ein Kind-Widget.

---

## Fehlerverhalten

Jede Methode prueft den gueltigen Zustand und liefert bei Fehlverwendung eine **klare und sprechende Fehlermeldung**, z. B.:

- `"No adapter/host active – cannot start app."`
- `"No app active – cannot select window."`
- `"Window 'Foo' not found in app model."`
