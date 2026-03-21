# CONTRACT – robotframework-okw4robot

Dieses Dokument definiert den oeffentlichen Vertrag von `robotframework-okw4robot`.

Fuer oekosystem-weite Konzepte (Tokens, Matching-Modi, YES/NO-Modell,
Widget-Delegations-Modell) siehe: **OKW-CONTRACT.md** im okw-workspace.

---

## Dokumentationssprache (Deutsch / Englisch)

Die OKW-Dokumentation wird **zweisprachig** gepflegt: Deutsch und Englisch.

### Hintergrund

Die Keyword-Bibliothek wird u.a. bei deutschen Bundesbehoerden eingesetzt.
Viele Anwender benoetigen die Dokumentation auf Deutsch. Gleichzeitig soll
das Projekt international zugaenglich bleiben.

### Konvention

| Datei | Sprache | Beispiel |
|-------|---------|---------|
| `dokument.md` | **Englisch** (Primaersprache) | `okw_parameters.md` |
| `dokument_de.md` | **Deutsch** | `okw_parameters_de.md` |

Regeln:

1. **Englisch ist die Primaersprache.** Die Datei ohne Suffix (`*.md`) ist immer
   die englische Version.
2. **Deutsche Version** wird mit dem Suffix `_de.md` gekennzeichnet und liegt
   **neben** der englischen Version im selben Verzeichnis.
3. **Inhaltliche Gleichwertigkeit.** Beide Versionen muessen denselben
   fachlichen Inhalt abdecken. Code-Beispiele und Tabellen sind in beiden
   Versionen identisch (Keywords, Variablennamen, YAML-Syntax sind ohnehin
   sprachunabhaengig).
4. **Aenderungen synchron halten.** Wird eine Version aktualisiert, muss die
   andere Version zeitnah nachgezogen werden.
5. **README.md** verlinkt auf beide Sprachversionen (sofern vorhanden).
6. **Gilt fuer alle OKW-Pakete** (`okw4robot`, `okw-web-selenium`,
   `okw-java-remoteswing`, etc.).

### Verzeichnisstruktur (Beispiel)

```
docs/
  okw_parameters.md          ← Englisch
  okw_parameters_de.md       ← Deutsch
  widgets_common.md           ← Englisch
  widgets_common_de.md        ← Deutsch
  CONTRACT.md                 ← Englisch (dieses Dokument)
  CONTRACT_de.md              ← Deutsch
  ...
```

### Bestehende Dokumente

Bestehende Dokumente, die aktuell nur in einer Sprache vorliegen, werden
schrittweise um die jeweils fehlende Version ergaenzt. Neue Dokumente werden
von Anfang an in beiden Sprachen erstellt.

---

## Library Import

```robot
Library    okw4robot.library.OKW4RobotLibrary
```

---

## Architektur: Delegation statt Steuerung

`okw4robot` ist **treiber-agnostisch**. Keywords rufen keine Adapter-Methoden
direkt auf, sondern delegieren an genau **eine** `okw_*`-Methode des Widgets.
Die treiberspezifische Widget-Klasse (z.B. `WebSe_TextField` in
`okw_web_selenium`) entscheidet intern, wie die Aktion umgesetzt wird.

Die vollstaendige Keyword → Widget-Methoden-Zuordnung ist in der
**OKW-CONTRACT.md** definiert (Abschnitt "Widget-Delegations-Modell").

### Basisklasse

```python
from okw4robot.widgets.okw_widget import OkwWidget
```

`OkwWidget` definiert die Schnittstelle. Nicht implementierte Methoden
werfen `NotImplementedError`. Treiber-Pakete erben von `OkwWidget`
und ueberschreiben die benoetigten Methoden.

### Treiber-Pakete

| Paket                                | Namespace                | Treiber               |
|--------------------------------------|--------------------------|-----------------------|
| `robotframework-okw-web-selenium`    | `okw_web_selenium`       | Selenium/Browser      |
| `robotframework-okw-java-remoteswing`| `okw_java_remoteswing`   | RemoteSwingLibrary/Swing |

---

## Window-Modell: „Ein Fenster ist das, was man als Fenster definiert."

### Grundsatz

In OKW ist ein **Fenster** (Window) kein technischer Begriff, sondern ein
**logisches Konzept**. Ein Fenster ist jeder GUI-Bereich, den das Projekt als
eigenstaendigen Kontext definiert. Das kann sein:

