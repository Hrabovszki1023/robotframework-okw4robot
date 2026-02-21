# Widget-Vererbung und Erweiterungsstrategie

## Grundidee

Eine universelle, fuer **alle** GUI-Objekte aller Technologien gueltige
Implementierung gibt es nicht. HTML-Buttons verhalten sich anders als
Swing-Buttons, und selbst innerhalb einer Technologie kann ein Unternehmen oder
Projekt eigene GUI-Konventionen haben, die vom Standard abweichen.

OKW loest das durch eine **mehrstufige Vererbungskette**, die es erlaubt, auf
jeder Ebene einzugreifen – vom globalen Standard bis zur Einzelanpassung eines
konkreten GUI-Objekts.

---

## Vererbungskette

```
OkwWidget                              okw4robot (Interface / Vertrag)
    │
    │   Definiert alle okw_*-Methoden mit NotImplementedError.
    │   Kein treiberspezifischer Code.
    │
    ├── WebSe_Base                     okw-web-selenium (Treiber-Paket)
    │       │
    │       │   Allgemeine Selenium-Implementierung fuer den HTML-Standard:
    │       │   click, exists, visible, enabled, get_text, get_label, ...
    │       │
    │       ├── WebSe_Button           Globale Implementierung fuer <button>
    │       ├── WebSe_TextField        Globale Implementierung fuer <input type="text">
    │       ├── WebSe_CheckBox         Globale Implementierung fuer <input type="checkbox">
    │       ├── WebSe_ComboBox         Globale Implementierung fuer <select>
    │       ├── WebSe_RadioList        Globale Implementierung fuer <input type="radio">
    │       ├── WebSe_Table            Globale Implementierung fuer <table>
    │       └── ...
    │
    ├── JavaSw_Base                    okw-java-swing (Treiber-Paket)
    │       │
    │       ├── JavaSw_Button          Globale Implementierung fuer JButton
    │       ├── JavaSw_TextField       Globale Implementierung fuer JTextField
    │       └── ...
    │
    └── (weitere Treiber: Playwright, WinUI, ...)
```

---

## Erweiterungsebenen

Die Vererbungskette kann auf **vier Ebenen** erweitert werden:

### Ebene 1: Treiber-Standard (z.B. WebSe_Button)

Die mitgelieferten Widget-Klassen decken das **Standard-Verhalten** der
jeweiligen GUI-Technologie ab. Fuer die meisten Projekte reichen diese aus.

### Ebene 2: Unternehmensspezifische Widgets

Wenn ein Unternehmen eigene GUI-Konventionen hat (z.B. alle Buttons haben ein
bestimmtes Loading-Pattern, oder Dropdowns werden als Custom-Components statt
nativer `<select>` gebaut), kann ein unternehmensweites Widget-Paket erstellt
werden:

```python
# firma_widgets/firma_button.py
from okw_web_selenium.widgets.webse_button import WebSe_Button

class FirmaButton(WebSe_Button):
    def okw_click(self):
        super().okw_click()
        # Nach jedem Klick: Warte bis Loading-Spinner weg ist
        self.adapter.wait_until_not_visible({'css': '.spinner'}, timeout=10)
```

### Ebene 3: Projektspezifische Widgets

Wenn ein Projekt innerhalb des Unternehmens abweichende GUI-Elemente hat:

```python
# projekt_abc/widgets/projekt_combo.py
from okw_web_selenium.widgets.webse_combobox import WebSe_ComboBox

class ProjektAbcCombo(WebSe_ComboBox):
    def okw_set_value(self, value):
        # Dieses Projekt nutzt ein React-Select statt nativem <select>
        self.adapter.click(self.locator)
        search_input = {'css': f'{self.locator["css"]} input.react-select__input'}
        self.adapter.input_text(search_input, value)
        option = {'css': f'.react-select__option:contains("{value}")'}
        self.adapter.click(option)
```

### Ebene 4: Einzelanpassung (GUI-Objekt tanzt aus der Reihe)

Manchmal weicht ein einzelnes GUI-Objekt vom Projektstandard ab. Auch dafuer
kann eine Klasse abgeleitet werden:

```python
# projekt_abc/widgets/sonder_checkbox.py
from okw_web_selenium.widgets.webse_checkbox import WebSe_CheckBox

class SonderCheckbox(WebSe_CheckBox):
    def okw_get_value(self):
        # Dieses spezielle Element nutzt aria-checked statt checked
        val = self.adapter.get_attribute(self.locator, 'aria-checked')
        return "Checked" if val == 'true' else "Unchecked"
```

---

## Einbindung ueber YAML-Locators

Eigene Widget-Klassen werden im YAML-Locator referenziert. Der `class`-Pfad
bestimmt, welche Implementierung fuer ein GUI-Objekt verwendet wird:

