Listen‑Keywords (Anzahl und Auswahl)

Diese Seite beschreibt die Keywords zur Prüfung der Anzahl von Einträgen in listenartigen Widgets sowie der Anzahl ausgewählter Einträge.

Unter „listenartig“ fallen u. a.: ListBox, RadioList (Gruppe von Radiobuttons), ComboBox‑Optionsliste (bei nativem `<select>`), ggf. TreeView (als Liste von Blatt‑Pfaden).

---

## Keywords (Library: `okw4robot.keywords.list_keywords.ListKeywords`)

- `VerifyListCount       <Name>    <ExpectedCount>`
  - Prüft die Anzahl der Einträge eines listenartigen Widgets.
  - Wartet bis der Zählwert dem Soll entspricht (Timeout gesteuert, s. u.).

- `VerifySelectedCount   <Name>    <ExpectedCount>`
  - Prüft die Anzahl ausgewählter Einträge.
  - Für RadioList typischerweise 0/1; für ListBox (multi‑select) ≥ 0; für ComboBox meist 0/1.

Unterstützte Widgets (Basismodelle)
- ListBox: Einträge = Anzahl `option`; ausgewählt = Anzahl selektierter Werte.
- RadioList: Einträge = Anzahl Inputs der Gruppe; ausgewählt = Anzahl `:checked`.
- ComboBox (native `<select>`): Einträge = Anzahl `option`; ausgewählt = Anzahl selektierter Optionen (i. d. R. 0/1). Bei input‑basierten Custom‑Combos liefert die Basis für ListCount derzeit `NotImplemented`; `SelectedCount` ist 0/1 abhängig vom Eingabewert.
- TreeView: Projektspezifisch (z. B. Blätter zählen). Eigene Widgets können die Zähl‑Methoden überschreiben.

---

## Beispiele (Robot Framework)

```
*** Settings ***
Library    okw4robot.keywords.list_keywords.ListKeywords    WITH NAME    LST

*** Test Cases ***
Listen und Auswahl zählen
    SelectWindow   WidgetsDemo
    # Combo (native <select>)
    LST.VerifyListCount        Geschlecht       4
    LST.VerifySelectedCount    Geschlecht       0

    # Radio‑Gruppen
    LST.VerifyListCount        Zahlungsmethode  3
    LST.VerifySelectedCount    Zahlungsmethode  0
    Select                     Zahlungsmethode  paypal
    LST.VerifySelectedCount    Zahlungsmethode  1
```

---

## Timeouts

- `${OKW_TIMEOUT_VERIFY_LIST}`: Default 2s. Zahl oder Robot‑Zeitstring möglich (z. B. `1.5s`).
- `${OKW_POLL_VERIFY}`: Poll‑Intervall, Default 0.1s.

---

## Implementierung

- Keywords rufen am Widget auf:
  - `okw_get_list_count()`
  - `okw_get_selected_count()`
- Basisklasse: `src/okw4robot/widgets/base/base_widget.py` (Stubs). Widgets überschreiben diese Methoden objektspezifisch.
- Beispiel‑Widgets:
  - ListBox: `src/okw4robot/widgets/common/listbox.py`
  - RadioList: `src/okw4robot/widgets/common/radiolist.py`
  - ComboBox: `src/okw4robot/widgets/common/combobox.py`