| Technologie | Fenster kann sein |
|-------------|-------------------|
| Java Swing | JFrame, JDialog, JPanel, JTabbedPane, ... |
| HTML/Web | Browserfenster, `<div>`-Bereich, iFrame, Shadow-DOM-Host, ... |
| Windows Desktop | Window, Dialog, UserControl, Panel, ... |
| Mobile | Activity, Fragment, Screen, Modal, ... |

**OKW erzwingt keine 1:1-Abbildung auf physische Fenster.** Das Projekt
entscheidet, wie es seine GUI in logische Fenster „schneidet".

### Fenster als Widget

Ein Fenster hat — wie jedes Widget — eine eigene `class` und einen `locator`
in der YAML-Definition:

```yaml
MeineApp:
  __self__:
    class: okw_web_selenium.adapters.selenium_web.SeleniumWebAdapter
    browser: chrome

  # Physisches Browserfenster
  MainPage:
    class: okw_web_selenium.widgets.webse_frame.WebSe_Frame
    locator: { css: "body" }

    txtSearch:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { id: search_input }

  # Logisches "Fenster" — eine Navigationsleiste (immer sichtbar)
  NavBar:
    class: okw_web_selenium.widgets.webse_panel.WebSe_Panel
    locator: { css: "nav#main-nav" }

    btnHome:
      class: okw_web_selenium.widgets.webse_button.WebSe_Button
      locator: { css: "a[href='/']" }
    btnSettings:
      class: okw_web_selenium.widgets.webse_button.WebSe_Button
      locator: { css: "a[href='/settings']" }

  # Logisches "Fenster" — der Detailbereich (wechselt je nach Ansicht)
  DetailView:
    class: okw_web_selenium.widgets.webse_panel.WebSe_Panel
    locator: { css: "div#detail-content" }

    lblTitle:
      class: okw_web_selenium.widgets.webse_label.WebSe_Label
      locator: { css: "h1.title" }
```

### SelectWindow mit Widget-Semantik

`SelectWindow` ist nicht nur ein Kontext-Wechsel, sondern loest das Fenster
als Widget auf:

1. Liest `class` + `locator` aus dem YAML
2. Instanziiert die Widget-Klasse (z.B. `WebSe_Panel`, `RemoteSw_Frame`)
3. Kann das Fenster aktiv selektieren/fokussieren (ueber den Adapter)
4. Setzt den Window-Context fuer alle nachfolgenden Widget-Keywords

Dadurch kann ein Fenster auch geprueft werden:

```robot
# Pruefen ob die NavBar existiert und sichtbar ist
SelectWindow    NavBar
VerifyExist     NavBar    YES
VerifyIsVisible NavBar    YES

# Dann mit Widgets innerhalb der NavBar arbeiten
ClickOn         btnHome

# Zu einem anderen logischen Fenster wechseln
SelectWindow    DetailView
VerifyValue     lblTitle    Willkommen
```

### Beispiele fuer Fenster-Schnitt

**Beispiel 1: Web-Anwendung mit Sidebar + Content**

```robot
SelectWindow    Sidebar
ClickOn         btnDashboard

SelectWindow    ContentArea
VerifyValue     lblHeading    Dashboard
SetValue        txtFilter     2024
```

**Beispiel 2: Java-Swing mit mehreren Dialogen**

```robot
SelectWindow    MainFrame
ClickOn         btnOpenSettings

SelectWindow    SettingsDialog
SetValue        txtTimeout    30
ClickOn         btnSave

SelectWindow    MainFrame
VerifyValue     lblStatus     Gespeichert
```

**Beispiel 3: Wiederverwendbare Teilbereiche**

Eine Navigationsleiste ist aus jedem Kontext erreichbar — sie ist immer gleich
definiert, egal welche Detail-Ansicht gerade aktiv ist:

```robot
# Egal wo wir gerade sind:
SelectWindow    NavBar
ClickOn         btnHome
```

### Reservierte Keys in Window/Widget-Definitionen

Auf jeder Ebene im YAML-Baum sind folgende Keys reserviert:

| Key | Bedeutung |
|-----|-----------|
| `class` | Vollqualifizierter Klassenname der Widget-Implementierung |
| `locator` | Treiberspezifischer Locator (dict) |
| `__self__` | Adapter-Konfiguration (nur auf App-Root-Ebene) |

