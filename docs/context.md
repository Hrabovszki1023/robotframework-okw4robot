# OKW4Robot Execution Context – Dokumentation (sortiert nach Host / App / Window)

Diese Datei beschreibt die interne Zustandsverwaltung fuer das Framework **OKW4Robot**.
Die zentrale Instanz `context` verwaltet den Ablaufzustand fuer Host, Anwendung und Fenster.

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

### Host-Ebene

| Aktion                  | Adapter       | App     | Window  |
|-------------------------|---------------|---------|---------|
| `Start Host Chrome`     | gesetzt       | None    | None    |
| `Select Host Chrome`    | bleibt        | None    | None    |
| `Stop Host`             | None          | None    | None    |

---

### App-Ebene (setzt Host voraus)

| Aktion                   | Adapter       | App           | Window      |
|--------------------------|---------------|---------------|-------------|
| `Start App TestApp`      | bleibt        | TestApp       | None        |
| `Select App TestApp`     | bleibt        | TestApp       | None        |
| `Stop App TestApp`       | bleibt        | None          | None        |

---

### Window-Ebene (setzt App & Host voraus)

| Aktion                        | Adapter       | App           | Window          |
|-------------------------------|---------------|---------------|-----------------|
| `Select Window LoginDialog`   | bleibt        | bleibt        | LoginDialog     |

---

## Kontextmethoden mit Validierung

| Methode                 | Voraussetzungen                            | Effekt                                      |
|------------------------|---------------------------------------------|---------------------------------------------|
| `set_adapter(a)`       | —                                           | Adapter gesetzt, App + Window geloescht     |
| `stop_adapter()`       | —                                           | Alle 3 Zustaende geloescht                 |
| `get_adapter()`        | Adapter muss gesetzt sein                   | Liefert aktuelle Adapterinstanz            |
| `set_app(name, model)` | Adapter muss gesetzt sein                   | App geladen, Fensterkontext geloescht      |
| `select_app(name)`     | App muss aktiv sein                         | Bestaetigt und (re)setzt Fensterkontext    |
| `stop_app()`           | App muss aktiv sein                         | App + Window geloescht                      |
| `set_window(name)`     | App + Adapter muessen gesetzt sein          | Setzt Fensterkontext                       |
| `get_current_window_model()` | Alle drei Zustaende muessen aktiv sein | Liefert Modell des aktiven Fensters         |
| `describe()`           | —                                           | Gibt aktuellen Kontextzustand zurueck      |

---

## Beispiel

```python
context.set_adapter(SeleniumWebAdapter())
context.set_app("MeineApp", app_yaml)
context.set_window("LoginDialog")

model = context.get_current_window_model()
```

---

## Fehlerverhalten

Jede Methode prueft den gueltigen Zustand und liefert bei Fehlverwendung eine **klare und sprechende Fehlermeldung**, z. B.:

- `"No adapter/host active – cannot start app."`
- `"No app active – cannot select window."`
- `"Window 'Foo' not found in app model."`
