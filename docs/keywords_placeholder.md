# Placeholder-Keywords

Diese Seite beschreibt die Prüfung von Placeholdern (HTML-Attribut `placeholder`) je Widget sowie die zugehörigen Robot-Keywords.

---

## Unterstützte Widgets

- TextField (`input`): unterstützt Placeholder vollständig
- MultilineField (`textarea`): unterstützt Placeholder vollständig
- ComboBox: unterstützt Placeholder nur, wenn die Combo ein Eingabefeld verwendet; native `<select>`-Elemente haben i. d. R. keinen Placeholder (lesen dann `""`).
- Nicht unterstützt: Button, Label, CheckBox, RadioList, ListBox

---

## Keywords (Library: `okw4robot.keywords.placeholder_keywords.PlaceholderKeywords`)

- `VerifyPlaceholder    <Name>    <Soll>`: exakter Vergleich
- `VerifyPlaceholderWCM <Name>    <Soll>`: Wildcard-Match (`*`, `?`), mehrzeilig möglich
- `VerifyPlaceholderREGX <Name>   <Regex>`: Regex-Match

Ignore-Regel: Leere Werte (optional via `${OKW_IGNORE_EMPTY}=YES`) oder das Token `$IGNORE` führen zu einem No-Op.

---

## Beispiele (Robot Framework)

```robotframework
*** Settings ***
Library    okw4robot.keywords.placeholder_keywords.PlaceholderKeywords    WITH NAME    PH

*** Test Cases ***
Placeholder Prüfen
    Select Window           WidgetsDemo
    VerifyPlaceholder       Name         Nachname
    VerifyPlaceholderWCM    Vorname      *name*
    VerifyPlaceholderREGX   Anmerkung    ^Mehrzeilige\s+Eingabe
```

---

## Implementierung

- Adapter: `src/okw4robot/adapters/selenium_web.py` → `get_attribute(locator, name)`
- TextField: `src/okw4robot/widgets/common/text_field.py` → `okw_verify_placeholder*`
- MultilineField: erbt von TextField
- ComboBox: `src/okw4robot/widgets/common/combobox.py` → `okw_verify_placeholder*` (nur sinnvoll bei input-basierten Combos)
 - Keywords: `src/okw4robot/keywords/placeholder_keywords.py`

---

## Hinweis zu Regex in Robot

Backslashes werden in Robot‑Tabellen häufig als Escape interpretiert. Nutze daher z. B. `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^Mehrzeilige\\s+Eingabe`). Das betrifft alle REGX‑Varianten der Placeholder‑Keywords.