Alle anderen Keys auf derselben Ebene sind **Kind-Widgets**.

### Scoping: Fenster-Context begrenzt die Widget-Suche

`SelectWindow` setzt nicht nur den logischen Context, sondern begrenzt auch
den **Suchbereich** fuer nachfolgende Widget-Keywords. Dadurch koennen
mehrere Fenster/Dialoge gleichzeitig existieren, die Widgets mit identischen
Namen enthalten — der Fenster-Context stellt sicher, dass das richtige
Widget gefunden wird.

**Problem ohne Scoping:**

```
┌─ MainFrame ────────────┐   ┌─ SettingsDialog ──────────┐
│  [txtUser] name="user" │   │  [txtUser] name="user"    │
└────────────────────────┘   └──────────────────────────┘

SetValue  txtUser  admin   → Welches "user"??
```

**Loesung mit Fenster-Context:**

```robot
SelectWindow    MainFrame           # Scope = MainFrame
SetValue        txtUser    admin    # findet "user" in MainFrame ✓

SelectWindow    SettingsDialog      # Scope = SettingsDialog
SetValue        txtUser    root     # findet "user" in SettingsDialog ✓
```

### Scoping-Umsetzung pro Treiber

OKW gibt den logischen Context vor (Window → Widget). Der Treiber setzt
das Scoping konkret um. Die Container-Widget-Klasse entscheidet in
`okw_select_window()`, wie der Suchbereich eingeschraenkt wird:

| Treiber | Widget-Klasse | Scoping-Mechanismus |
|---------|--------------|---------------------|
| **Swing (RemoteSwing)** | `RemoteSw_Frame` | `Select Window <name>` (SwingLibrary) |
| | `RemoteSw_Dialog` | `Select Dialog <name>` (SwingLibrary) |
| | `RemoteSw_Panel` | `Select Context <name>` (SwingLibrary) |
| **Web (Selenium)** | `WebSe_Frame` | `find_element(locator)` als Parent-Element |
| | `WebSe_Panel` | `find_element(locator)` als Parent-Element |
| | `WebSe_Dialog` | `find_element(locator)` als Parent-Element |

**Swing:** SwingLibrary hat eingebautes Context-Scoping. `Select Window`,
`Select Dialog` und `Select Context` begrenzen alle nachfolgenden
Komponentensuchen auf den gewaehlten Container. Komponenten mit identischen
Namen in verschiedenen Containern werden korrekt unterschieden.

**Web/Selenium:** Selenium hat kein eingebautes Context-Scoping. Die
Container-Widget-Klasse merkt sich das Parent-Element (`find_element(locator)`)
und Kind-Widgets suchen relativ dazu (`parent.find_element(...)`).

### Treiber-Unabhaengigkeit

Dieses Modell gilt fuer **alle** OKW-Treiber. Jeder Treiber implementiert
die passenden Container-Widget-Klassen:

| Treiber | Container-Widget-Klassen |
|---------|-------------------------|
| `okw-web-selenium` | `WebSe_Frame`, `WebSe_Panel`, `WebSe_Dialog` |
| `okw-java-remoteswing` | `RemoteSw_Frame`, `RemoteSw_Dialog`, `RemoteSw_Panel` |

---

## Keywords (Public API)

### App Lifecycle

| Keyword        | Parameters      | Description |
|----------------|----------------|-------------|
| `StartApp`     | `<name>`        | Loads the app YAML (`locators/<name>.yaml`), sets the active app model in the Context. If the YAML contains a `__self__` section and no adapter is active, the adapter is instantiated automatically. |
| `SelectWindow` | `<name>`        | Selects the named window/view from the active app model. Resolves the window as a widget (class + locator). Can verify and focus the window via the adapter. All widget keywords operate on this window. |
| `StopApp`      |                 | Clears the active app context. |

### Host Lifecycle (optional, rueckwaertskompatibel)

| Keyword       | Parameters      | Description |
|---------------|----------------|-------------|
| `StartHost`   | `<name>`        | Loads the host YAML (`locators/<name>.yaml`), instantiates the adapter and registers it in the global Context. Optional if `StartApp` YAML contains `__self__`. |
| `SelectHost`  | `<name>`        | Asserts that the named host/adapter is currently active. |
| `StopHost`    |                 | Stops the active host/adapter and clears the Context. |

