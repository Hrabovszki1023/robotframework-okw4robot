# OKW4Robot Keywords & Notation für KI‑Prompts

Ziel: Dieses Dokument beschreibt die OKW4Robot‑Schlüsselwörter und deren Notation so kompakt, dass eine KI daraus Robot‑Framework‑Testfälle generieren kann.

---

## Grundprinzipien

- Tests verwenden Robot Framework. Ein Schritt ist ein Keyword mit Argumenten, getrennt durch mindestens zwei Spaces.
- Vor Widget‑Aktionen immer die Umgebung initialisieren:
  1) `StartHost <HostKonfig>` → Adapter starten
  2) `StartApp <AppKonfig>` → App‑/Fenster‑Modell laden
  3) `SelectWindow <FensterName>` → Kontext setzen
- Widget‑Namen beziehen sich auf das aktuell gewählte Fenster im YAML‑Modell. Keine direkten Locator‑Strings im Test schreiben.
- Am Ende optional: `StopApp`, `StopHost`.

---

## Globale Regeln & Tokens

- `$IGNORE` bzw. `${IGNORE}`: Eingaben/Erwartungen überspringen (No‑Op). Empfehlung: `${IGNORE}` als Variable definieren, die auf den Literal `$IGNORE` zeigt.
- `${OKW_IGNORE_EMPTY}`: Wenn `YES|TRUE|1`, werden leere/Whitespace‑Werte wie `$IGNORE` behandelt.
- `$DELETE` (nur `TypeKey`): Feldinhalt löschen (Adapter `clear_text`, sonst `CTRL+A` + `DELETE`).
- `YES|NO`: Erwartungswerte für `VerifyExist` und `VerifyHasFocus`.
- Zeitverhalten (Sekunden oder Robot‑Zeitstrings wie `10s`):
  - `${OKW_TIMEOUT_VERIFY_VALUE}`
  - `${OKW_TIMEOUT_VERIFY_TOOLTIP}`
  - `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}`
  - `${OKW_TIMEOUT_VERIFY_LABEL}`
  - `${OKW_TIMEOUT_VERIFY_CAPTION}`
  - `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}`
  - Setzen per `SetOKWParameter  TimeOutVerify<Value|Tooltip|Placeholder|Label|Caption|Attribute>  <Wert>`

---

## Keyword‑Gruppen (Signaturen & Semantik)

- Host/App
  - `StartHost    <HostKonfig>`: Lädt Host‑YAML, instanziiert Adapter und setzt Host‑Kontext.
  - `SelectHost   <AdapterName>`: Verifiziert, dass der aktive Adapter dem Namen entspricht.
  - `StopHost`: Beendet den aktiven Host.
  - `StartApp     <AppKonfig>`: Lädt App‑YAML, setzt App‑/Fenster‑Modell.
  - `SelectWindow <FensterName>`: Wählt Fenster/Widget‑Kontext aus dem App‑Modell.
  - `StopApp`: Setzt App‑Kontext zurück.

- Widget‑Aktionen
  - `ClickOn      <Name>`: Klickt Widget.
  - `DoubleClickOn <Name>`: Doppelklickt Widget.
  - `SetValue     <Name>  <Wert>`: Setzt Wert. Ignoriert bei `$IGNORE`/leer (wenn aktiviert).
  - `Select       <Name>  <Wert>`: Wählt Eintrag. Ignoriert bei `$IGNORE`/leer (wenn aktiviert).
  - `TypeKey      <Name>  <Taste|$DELETE>`: Tippt Taste/Text oder löscht Inhalt via `$DELETE`. Ignoriert bei `$IGNORE`/leer (wenn aktiviert).

- Verifikation von Werten
  - `VerifyValue       <Name>  <Soll>`: Exakter Vergleich; wartet bis Timeout.
  - `VerifyValueWCM    <Name>  <Soll>`: Wildcard‑Match mit `*` und `?`, voller Match (an den Rändern geankert).
  - `VerifyValueREGX   <Name>  <Regex>`: Regex‑Suche (Python‑Regex, nicht zwingend geankert).

