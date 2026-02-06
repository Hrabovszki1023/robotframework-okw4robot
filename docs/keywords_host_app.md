# 🧭 Keyword-Referenz: Host- & App-Keywords

Diese Anleitung beschreibt die Verwendung der OKW4Robot-Schlüsselwörter für Host- und App-Steuerung. Sie bilden das Fundament für alle Testfälle: Ohne aktiven Host (Treiber) und geladene App (Objektlisten-YAML) können keine Widgets angesprochen werden.

---

## 🔌 Host-Keywords

### `StartHost    <HostName>`
Lädt und initialisiert den Treiber für die Host-Umgebung (z. B. `Chrome`, `Firefox`). Erwartet wird eine passende Objektlisten-YAML in:

```
# Beispiel: Chrome
src/okw4robot/locators/Chrome.yaml
```

Diese YAML muss enthalten:
```yaml
Chrome:
  __self__:
    class: okw4robot.adapters.selenium_web.SeleniumWebAdapter
    browser: chrome
```

🔄 Diese Methode startet **noch nicht automatisch den Browser**, sondern stellt nur den Treiber bereit.

---

### `SelectHost    <HostName>`
Wechselt in einen zuvor gestarteten Host-Kontext. Dies ist sinnvoll, wenn mehrere Hosts parallel verwendet werden (z. B. Browser-Vergleich).

✅ Wirft Fehler, wenn der gewünschte Host nicht aktiv ist.

---

### `StopHost`
Beendet den aktuellen Treiber (z. B. schließt den Browser) und löscht alle App- und Fensterkontexte.

---

## 🧱 App-Keywords

### `StartApp    <AppName>`
Lädt eine **Objektlisten-YAML** für eine Anwendung. Der Pfad wird wie folgt interpretiert:

- `StartApp    TestApp` → `locators/TestApp.yaml`
- `StartApp    web/TestApp` → `locators/web/TestApp.yaml`

Beispiel:
```yaml
TestApp:
  LoginDialog:
    Benutzer:
      class: okw4robot.widgets.web.TextField
      locator: { css: '[data-testid="Benutzer"]' }
```

☝️ Voraussetzung: Ein Host muss zuvor gestartet worden sein.

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

## 🧪 Beispiel: Browser wechseln (Chrome vs. Firefox)

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
    StartApp            web/TestAppOKW4Robot_WEB
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
    StartApp            web/TestAppOKW4Robot_WEB
    SelectWindow        LoginDialog
    SetValue             Benutzer     admin
    StopApp
    StopHost
```

---

## 📌 Hinweise

- Das `SelectWindow` funktioniert sowohl für "echte" Fenster als auch für virtuelle Objekte (z. B. `URL`, `Maximize Window` bei Browsern).
- Wird `StartHost` erneut aufgerufen, werden App und Fenster-Kontext automatisch zurückgesetzt.
- Alle Fehler wie "kein Host aktiv", "Fenster nicht gefunden" oder "Widget nicht definiert" werden klar protokolliert (inkl. Stacktrace, falls aktiviert).

---

> 📂 Du findest die zugehörigen YAMLs in `locators/` (Projekt) oder `src/okw4robot/locators/` (Framework-Vorgaben).

> 🧩 Für eine Liste aller verfügbaren Widget-Keywords siehe `docs/keywords_widget.md` (folgt).


