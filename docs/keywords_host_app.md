# Keyword-Referenz: Host- & App-Keywords

Diese Anleitung beschreibt die Verwendung der OKW4Robot-Schluesselwoerter fuer Host- und App-Steuerung. Sie bilden das Fundament fuer alle Testfaelle: Ohne aktiven Host (Treiber) und geladene App (Objektlisten-YAML) koennen keine Widgets angesprochen werden.

---

## Host-Keywords

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

Diese Methode startet **noch nicht automatisch den Browser**, sondern stellt nur den Treiber bereit.

---

### `SelectHost    <HostName>`
Wechselt in einen zuvor gestarteten Host-Kontext. Dies ist sinnvoll, wenn mehrere Hosts parallel verwendet werden (z. B. Browser-Vergleich).

Wirft Fehler, wenn der gewuenschte Host nicht aktiv ist.

---

### `StopHost`
Beendet den aktuellen Treiber (z. B. schliesst den Browser) und loescht alle App- und Fensterkontexte.

---

## App-Keywords

### `StartApp    <AppName>`
Laedt eine **Objektlisten-YAML** fuer eine Anwendung. Der Pfad wird wie folgt interpretiert:

- `StartApp    TestApp` -> `locators/TestApp.yaml`
- `StartApp    LoginDialog` -> `locators/LoginDialog.yaml`

Beispiel:
```yaml
TestApp:
  LoginDialog:
    Benutzer:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { css: '[data-testid="Benutzer"]' }
```

Voraussetzung: Ein Host muss zuvor gestartet worden sein.

---

### `SelectWindow    <WindowName>`
Aktiviert ein Fenster oder ein virtuelles Widget aus dem App-Modell. Erst nach Auswahl eines Fensters kann auf darunterliegende Widgets zugegriffen werden.

Beispiel:
```
SelectWindow    LoginDialog
```

---

### `StopApp`
Beendet den aktuellen Anwendungskontext (Modell, Fenster, Name).

---

## Beispiel: Browser wechseln (Chrome vs. Firefox)

```robotframework
*** Settings ***
Library    okw4robot.keywords.host.HostKeywords
Library    okw4robot.keywords.app.AppKeywords
Library    okw4robot.keywords.widget_keywords.WidgetKeywords

*** Test Cases ***
Login mit Chrome
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

Login mit Firefox
    StartHost           Firefox
    StartApp            Firefox
    SelectWindow        Firefox
    SetValue             URL      file:///C:/temp/login.html
    ClickOn              Maximize Window
    StartApp            TestAppOKW4Robot_WEB
    SelectWindow        LoginDialog
    SetValue             Benutzer     admin
    StopApp
    StopHost
```

---

## Hinweise

- Das `SelectWindow` funktioniert sowohl fuer "echte" Fenster als auch fuer virtuelle Objekte (z. B. `URL`, `Maximize Window` bei Browsern).
- Wird `StartHost` erneut aufgerufen, werden App und Fenster-Kontext automatisch zurueckgesetzt.
- Alle Fehler wie "kein Host aktiv", "Fenster nicht gefunden" oder "Widget nicht definiert" werden klar protokolliert.

---

> Du findest die zugehoerigen YAMLs in `locators/` (Projekt) oder in den Treiber-Paketen (z. B. `okw_web_selenium/locators/`).

> Fuer eine Liste aller verfuegbaren Widget-Keywords siehe `docs/keywords_widget.md`.
