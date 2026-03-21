# Keyword-Referenz: Host- & App-Keywords

Diese Anleitung beschreibt die Verwendung der OKW4Robot-Schluesselwoerter fuer Host- und App-Steuerung. Sie bilden das Fundament fuer alle Testfaelle: Ohne aktiven Adapter und geladene App (Objektlisten-YAML) koennen keine Widgets angesprochen werden.

---

## App-Keywords

### `StartApp    <AppName>`
Laedt eine **Objektlisten-YAML** fuer eine Anwendung. Der Pfad wird wie folgt interpretiert:

- `StartApp    TestApp` -> `locators/TestApp.yaml`
- `StartApp    LoginDialog` -> `locators/LoginDialog.yaml`

**Adapter-Auto-Start:** Enthaelt die YAML einen `__self__`-Block und ist kein Adapter aktiv, wird der Adapter automatisch instanziiert. Alle Parameter aus `__self__` (ausser `class`) werden als kwargs an den Adapter-Konstruktor uebergeben. Ein separater `StartHost`-Aufruf ist dann **nicht noetig**.

Beispiel YAML mit `__self__`:
```yaml
DemoApp:
  __self__:
    class: okw_java_remoteswing.adapters.remote_swing_adapter.RemoteSwingAdapter
    app_alias: demo
    app_command: java -jar /path/to/DemoApp.jar
  MainFrame:
    txtName:
      class: okw_java_remoteswing.widgets.remotesw_textfield.RemoteSw_TextField
      locator: { name: "txtName" }
```

---

### `SelectWindow    <WindowName>`
Aktiviert ein Fenster oder ein virtuelles Widget aus dem App-Modell. Erst nach Auswahl eines Fensters kann auf darunterliegende Widgets zugegriffen werden.

Beispiel:
```
SelectWindow    MainFrame
```

---

### `StopApp`
Beendet den aktuellen Anwendungskontext (Modell, Fenster, Name).

---

## Host-Keywords (optional, rueckwaertskompatibel)

Die Host-Keywords sind weiterhin verfuegbar, werden aber nicht mehr zwingend benoetigt,
wenn die App-YAML einen `__self__`-Block enthaelt.

### `StartHost    <HostName>`
Laedt und initialisiert den Treiber fuer die Host-Umgebung (z. B. `Chrome`, `Firefox`). Erwartet wird eine passende Host-YAML im Treiber-Paket:

```
# Beispiel: Chrome
okw_web_selenium/locators/Chrome.yaml
```

Diese YAML muss enthalten:
```yaml
Chrome:
  __self__:
    class: okw_web_selenium.adapters.selenium_web.SeleniumWebAdapter
    browser: chrome
```

---

### `SelectHost    <HostName>`
Wechselt in einen zuvor gestarteten Host-Kontext. Dies ist sinnvoll, wenn mehrere Hosts parallel verwendet werden (z. B. Browser-Vergleich).

Wirft Fehler, wenn der gewuenschte Host nicht aktiv ist.

---

### `StopHost`
Beendet den aktuellen Treiber (z. B. schliesst den Browser) und loescht alle App- und Fensterkontexte.

---

## Beispiele

### Empfohlener Ablauf (neu): StartApp uebernimmt alles

```robotframework
*** Settings ***
Library    okw_java_remoteswing.library.OkwJavaRemoteSwingLibrary

*** Test Cases ***
JTextField Schreiben Und Lesen
    StartApp        DemoApp
    SelectWindow    MainFrame
    SetValue        txtName    Hello World
    VerifyValue     txtName    Hello World
```

Der Adapter wird automatisch aus `DemoApp.yaml` → `__self__` erzeugt.
Die Java-Swing-App wird im Adapter-Konstruktor gestartet.

### Empfohlener Ablauf (Web/Selenium): StartApp mit __self__

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Test Cases ***
Login Test
    StartApp        MyApp
    SelectWindow    LoginDialog
    SetValue        Username     admin
    SetValue        Password     secret
    ClickOn         Login
    VerifyValue     Status       Logged in
```

Voraussetzung: `MyApp.yaml` enthaelt `__self__` mit Adapter-Klasse und
treiberspezifischen Parametern (z.B. `browser: chrome`, `url: ...`).

### Alter Ablauf (rueckwaertskompatibel): StartHost + StartApp

```robotframework
*** Test Cases ***
Login mit Chrome (alt)
    StartHost           Chrome
    StartApp            Chrome
    SelectWindow        Chrome
    SetValue             URL      file:///C:/temp/login.html
    ClickOn              Maximize Window
    StartApp            TestAppOKW4Robot_WEB
    SelectWindow        LoginDialog
    SetValue             Benutzer     admin
    StopApp
    StopHost
```

Dieser Ablauf funktioniert weiterhin. `StartHost` erzeugt den Adapter explizit,
`StartApp` laedt nur die Widget-Definitionen.

---

## Hinweise

- `StartApp` prueft: Existiert `__self__` UND ist kein Adapter aktiv? → Adapter automatisch erzeugen.
- Ist bereits ein Adapter aktiv (z.B. durch `StartHost` oder vorheriges `StartApp`), wird `__self__` ignoriert.
- `SelectWindow` funktioniert sowohl fuer "echte" Fenster als auch fuer virtuelle Objekte (z. B. `URL`, `Maximize Window` bei Browsern).
- Wird `StartHost` erneut aufgerufen, werden App und Fenster-Kontext automatisch zurueckgesetzt.
- Alle Fehler wie "kein Adapter aktiv", "Fenster nicht gefunden" oder "Widget nicht definiert" werden klar protokolliert.

---

> Du findest die zugehoerigen YAMLs in `locators/` (Projekt) oder in den Treiber-Paketen (z. B. `okw_web_selenium/locators/`).

> Fuer eine Liste aller verfuegbaren Widget-Keywords siehe `docs/keywords_widget.md`.
