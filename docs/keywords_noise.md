# Schlüsselwort: OnFailNOISE

## Zweck

`OnFailNOISE` klassifiziert Fehler in Vorbereitungsphasen automatisch als
**NOISE** — also als Infrastruktur- oder Umgebungsprobleme, nicht als
Defekte im System under Test (SUT).

Robot Framework kennt nur PASS und FAIL. `OnFailNOISE` nutzt ein Prefix
in der Fehlermeldung (`[N]` vs. `[X]`), um Failures zu unterscheiden:

| Prefix | Bedeutung | Aktion |
|--------|-----------|--------|
| `[N]` | **NOISE** — Fehler in Vorbereitungsphase | Umgebungsproblem. Nicht das SUT. |
| `[X]` | **FAIL** — Fehler in Test-/Verifikationsphase | Möglicher SUT-Defekt. Analyse nötig. |

## 5-Phasen-Modell

Jeder Testfall folgt einem 5-Phasen-Aufbau:

| Phase | Name | Zweck | Fehler = |
|-------|------|-------|----------|
| 1 | Reset | Anwendung/Umgebung in definierten Zustand bringen | **[N]** NOISE |
| 2 | Umgebungsvorbereitung | Testdaten, Konfigurationen vorbereiten | **[N]** NOISE |
| 3 | Navigation | Zum Fenster/Zustand unter Test navigieren | **[N]** NOISE |
| 4 | Testaktion | Eigentliche Testaktion ausfuehren | **[X]** FAIL |
| 5 | Verifikation | Erwartetes Ergebnis pruefen | **[X]** FAIL |

## Syntax

```
OnFailNOISE    <Keyword>    [Parameter1]    [Parameter2]    ...
```

`OnFailNOISE` nimmt ein beliebiges Keyword samt Parametern entgegen,
fuehrt es aus, und faengt bei Fehler die Exception ab. Die Fehlermeldung
wird mit `[N]` Prefix neu geworfen. Zusaetzlich wird der Tag `NOISE`
auf den Testfall gesetzt.

## Elementare und abstrakte Schluesselwoerter

`OnFailNOISE` funktioniert mit **jedem** Keyword — egal ob elementar
(z.B. `SelectWindow`, `SetValue`) oder abstrakt (ein selbst definiertes
Keyword, das intern weitere Keywords aufruft).

Die NOISE-Klassifizierung wird auf **Testfall-Ebene** bestimmt, nicht
im Keyword selbst. Wenn ein abstraktes Keyword wie `Login` intern
`SelectWindow`, `SetValue` und `ClickOn` aufruft und eines davon
fehlschlaegt, steigt die Exception nach oben bis zu `OnFailNOISE`
und wird dort als `[N]` klassifiziert.

Das bedeutet: Dasselbe Keyword kann in einem Testfall als NOISE gelten
(Vorbereitung) und in einem anderen als FAIL (Testaktion) — die
Entscheidung trifft der Testfall, nicht das Keyword.

## Beispiele

### Elementare Keywords

```robotframework
*** Test Cases ***
Kunde Anlegen
    # Phase 1-3: Vorbereitung — Fehler = NOISE
    OnFailNOISE    ResetApp
    OnFailNOISE    SelectWindow    Hauptfenster
    OnFailNOISE    NavigateTo       Kundenverwaltung

    # Phase 4-5: Test & Verifikation — Fehler = FAIL [X]
    SetValue       Kundenname    Mueller
    ClickOn        Speichern
    VerifyValue    Status        Gespeichert
```

### Abstrakte Keywords

```robotframework
*** Keywords ***
Login
    [Arguments]    ${user}    ${password}
    SelectWindow    LoginDialog
    SetValue        Benutzer    ${user}
    SetValue        Passwort    ${password}
    ClickOn         Anmelden

*** Test Cases ***
Kunde Anlegen Nach Login
    # Phase 1-3: Login ist Vorbereitung — komplett NOISE
    OnFailNOISE    Login    ${AdminUser}    ${AdminPasswort}
    OnFailNOISE    SelectWindow    Kundenverwaltung

    # Phase 4-5: Test & Verifikation — FAIL [X]
    SetValue       Kundenname    Mueller
    VerifyValue    Status        Gespeichert

Login Pruefung
    # Hier ist Login die eigentliche Testaktion — FAIL [X]
    Login          ${TestUser}    ${TestPasswort}
    VerifyValue    Status         Angemeldet
```

Im ersten Testfall ist `Login` Vorbereitung (NOISE). Im zweiten ist
`Login` selbst der Test (FAIL). Dasselbe Keyword — unterschiedliche
Klassifizierung, gesteuert auf Testfall-Ebene.