### Adapter-Auto-Start via `__self__`

When `StartApp` loads a YAML that contains a `__self__` section and no adapter is
currently active, the adapter is created automatically:

```yaml
DemoApp:
  __self__:
    class: okw_java_remoteswing.adapters.remote_swing_adapter.RemoteSwingAdapter
    app_alias: demo
    app_command: java -jar DemoApp.jar

  MainFrame:
    class: okw_java_remoteswing.widgets.remotesw_frame.RemoteSw_Frame
    locator: { name: "MainFrame" }

    txtName:
      class: okw_java_remoteswing.widgets.remotesw_textfield.RemoteSw_TextField
      locator: { name: "txtName" }
```

All parameters in `__self__` (except `class`) are passed as kwargs to the adapter
constructor. The adapter decides how to use them (e.g. `RemoteSwingAdapter` starts
the Java app, `SeleniumWebAdapter` opens a browser).

A separate `StartHost` call is **not required** if `__self__` is present in the
app YAML.

### Widget – Write / Interact

| Keyword              | Parameters                  | Delegiert an                        |
|----------------------|-----------------------------|-------------------------------------|
| `SetValue`           | `<name>` `<value>`          | `okw_set_value(value)`              |
| `Select`             | `<name>` `<value>`          | `okw_select(value)`                 |
| `TypeKey`            | `<name>` `<key>`            | `okw_type_key(key)`                 |
| `TypeKey`            | `<name>` `$DELETE`          | `okw_delete()`                      |
| `ClickOn`            | `<name>`                    | `okw_click()`                       |
| `DoubleClickOn`      | `<name>`                    | `okw_double_click()`                |
| `DoubleClickOn`      | `<name>` `<value>`          | `okw_double_click_value(value)`     |
| `SetFocus`           | `<name>`                    | `okw_set_focus()`                   |
| `SelectContextMenu`  | `<name>` `<path>`           | `okw_select_context_menu(path)`     |

### Window – Keyboard (NEU)

| Keyword              | Parameters                  | Delegiert an                        |
|----------------------|-----------------------------|-------------------------------------|
| `TypeKeyWindow`      | `<key>`                     | _(Fenster-level Tastaturkommando)_  |

`TypeKeyWindow` sendet Tastaturkommandos an das aktuelle Fenster (nicht an
ein bestimmtes Widget). Typische Anwendungsfaelle: Menue-Shortcuts, Hotkeys,
Tastenkombinationen (z.B. `<Strg+P>`, `<Strg+S>`, `<Enter>`).

Im Gegensatz zu `TypeKey` wird kein Widget aufgeloest — das Kommando geht
direkt an das aktive Fenster.

```robot
# Beispiel
SelectWindow     MainFrame
TypeKeyWindow    <Strg+P>    # Druckdialog oeffnen
TypeKeyWindow    <Strg+S>    # Speichern
```

**Status:** NEU — noch zu implementieren.

### Widget – Verify Value

| Keyword           | Parameters                | Delegiert an        |
|-------------------|--------------------------|---------------------|
| `VerifyValue`     | `<name>` `<expected>`    | `okw_get_value()`   |
| `VerifyValueWCM`  | `<name>` `<pattern>`     | `okw_get_value()`   |
| `VerifyValueREGX` | `<name>` `<regex>`       | `okw_get_value()`   |

Timeout: `${OKW_TIMEOUT_VERIFY_VALUE}` (default: 10s).

### Widget – Verify State

| Keyword             | Parameters              | Delegiert an          |
|---------------------|------------------------|-----------------------|
| `VerifyExist`       | `<name>` `<expected>`  | `okw_exists()`        |
| `VerifyIsVisible`   | `<name>` `<expected>`  | `okw_is_visible()`    |
| `VerifyIsEnabled`   | `<name>` `<expected>`  | `okw_is_enabled()`    |
| `VerifyIsEditable`  | `<name>` `<expected>`  | `okw_is_editable()`   |
| `VerifyIsFocusable` | `<name>` `<expected>`  | `okw_is_focusable()`  |
| `VerifyIsClickable` | `<name>` `<expected>`  | `okw_is_clickable()`  |
| `VerifyHasFocus`    | `<name>` `<expected>`  | `okw_has_focus()`     |

