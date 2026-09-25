# Prompt‑Vorlagen für OKW4Robot (Deutsch)

Kurze, praxistaugliche Vorlagen, um eine KI anzuweisen, Robot‑Tests mit OKW4Robot zu erzeugen.

---

## Vorlage A: Kompaktauftrag

Erzeuge Robot‑Framework‑Testfälle mit OKW4Robot. Anforderungen:
- Nutze nur OKW4Robot‑Keywords (Host/App, Widget‑Aktionen, Verify‑Keywords inkl. WCM/REGX, Memorize/Log, Fokus/Existenz).
- Initialisiere jeden Test mit `StartHost`, `StartApp`, `SelectWindow`. Beende optional mit `StopApp`, `StopHost`.
- Verwende `$IGNORE` (oder `${IGNORE}`) für optionale/irrelevante Felder; `${OKW_IGNORE_EMPTY}` kann leerwerte global ignorieren.
- Setze Zeitouts bei Bedarf mit `SetOKWParameter`.
- Nutze `…WCM` für Wildcards (`*`, `?`) und `…REGX` für komplexe Regex.
- Verwende für Existenz/Focus ausschließlich `YES` oder `NO`.

Gegeben:
- Ziel(e): <kurz beschreiben>
- Fenster/Widgets: <Fenstername und relevante Widget‑Namen>
- Testdaten: <Werte, erwartete Texte/Muster>

Gib nur gültige `.robot`‑Schritte aus (ohne Erklärtext).

---

## Vorlage B: Strukturiert mit Platzhaltern

Erzeuge einen Robot‑Test mit OKW4Robot basierend auf:

- Host: {HOST_NAME}
- App‑Konfiguration: {APP_CONFIG_PATH}
- Fenster: {WINDOW_NAME}
- Testschritte (Aktionen):
  - {ACTION_1}
  - {ACTION_2}
  - …
- Erwartungen:
  - {VERIFY_1}
  - {VERIFY_2}

Regeln:
- Nutze nur OKW4Robot‑Keywords: Start/Select/Stop, ClickOn, DoubleClickOn, SetValue, Select, TypeKey, VerifyExist, VerifyValue/WCM/REGX, Label/Caption/Tooltip/Placeholder/Attribute‑Verifies (inkl. WCM/REGX), SetFocus, VerifyHasFocus, Memorize*, Log*.
- Ignoriere Eingaben/Prüfungen mit `$IGNORE` (oder `${IGNORE}`); lösche Felder mit `$DELETE` via `TypeKey`.
- Setze optionale Timeouts mit `SetOKWParameter`.
- Verwende nur `YES|NO` bei Existenz/Fokus.

Ausgabeformat: Nur `.robot`‑Schritte, z. B.:

```
StartHost         {HOST_NAME}
StartApp          {APP_CONFIG_PATH}
SelectWindow      {WINDOW_NAME}
{ACTION_1}
{ACTION_2}
{VERIFY_1}
{VERIFY_2}
StopApp
StopHost
```

---

## Vorlage C: Beispiel mit Testdaten

Erzeuge einen Test „Registrierung erfolgreich“. Daten:
- Fenster: `Signup`
- Felder: `Vorname=Anna`, `Nachname=Meyer`, `E‑Mail=anna@example.org`, `Passwort=$DELETE` → danach `SetValue Passwort geheim123`.
- Aktion: `ClickOn  Registrieren`
- Erwartungen: `VerifyExist  Fehlermeldung  NO`, `VerifyLabelWCM  Begrüßung  Willkommen, *`.

Nur `.robot` ausgeben.