- Existenz, Fokus, Logging, Merken
  - `VerifyExist     <Name>  YES|NO`: Existenzprüfung.
  - `SetFocus        <Name>`: Fokus auf Widget setzen.
  - `VerifyHasFocus  <Name>  YES|NO`: Fokusprüfung.
  - `LogValue        <Name>`: Wert in die Logausgabe schreiben.
  - `HasValue        <Name>`: Prüft/erfragt, ob ein Wert vorhanden ist (Widget‑spezifisch).
  - `MemorizeValue   <Name>  <Variable>`: Wert in Robot‑Variable speichern (mit oder ohne `${}` möglich).

- Label
  - `VerifyLabel        <Name>  <Soll>`
  - `VerifyLabelWCM     <Name>  <Soll>`
  - `VerifyLabelREGX    <Name>  <Regex>`
  - `MemorizeLabel      <Name>  <Variable>`
  - `LogLabel           <Name>`

- Caption (sichtbarer Element‑Text)
  - `VerifyCaption      <Name>  <Soll>`
  - `VerifyCaptionWCM   <Name>  <Soll>`
  - `VerifyCaptionREGX  <Name>  <Regex>`
  - `MemorizeCaption    <Name>  <Variable>`
  - `LogCaption         <Name>`

- Tooltip (`title`/`aria-label`)
  - `VerifyTooltip      <Name>  <Soll>`
  - `VerifyTooltipWCM   <Name>  <Soll>`
  - `VerifyTooltipREGX  <Name>  <Regex>`
  - `MemorizeTooltip    <Name>  <Variable>`
  - `LogTooltip         <Name>`

- Placeholder (falls vom Widget unterstützt)
  - `VerifyPlaceholder      <Name>  <Soll>`
  - `VerifyPlaceholderWCM   <Name>  <Soll>`
  - `VerifyPlaceholderREGX  <Name>  <Regex>`

- Attribute (beliebiger Attributname)
  - `VerifyAttribute      <Name>  <Attribut>  <Soll>`
  - `VerifyAttributeWCM   <Name>  <Attribut>  <Soll>`
  - `VerifyAttributeREGX  <Name>  <Attribut>  <Regex>`
  - `MemorizeAttribute    <Name>  <Attribut>  <Variable>`
  - `LogAttribute         <Name>  <Attribut>`

- Java‑Swing (Adapter‑spezifisch)
  - `Export Object Tree To File    <Pfad=objecttree.yaml>`: GUI‑Objektbaum als YAML exportieren.
  - `Wait Until JavaRPC Server Is Ready  <timeout=10>  <interval=1>`: Warten bis Server antwortet.

Hinweise zu WCM/REGX:
- WCM: Muster wird geankert (`^…$`), `*` → `.*`, `?` → `.`; mehrzeilig möglich.
- REGX: Python‑Regex, es wird per Suche geprüft (kein implizites `^…$`).

---

## Prompt‑Hinweise für die Testfall‑Generierung

- Nutze ausschließlich die oben gelisteten Keywords; keine Low‑Level‑Selenium‑Aufrufe.
- Beginne Tests immer mit `StartHost`, `StartApp`, `SelectWindow` im korrekten Kontext.
- Verwende `$IGNORE` (oder `${IGNORE}`) bei optionalen/irrelevanten Eingaben und Erwartungen.
- Nutze `...WCM` für grobe/robuste Prüfungen und `...REGX` für komplexe Muster.
- Speichere dynamische Werte mit `Memorize*` in Robot‑Variablen und referenziere sie später.
- Für Fokus/Existenz nur `YES|NO` verwenden.

---

## Minimales Beispiel (Robot Framework)

```robotframework
*** Settings ***
Library    okw4robot.keywords.host.HostKeywords
Library    okw4robot.keywords.app.AppKeywords
Library    okw4robot.keywords.widget_keywords.WidgetKeywords
Library    okw4robot.keywords.label_keywords.LabelKeywords

*** Variables ***
${IGNORE}    $IGNORE

*** Test Cases ***
Login Prüfen (Beispiel)
    StartHost         SeleniumWeb
    StartApp          demo/app.yaml
    SelectWindow      Login
    SetValue           Benutzername      alice
    TypeKey            Passwort          $DELETE
    SetValue           Passwort          geheim
    ClickOn            Anmelden
    VerifyExist        FehlerHinweis     NO
    VerifyLabelWCM     Begrüßung         Hallo, *
    MemorizeLabel      Begrüßung         ${GREETING}
    LogValue           Begrüßung
    StopApp
    StopHost
```

