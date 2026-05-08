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

## Beispiel

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

## Fehlermeldungen

Bei einem Fehler in Phase 1-3 (mit `OnFailNOISE`):
```
FAIL: [N] SelectWindow fehlgeschlagen: Fenster 'Hauptfenster' nicht gefunden
```

Bei einem Fehler in Phase 4-5 (ohne Wrapper):
```
FAIL: [X] VerifyValue: erwartet 'Gespeichert', ist 'Entwurf'
```

## Einsatz ist optional

`OnFailNOISE` ist ein optionales Werkzeug. Tester die das NOISE-vs-Signal-
Konzept verstanden haben, koennen es einsetzen. Ohne `OnFailNOISE` bleiben
alle Fehler standard `[X]` FAILs — es aendert sich nichts am bisherigen
Verhalten.

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
