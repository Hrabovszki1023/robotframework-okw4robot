# Label-Keywords (sichtbare Beschriftung)

Diese Keywords prüfen/merken/loggen die sichtbare Beschriftung (Label/Caption) eines Widgets.

Semantik:
- Label = sichtbarer Beschriftungstext eines Controls.
- Für Eingabefelder (TextField, MultilineField, ComboBox) ist Label die Feldbeschriftung (z. B. `<label for=...>`), nicht der Feldinhalt (dafür `VerifyValue*`).
- Für Button/Link/Label ist Label der eigene sichtbare Text.
- Für CheckBox/Radio: der zugehörige Label‑Text („AGB akzeptieren“, „PayPal“ …).

---

## Keywords (Library: `okw4robot.keywords.label_keywords.LabelKeywords`)

- `VerifyLabel      <Name>    <Soll>`: wartet bis exakter Match passt (Default‑Timeout `${OKW_TIMEOUT_VERIFY_LABEL}` = 10)
- `VerifyLabelWCM   <Name>    <Soll>`: wartet bis Wildcard‑Match (`*`, `?`, DOTALL) passt
- `VerifyLabelREGX  <Name>    <Regex>`: wartet bis Regex‑Match passt
- `MemorizeLabel    <Name>    <Variable>`: speichert den Label‑Text in `${Variable}`
- `LogLabel         <Name>`: loggt den Label‑Text

Ignore‑Regel: `$IGNORE` (und optional leere Werte via `${OKW_IGNORE_EMPTY}=YES`) → No‑Op bei Verify*.

---

## Auflösung der Beschriftung

Heuristik:
1. `aria-labelledby` → Texte der referenzierten IDs (verkettet)
2. `<label for="id">…</label>` → Text
3. `aria-label` → Wert
4. Fallback: eigener sichtbarer Text des Elements

---

## Beispiele

```robotframework
*** Settings ***
Library    okw4robot.keywords.label_keywords.LabelKeywords    WITH NAME    LAB

*** Test Cases ***
Beschriftung Prüfen
    Select Window     WidgetsDemo
    VerifyLabel       Name       Name
    VerifyLabelWCM    Verheiratet    *heirat*
    VerifyLabelREGX   Zahlungsmethode    ^Zahlung

Beschriftung Merken
    Select Window     WidgetsDemo
    MemorizeLabel     OK         OkLabel
    LogLabel          OK
```

---

## Timeouts

- `${OKW_TIMEOUT_VERIFY_LABEL}`: Default 10 (Sekunden). Als Zahl oder Robot‑Zeitstring setzbar.
- Setzen per Keyword: `SetOKWParameter  TimeOutVerifyLabel  15s`
- Alternativ in `*** Variables ***`:

```robotframework
${OKW_TIMEOUT_VERIFY_LABEL}    15s
```

---

## Hinweis zu Regex in Robot

Backslashes werden in Robot‑Tabellen häufig als Escape interpretiert. Verwende nach Möglichkeit Klassen wie `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^Start\\d+$`). Das gilt für alle REGX‑Varianten der Verify‑Keywords.
