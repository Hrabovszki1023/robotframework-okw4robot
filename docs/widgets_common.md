# Web-Widgets (Selenium)

Diese Seite dokumentiert die Web-Widget-Klassen im Treiber-Paket `okw_web_selenium`.
Die Klassen erben von `OkwWidget` (definiert in `okw4robot`) und implementieren
die treiberspezifische Logik via SeleniumLibrary.

---

## Grundlagen

- **Delegation**: Keywords rufen `widget.okw_*()` auf. Das Widget entscheidet intern,
  wie die Aktion treiberspezifisch (via SeleniumLibrary/Adapter) umgesetzt wird.
- **Locator-Format**: YAML-Locatoren sind in der Regel ein Dict mit genau einem
  Schluessel, z.B. `{ css: '...' }`, `{ xpath: '...' }`. Die Aufloesung uebernimmt der Adapter.
- **Fehlersemantik**:
  - Ungueltige Locator-Formate: `ValueError`
  - Nicht gefundene Elemente bei Verifikationen: `AssertionError`
  - Laufzeitfehler des Backends: `RuntimeError` oder spezifische Exceptions

---

## Klassenuebersicht

### OkwWidget (Basisklasse)
Pfad: `okw4robot/widgets/okw_widget.py`

Definiert die vollstaendige Schnittstelle. Nicht implementierte Methoden werfen
`NotImplementedError`. Treiber-Pakete erben und ueberschreiben die benoetigten Methoden.

### WebSe_Base (Selenium-Basis)
Pfad: `okw_web_selenium/widgets/webse_base.py`

Erbt von `OkwWidget`. Implementiert gemeinsame Selenium-Logik:
- `okw_click()`, `okw_double_click()`, `okw_delete()`
- `okw_exists()`, `okw_is_visible()`, `okw_is_enabled()`, `okw_is_editable()`
- `okw_has_focus()`, `okw_is_focusable()`, `okw_is_clickable()`
- `okw_get_text()`, `okw_get_label()`, `okw_get_tooltip()`, `okw_get_placeholder()`
- `okw_get_attribute(name)`
- `_wait_before(intent)` – Sync-Strategie (exists, scroll, visible, enabled, editable, busy)

---

### WebSe_Button
Pfad: `okw_web_selenium/widgets/webse_button.py`

- `okw_get_value()` -> sichtbarer Text als Wert

---

### WebSe_TextField
Pfad: `okw_web_selenium/widgets/webse_textfield.py`

- `okw_set_value(value)` -> Clear + input_text
- `okw_get_value()` -> adapter.get_value
- `okw_type_key(key)` -> press_keys

---

### WebSe_MultilineField
Pfad: `okw_web_selenium/widgets/webse_multilinefield.py`

Erbt von `WebSe_TextField`. Identisches Verhalten.

---

### WebSe_Label
Pfad: `okw_web_selenium/widgets/webse_label.py`

- `okw_get_value()` -> adapter.get_text (sichtbarer Text)

---

### WebSe_CheckBox
Pfad: `okw_web_selenium/widgets/webse_checkbox.py`

- `okw_set_value(value)` -> akzeptiert Checked/Unchecked/True/False/Yes/No
- `okw_get_value()` -> "Checked" oder "Unchecked"

Robot-Beispiele:
```robotframework
SetValue     myCheckbox    Checked
VerifyValue  myCheckbox    Checked
SetValue     myCheckbox    Unchecked
```

---

### WebSe_ComboBox
Pfad: `okw_web_selenium/widgets/webse_combobox.py`

- `okw_set_value(value)` -> editable: clear+type, non-editable: select
- `okw_select(value)` -> select_by_label
- `okw_get_value()` -> aktuell ausgewaehlter Wert
- `okw_type_key(key)` -> press_keys (nur wenn editable)

---

### WebSe_RadioList
Pfad: `okw_web_selenium/widgets/webse_radiolist.py`

- `okw_select(value)` -> waehlt per value innerhalb der Gruppe
- `okw_get_value()` -> aktuell ausgewaehlter Wert

YAML-Varianten:
- Name-basiert: `group: zahlungsmethode`
- Container-basiert: `locator: { css: '[data-testid="..."]' }`

---

### WebSe_ListBox
Pfad: `okw_web_selenium/widgets/webse_listbox.py`

- `okw_select(value)` / `okw_set_value(value)` -> Auswahl per Label
- `okw_get_value()` -> kommaseparierte Liste der ausgewaehlten Werte

---

### WebSe_Table
Pfad: `okw_web_selenium/widgets/webse_table.py`

- `okw_get_row_texts(row)`, `okw_get_column_texts(col)`, `okw_get_cell_text(row, col)`
- `okw_get_row_count()`, `okw_get_column_count()`, `okw_get_header_names()`

---

## Robot-Keywords -> Widget-Methoden (Mapping)

- `ClickOn <Name>` -> `okw_click()`
- `DoubleClickOn <Name>` -> `okw_double_click()`
- `SetValue <Name> <Wert>` -> `okw_set_value(value)`
- `Select <Name> <Wert>` -> `okw_select(value)`
- `TypeKey <Name> <Key>` -> `okw_type_key(key)`
- `VerifyValue <Name> <Soll>` -> `okw_get_value()` + verify_with_timeout
- `VerifyExist <Name> YES|NO` -> `okw_exists()` + verify_yes_no_poll
- `LogValue <Name>` -> `okw_get_value()` + log
- `MemorizeValue <Name> <Variable>` -> `okw_get_value()` + set_test_variable

Pfad: `okw4robot/keywords/widget_keywords.py`

---

## YAML-Beispiel

```yaml
LoginDialog:
  __self__:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="login-page"]' }

  Benutzer:
    class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
    locator: { css: '[data-testid="username"]' }

  Passwort:
    class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
    locator: { css: '[data-testid="password"]' }

  OK:
    class: okw_web_selenium.widgets.webse_button.WebSe_Button
    locator: { css: '[data-testid="login"]' }

  Status:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="status-text"]' }
```

---

## Projektspezifische Erweiterungen

Ableiten von WebSe_*-Widgets fuer projektspezifische Besonderheiten:

```python
class MyProjectCombo(WebSe_ComboBox):
    def okw_set_value(self, value):
        # Projekt-spezifische Logik
        super().okw_set_value(value)
```

YAML:
```yaml
MeinCombo:
  class: myproject.widgets.MyProjectCombo
  locator: { css: "#combo" }
```
