# Caption-Keywords (sichtbarer Elementtext)

Diese Keywords prüfen/merken/loggen den sichtbaren Text des Elements selbst (Caption) – z. B. Button‑Text, Link‑Text, Überschrift eines Label‑Widgets. Für Eingabefelder bleibt der Feldinhalt `VerifyValue*`; die Feldbeschriftung liegt bei `VerifyLabel*`.

---

## Keywords (Library: `okw4robot.keywords.caption_keywords.CaptionKeywords`)

- `VerifyCaption      <Name>    <Soll>`: wartet bis exakter Match passt (Default‑Timeout `${OKW_TIMEOUT_VERIFY_CAPTION}` = 10)
- `VerifyCaptionWCM   <Name>    <Soll>`: wartet bis Wildcard‑Match (`*`, `?`, DOTALL) passt
- `VerifyCaptionREGX  <Name>    <Regex>`: wartet bis Regex‑Match passt
- `MemorizeCaption    <Name>    <Variable>`: speichert den Caption‑Text in `${Variable}`
- `LogCaption         <Name>`: loggt den Caption‑Text

Ignore‑Regel: `$IGNORE` (und optional leere Werte via `${OKW_IGNORE_EMPTY}=YES`) → No‑Op bei Verify*.

---

## Abgrenzung

- Caption = eigener sichtbarer Text des Elements (Button/Link/Label etc.)
- Label = Beschriftung eines Controls über `<label for=…>`/`aria-labelledby` (siehe `keywords_label.md`)
- Value = inhaltlicher Wert (z. B. Eingabetext), siehe `VerifyValue*`

---

## Timeouts

- `${OKW_TIMEOUT_VERIFY_CAPTION}`: Default 10 (Sekunden). Als Zahl oder Robot‑Zeitstring setzbar.
- Setzen per Keyword: `SetOKWParameter  TimeOutVerifyCaption  15s`

---

## Hinweis zu Regex in Robot

Backslashes werden in Robot‑Tabellen häufig als Escape interpretiert. Bevorzuge z. B. `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^Titel\\s+\d+$`). Diese Empfehlung gilt für alle REGX‑Varianten.
