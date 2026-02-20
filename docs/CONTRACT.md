# CONTRACT – robotframework-okw4robot

Dieses Dokument definiert den oeffentlichen Vertrag von `robotframework-okw4robot`.

Fuer oekosystem-weite Konzepte (Tokens, Matching-Modi, YES/NO-Modell,
Widget-Delegations-Modell) siehe: **OKW-CONTRACT.md** im okw-workspace.

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

| Paket                           | Namespace           | Treiber          |
|---------------------------------|---------------------|------------------|
| `robotframework-okw-web-selenium` | `okw_web_selenium`  | Selenium/Browser |
| `robotframework-okw-java-swing`   | `okw_java_swing`    | JavaRPC/Swing    |

---

## Keywords (Public API)

### Host Lifecycle

| Keyword       | Parameters      | Description |
|---------------|----------------|-------------|
| `StartHost`   | `<name>`        | Loads the host YAML (`locators/<name>.yaml`), instantiates the adapter and registers it in the global Context. |
| `SelectHost`  | `<name>`        | Asserts that the named host/adapter is currently active. |
| `StopHost`    |                 | Stops the active host/adapter and clears the Context. |

### App Lifecycle

| Keyword        | Parameters      | Description |
|----------------|----------------|-------------|
| `StartApp`     | `<name>`        | Loads the app YAML (`locators/<name>.yaml`), sets the active app model in the Context. |
| `SelectWindow` | `<name>`        | Selects the named window/view from the active app model. All widget keywords operate on this window. |
| `StopApp`      |                 | Clears the active app context. |

### Widget – Write / Interact

| Keyword         | Parameters          | Delegiert an             |
|-----------------|---------------------|--------------------------|
| `SetValue`      | `<name>` `<value>`  | `okw_set_value(value)`   |
| `Select`        | `<name>` `<value>`  | `okw_select(value)`      |
| `TypeKey`       | `<name>` `<key>`    | `okw_type_key(key)`      |
| `TypeKey`       | `<name>` `$DELETE`  | `okw_delete()`           |
| `ClickOn`       | `<name>`            | `okw_click()`            |
| `DoubleClickOn` | `<name>`            | `okw_double_click()`     |
| `SetFocus`      | `<name>`            | `okw_set_focus()`        |

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

Widgets werden in YAML-Dateien beschrieben. Die `class`-Eigenschaft referenziert
die **treiberspezifische** Widget-Klasse:

```yaml
# locators/web/LoginApp.yaml – Selenium-Treiber
LoginApp:
  LoginDialog:
    Username:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { id: user_input }
    Password:
      class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
      locator: { id: password_input }
    OK:
      class: okw_web_selenium.widgets.webse_button.WebSe_Button
      locator: { id: login_btn }
    SubmitButton:
      class: okw_web_selenium.widgets.webse_button.WebSe_Button
      locator: { css: "button[type=submit]" }
```

### YAML-Suche (Fallback)

`okw4robot` sucht YAML-Dateien in dieser Reihenfolge:
1. Projektverzeichnis (`locators/`)
2. `okw_web_selenium.locators` (falls installiert)
3. `okw_java_swing.locators` (falls installiert)

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
