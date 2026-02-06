# Tooltip-Keywords

Diese SchlÃ¼sselwÃ¶rter lesen den Tooltip eines Widgets (HTML-Attribut `title`, Fallback `aria-label`) und prÃ¼fen, warten, merken oder loggen den Wert.

---

## Keywords (Library: `okw4robot.keywords.tooltip_keywords.TooltipKeywords`)

- `VerifyTooltip    <Name>    <Soll>`: exakter Vergleich
- `VerifyTooltipWCM <Name>    <Soll>`: Wildcard-Match (`*`, `?`), mehrzeilig mÃ¶glich
- `VerifyTooltipREGX <Name>   <Regex>`: Regex-Match
- `MemorizeTooltip  <Name>    <Variable>`: speichert Tooltip in `${Variable}`
- `LogTooltip       <Name>`: loggt den aktuellen Tooltip

Ignore-Regel: Leere Werte (optional via `${OKW_IGNORE_EMPTY}=YES`) oder das Token `$IGNORE` fÃ¼hren bei Verify*/Wait* zu einem No-Op.

---

## UnterstÃ¼tzte Widgets

Tooltip (title/aria-label) kann auf praktisch allen HTML-Elementen vorkommen. Die Keywords funktionieren daher fÃ¼r alle Widgets, sofern ein Locator vorhanden ist.

---

## Beispiele (Robot Framework)

```robotframework
*** Settings ***
Library    okw4robot.keywords.tooltip_keywords.TooltipKeywords    WITH NAME    TT

*** Test Cases ***
Tooltip PrÃ¼fen
    Select Window         WidgetsDemo
    VerifyTooltip         Name         Hinweis: Nachname eingeben
    VerifyTooltipWCM      Vorname      Hinweis: *
    VerifyTooltipREGX     OK           ^Klick.*


Merken Und Nutzen
    Select Window         WidgetsDemo
    MemorizeTooltip       OK           OkTip
    LogTooltip            OK
    # Verwendung: ${OkTip}
```

---

## Implementierung

- Keywords: `src/okw4robot/keywords/tooltip_keywords.py`
- Attributzugriff: `src/okw4robot/adapters/selenium_web.py#get_attribute` (nutzt WebElement.get_attribute)

---

## Hinweis zu Regex in Robot

Backslashes werden in Robot‑Tabellen oft als Escape interpretiert. Verwende z. B. `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^Klick\\s+hier$`). Gilt für alle REGX‑Varianten.