## Fehlermeldungen

Bei einem Fehler in Phase 1-3 (mit `OnFailNOISE`):
```
FAIL: [N] SelectWindow fehlgeschlagen: Fenster 'Hauptfenster' nicht gefunden
```

Bei einem Fehler in Phase 4-5 (ohne Wrapper):
```
FAIL: [X] VerifyValue: erwartet 'Gespeichert', ist 'Entwurf'
```

## OnFailIgnoreNOISE

`OnFailIgnoreNOISE` ist die „stumme" Variante von `OnFailNOISE`. Bei einem
Fehler wird die Exception **nicht** weitergeworfen — der Testfall laeuft
weiter. Der Fehler wird als `[N][IGNORED]` geloggt.

### Syntax

```
OnFailIgnoreNOISE    <Keyword>    [Parameter1]    [Parameter2]    ...
```

### Einsatzzweck

Fuer **optionale Vorbereitungsschritte**, die scheitern duerfen, ohne den
Testfall abzubrechen. Typische Beispiele:

- Werbung/Ads entfernen (Seite hat moeglicherweise keine Ads)
- Cookie-Banner schliessen (Banner erscheint nur beim ersten Besuch)
- Optionale UI-Elemente wegklicken (Willkommensdialog, Newsletter-Popup)

### Unterschied zu OnFailNOISE

| Keyword | Bei Fehler | Tag gesetzt? | Test laeuft weiter? |
|---------|-----------|--------------|---------------------|
| `OnFailNOISE` | `[N]` Prefix, Exception wird geworfen | NOISE | Nein — Testfall schlaegt fehl |
| `OnFailIgnoreNOISE` | `[N][IGNORED]` wird geloggt | — | Ja — Test laeuft weiter |

### Beispiel

```robotframework
*** Keywords ***
Login Seite Oeffnen
    OnFailNOISE          StartApp       MyAppChrome

    OnFailNOISE          SelectWindow   Chrome
    OnFailNOISE          SetValue       URL    ${URL}
    OnFailIgnoreNOISE    RemoveAds
    OnFailNOISE          VerifyWindowExists    LoginPage    YES
```

`RemoveAds` entfernt Werbeeinblendungen per JavaScript. Wenn die Seite
keine Ads hat, schlaegt das Keyword fehl — aber `OnFailIgnoreNOISE`
faengt den Fehler ab und der Test geht weiter.

### Wann OnFailNOISE, wann OnFailIgnoreNOISE?

- **OnFailNOISE**: Der Schritt *muss* gelingen, damit der Test Sinn hat
  (z.B. `StartApp`, `SelectWindow`, `SetValue URL`). Fehler = NOISE, aber
  Test wird abgebrochen.
- **OnFailIgnoreNOISE**: Der Schritt ist *optional* (z.B. Ad-Blocker,
  Cookie-Banner). Fehler wird ignoriert, Test laeuft weiter.

---

## Einsatz ist optional

`OnFailNOISE` und `OnFailIgnoreNOISE` sind optionale Werkzeuge. Tester die
das NOISE-vs-Signal-Konzept verstanden haben, koennen sie einsetzen. Ohne
diese Wrapper bleiben alle Fehler standard `[X]` FAILs — es aendert sich
nichts am bisherigen Verhalten.

## Zusammenspiel mit OKW-Tokens

| Token | Verhalten mit OnFailNOISE |
|-------|---------------------------|
| `$IGNORE` | Keyword wird zum No-Op (PASS). `OnFailNOISE` hat nichts zu fangen. |
| `$EMPTY` / `$DELETE` | Tokens werden im gewrappten Keyword aufgeloest. `OnFailNOISE` ist transparent. |

## Zusammenspiel mit Timeouts

Gewrappte Keywords nutzen weiterhin ihre eigenen Timeouts (z.B.
`${OKW_TIMEOUT_VERIFY_VALUE}`). `OnFailNOISE` faengt erst den
finalen Timeout-Fehler ab.

## Filtern und Reporting

Der `[N]` / `[X]` Prefix in der Fehlermeldung erlaubt Filtern mit
Standard-Werkzeugen:

- **Robot Framework Rebot**: `rebot --exclude NOISE output.xml`
- **output.xml**: XPath auf `<msg>`-Elemente mit `[N]` oder `[X]`
- **Kommandozeile**: `grep "\[N\]"` / `grep "\[X\]"` auf Log-Ausgaben

## Nutzen

Nur `[X]`-Fehler muessen sofort untersucht werden. `[N]`-Fehler koennen
gefiltert, gruppiert und separat behandelt werden. Das reduziert den
Analyseaufwand und fokussiert das Team auf relevante Fehler.