The `expected` parameter accepts `YES`/`NO`, `TRUE`/`FALSE`, or `1`/`0` (case-insensitive).
Timeouts: `${OKW_TIMEOUT_VERIFY_EXIST}`, `${OKW_TIMEOUT_VERIFY_VISIBLE}`, etc. (default: 2s).

### Widget – Memorize / Log

| Keyword         | Parameters                    | Delegiert an            |
|-----------------|------------------------------|-------------------------|
| `MemorizeValue` | `<name>` `<variable>`        | `okw_memorize_value()`  |
| `LogValue`      | `<name>`                     | `okw_log_value()`       |
| `HasValue`      | `<name>`                     | `okw_has_value()`       |

### Caption (sichtbarer Text)

| Keyword            | Parameters                | Delegiert an        |
|--------------------|--------------------------|---------------------|
| `VerifyCaption`    | `<name>` `<expected>`    | `okw_get_text()`    |
| `VerifyCaptionWCM` | `<name>` `<pattern>`     | `okw_get_text()`    |
| `VerifyCaptionREGX`| `<name>` `<regex>`       | `okw_get_text()`    |
| `MemorizeCaption`  | `<name>` `<variable>`    | `okw_get_text()`    |
| `LogCaption`       | `<name>`                 | `okw_get_text()`    |

Timeout: `${OKW_TIMEOUT_VERIFY_CAPTION}` (default: 10s).

### Label

| Keyword           | Parameters                | Delegiert an         |
|-------------------|--------------------------|----------------------|
| `VerifyLabel`     | `<name>` `<expected>`    | `okw_get_label()`    |
| `VerifyLabelWCM`  | `<name>` `<pattern>`     | `okw_get_label()`    |
| `VerifyLabelREGX` | `<name>` `<regex>`       | `okw_get_label()`    |
| `MemorizeLabel`   | `<name>` `<variable>`    | `okw_get_label()`    |
| `LogLabel`        | `<name>`                 | `okw_get_label()`    |

Timeout: `${OKW_TIMEOUT_VERIFY_LABEL}` (default: 10s).

### Tooltip

| Keyword             | Parameters                | Delegiert an          |
|---------------------|--------------------------|---------------------- |
| `VerifyTooltip`     | `<name>` `<expected>`    | `okw_get_tooltip()`   |
| `VerifyTooltipWCM`  | `<name>` `<pattern>`     | `okw_get_tooltip()`   |
| `VerifyTooltipREGX` | `<name>` `<regex>`       | `okw_get_tooltip()`   |
| `MemorizeTooltip`   | `<name>` `<variable>`    | `okw_get_tooltip()`   |
| `LogTooltip`        | `<name>`                 | `okw_get_tooltip()`   |

Timeout: `${OKW_TIMEOUT_VERIFY_TOOLTIP}` (default: 10s).

### Attribute

| Keyword               | Parameters                           | Delegiert an                |
|-----------------------|-------------------------------------|-----------------------------|
| `VerifyAttribute`     | `<name>` `<attribute>` `<expected>` | `okw_get_attribute(name)`   |
| `VerifyAttributeWCM`  | `<name>` `<attribute>` `<pattern>`  | `okw_get_attribute(name)`   |
| `VerifyAttributeREGX` | `<name>` `<attribute>` `<regex>`    | `okw_get_attribute(name)`   |
| `MemorizeAttribute`   | `<name>` `<attribute>` `<variable>` | `okw_get_attribute(name)`   |
| `LogAttribute`        | `<name>` `<attribute>`              | `okw_get_attribute(name)`   |

Timeout: `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` (default: 10s).

### Placeholder

| Keyword                 | Parameters                | Delegiert an              |
|-------------------------|--------------------------|---------------------------|
| `VerifyPlaceholder`     | `<name>` `<expected>`    | `okw_get_placeholder()`   |
| `VerifyPlaceholderWCM`  | `<name>` `<pattern>`     | `okw_get_placeholder()`   |
| `VerifyPlaceholderREGX` | `<name>` `<regex>`       | `okw_get_placeholder()`   |

Timeout: `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}` (default: 10s).

### List / Selection

| Keyword               | Parameters                    | Delegiert an               |
|-----------------------|------------------------------|----------------------------|
| `VerifyListCount`     | `<name>` `<expected_count>`  | `okw_get_list_count()`     |
| `VerifySelectedCount` | `<name>` `<expected_count>`  | `okw_get_selected_count()` |