```yaml
MeineApp:
  # Standard-Widget (aus Treiber-Paket)
  Benutzername:
    class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
    locator: { css: '#username' }

  # Unternehmens-Widget
  Speichern:
    class: firma_widgets.firma_button.FirmaButton
    locator: { css: '#save-btn' }

  # Projekt-Widget
  Kategorie:
    class: projekt_abc.widgets.projekt_combo.ProjektAbcCombo
    locator: { css: '#category-select' }

  # Einzelanpassung
  AGB akzeptiert:
    class: projekt_abc.widgets.sonder_checkbox.SonderCheckbox
    locator: { css: '#terms-checkbox' }
```

> **Kernprinzip:** Der YAML-Locator entscheidet, welche Widget-Klasse fuer ein
> GUI-Objekt verwendet wird. Die Keywords (`SetValue`, `VerifyValue`, ...)
> bleiben immer gleich – nur die Implementierung dahinter aendert sich.

---

## OkwWidget – Interface (Basisklasse)

Pfad: `okw4robot/widgets/okw_widget.py`

Definiert die vollstaendige Schnittstelle. Alle Methoden werfen
`NotImplementedError`. Treiber-Pakete erben und ueberschreiben die benoetigten
Methoden.

### Interaktion

| Methode | Beschreibung |
|---------|-------------|
| `okw_click()` | Klick auf das Element |
| `okw_double_click()` | Doppelklick |
| `okw_set_value(value)` | Wert setzen (Eingabe) |
| `okw_select(value)` | Wert auswaehlen (z.B. Dropdown, RadioList) |
| `okw_type_key(key)` | Taste druecken |
| `okw_delete()` | Inhalt loeschen |
| `okw_set_focus()` | Fokus setzen |

### Werte lesen

| Methode | Beschreibung |
|---------|-------------|
| `okw_get_value()` | Aktueller Wert des Elements |
| `okw_get_text()` | Sichtbarer Text |
| `okw_get_attribute(name)` | Beliebiges Attribut |
| `okw_get_tooltip()` | Tooltip-Text |
| `okw_get_label()` | Label/Beschriftung |
| `okw_get_placeholder()` | Platzhalter-Text |
| `okw_get_caption()` | Caption (sichtbarer Text des Elements selbst) |

### Zustand

| Methode | Beschreibung |
|---------|-------------|
| `okw_exists()` | Element vorhanden? |
| `okw_is_visible()` | Sichtbar? |
| `okw_is_enabled()` | Aktiviert? |
| `okw_is_editable()` | Bearbeitbar? |
| `okw_has_focus()` | Hat Fokus? |
| `okw_is_focusable()` | Fokussierbar? |
| `okw_is_clickable()` | Klickbar? |

### Listen

| Methode | Beschreibung |
|---------|-------------|
| `okw_get_list_count()` | Anzahl Eintraege |
| `okw_get_selected_count()` | Anzahl ausgewaehlte Eintraege |

### Tabellen

| Methode | Beschreibung |
|---------|-------------|
| `get_cell_text(row, col)` | Zellenwert (0-basiert) |
| `get_row_texts(row)` | Alle Werte einer Zeile |
| `get_column_texts(col)` | Alle Werte einer Spalte |
| `get_row_count()` | Anzahl Zeilen |
| `get_column_count()` | Anzahl Spalten |
| `get_header_names()` | Spaltennamen |

---

## Keyword → Widget-Methoden (Mapping)

| Robot-Keyword | Widget-Methode |
|---------------|---------------|
| `ClickOn <Name>` | `okw_click()` |
| `DoubleClickOn <Name>` | `okw_double_click()` |
| `SetValue <Name> <Wert>` | `okw_set_value(value)` |
| `Select <Name> <Wert>` | `okw_select(value)` |
| `TypeKey <Name> <Key>` | `okw_type_key(key)` |
| `VerifyValue <Name> <Soll>` | `okw_get_value()` + Verify-Loop |
| `VerifyExist <Name> YES/NO` | `okw_exists()` + Verify-Loop |
| `LogValue <Name>` | `okw_get_value()` + Log |
| `MemorizeValue <Name> <Var>` | `okw_get_value()` + set_test_variable |

Vollstaendige Keyword-Liste: [KEYWORDS.md](KEYWORDS.md)

---

## Treiberspezifische Dokumentation

Fuer die konkrete Implementierung der Widget-Klassen siehe die jeweilige
Treiber-Dokumentation:

- **Selenium**: [okw-web-selenium/docs/widgets_common.md](http://192.168.1.130:3000/Hrabovszki1023/robotframework-okw-web-selenium/src/branch/main/docs/widgets_common.md)
- **Java Swing**: (in Arbeit)
