# Attribute-Keywords (beliebige HTML-Attribute)

Diese Keywords lesen ein beliebiges Attribut eines Widgets aus und prüfen/merken/loggen es. Die Widget-Auswahl erfolgt über den abstrakten Namen (YAML‑Modell), das Attribut wird als zweiter Parameter angegeben.

---

## Keywords (Library: `okw4robot.keywords.attribute_keywords.AttributeKeywords`)

- `VerifyAttribute      <Name>    <Attribut>   <Soll>`: wartet bis Attribut exakt `<Soll>` ist (Default‑Timeout `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` = 10)
- `VerifyAttributeWCM   <Name>    <Attribut>   <Soll>`: wartet bis Wildcard‑Match (`*`, `?`, DOTALL) passt
- `VerifyAttributeREGX  <Name>    <Attribut>   <Regex>`: wartet bis Regex‑Match passt
- `MemorizeAttribute    <Name>    <Attribut>   <Variable>`: speichert den Attributwert in `${Variable}`
- `LogAttribute         <Name>    <Attribut>`: loggt den Attributwert

Ignore‑Regel: `$IGNORE` (und optional leere Werte via `${OKW_IGNORE_EMPTY}=YES`) → No‑Op bei Verify* (bezieht sich auf den Sollwert).

---

## Beispiele

```robotframework
*** Settings ***
Library    okw4robot.keywords.attribute_keywords.AttributeKeywords    WITH NAME    ATTR

*** Test Cases ***
Attribute Prüfen
    Select Window        WidgetsDemo
    ATTR.VerifyAttribute       Name        placeholder    Nachname
    ATTR.VerifyAttributeWCM    Vorname     placeholder    *name*
    ATTR.VerifyAttributeREGX   OK          data-state     ^(idle|ready)$

Attribute Merken/Loggen
    Select Window        WidgetsDemo
    ATTR.MemorizeAttribute   OK    data-state    BtnState
    ATTR.LogAttribute        OK    data-state
```

---

## Implementierung

- Keywords: `src/okw4robot/keywords/attribute_keywords.py`
- Adapterzugriff: `adapter.get_attribute(locator, name)` (Selenium: WebElement.get_attribute)

---

## Hinweis zu Regex in Robot

In Robot‑Tabellen können Backslashes als Escape behandelt werden. Nutze besser Klassen wie `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^(idle|ready)\\s*\d*$`). Das betrifft alle REGX‑Varianten.