Timeout: `${OKW_TIMEOUT_VERIFY_LIST}` (default: 2s).

---

## OKW Tokens

Siehe **OKW-CONTRACT.md** fuer die vollstaendige Token-Dokumentation.

| Token      | Supported by              | Behavior |
|------------|--------------------------|----------|
| `$IGNORE`  | All keywords with `value`/`expected` | Keyword is skipped (PASS). No action, no assertion. |
| `$EMPTY`   | `SetValue`               | Sets an explicit empty string. Never ignored even with `${OKW_IGNORE_EMPTY}=YES`. |
| `$DELETE`  | `TypeKey`                | Delegates to `okw_delete()` on the widget. |

---

## YES/NO Existence Model

Siehe **OKW-CONTRACT.md** (Abschnitt "YES/NO-Modell").

---

## Locator YAML Format

Widgets werden in YAML-Dateien beschrieben. Jeder Knoten mit `class` + `locator`
ist ein Widget — das gilt fuer Fenster und fuer Blatt-Widgets gleichermassen:

```yaml
# locators/LoginApp.yaml – Selenium-Treiber
LoginApp:
  __self__:
    class: okw_web_selenium.adapters.selenium_web.SeleniumWebAdapter
    browser: chrome
    url: https://example.com/login

  LoginDialog:
    class: okw_web_selenium.widgets.webse_panel.WebSe_Panel
    locator: { css: "div#login-form" }

    Username:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { id: user_input }
    Password:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { id: password_input }
    Login:
      class: okw_web_selenium.widgets.webse_button.WebSe_Button
      locator: { css: "button[type=submit]" }
```

```yaml
# locators/DemoApp.yaml – RemoteSwing-Treiber
DemoApp:
  __self__:
    class: okw_java_remoteswing.adapters.remote_swing_adapter.RemoteSwingAdapter
    app_alias: demo
    app_command: java -jar DemoApp.jar

  MainFrame:
    class: okw_java_remoteswing.widgets.remotesw_frame.RemoteSw_Frame
    locator: { name: "MainFrame" }

    txtName:
      class: okw_java_remoteswing.widgets.remotesw_textfield.RemoteSw_TextField
      locator: { name: "txtName" }
    btnOk:
      class: okw_java_remoteswing.widgets.remotesw_button.RemoteSw_Button
      locator: { name: "btnOk" }
```

### YAML-Suche (Fallback)

`okw4robot` sucht YAML-Dateien in dieser Reihenfolge:
1. Projektverzeichnis (`locators/`)
2. `okw_web_selenium.locators` (falls installiert)
3. `okw_java_remoteswing.locators` (falls installiert)

---

## Timeout Variables Reference

| Variable                             | Default | Keywords |
|--------------------------------------|---------|---------|
| `${OKW_TIMEOUT_VERIFY_VALUE}`        | 10s     | VerifyValue, VerifyValueWCM, VerifyValueREGX |
| `${OKW_TIMEOUT_VERIFY_EXIST}`        | 2s      | VerifyExist |
| `${OKW_TIMEOUT_VERIFY_VISIBLE}`      | 2s      | VerifyIsVisible |
| `${OKW_TIMEOUT_VERIFY_ENABLED}`      | 2s      | VerifyIsEnabled |
| `${OKW_TIMEOUT_VERIFY_EDITABLE}`     | 2s      | VerifyIsEditable |
| `${OKW_TIMEOUT_VERIFY_FOCUS}`        | 2s      | VerifyHasFocus |
| `${OKW_TIMEOUT_VERIFY_FOCUSABLE}`    | 2s      | VerifyIsFocusable |
| `${OKW_TIMEOUT_VERIFY_CLICKABLE}`    | 2s      | VerifyIsClickable |
| `${OKW_TIMEOUT_VERIFY_CAPTION}`      | 10s     | VerifyCaption, VerifyCaptionWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_LABEL}`        | 10s     | VerifyLabel, VerifyLabelWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_TOOLTIP}`      | 10s     | VerifyTooltip, VerifyTooltipWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}`    | 10s     | VerifyAttribute, VerifyAttributeWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}`  | 10s     | VerifyPlaceholder, VerifyPlaceholderWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_LIST}`         | 2s      | VerifyListCount, VerifySelectedCount |
| `${OKW_POLL_VERIFY}`                 | 0.1s    | All Verify keywords (poll interval) |
