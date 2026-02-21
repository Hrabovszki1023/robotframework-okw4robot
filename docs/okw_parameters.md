# OKW Parameter und Timeouts

OKW verwendet konfigurierbare Timeout- und Steuerungsparameter, um das Verhalten
von Verify-Keywords, Synchronisation und Ignore-Regeln anzupassen. Diese Seite
beschreibt **wann**, **warum** und **wie** diese Parameter gesetzt werden.

---

## Warum Timeouts anpassen?

OKW-Verify-Keywords (`VerifyValue`, `VerifyExist`, `VerifyTooltip`, ...) arbeiten
**nicht** mit einem einzelnen Abgleich. Stattdessen laufen sie in einer
**Polling-Schleife**: Der aktuelle Wert wird wiederholt gelesen und mit dem
Sollwert verglichen, bis er passt oder das Timeout ablaeuft.

```
Ablauf (vereinfacht):

    VerifyValue "Benutzer" "Max"
         │
         ▼
    ┌──────────────────────────┐
    │  Wert lesen (okw_get_value)  │◄─────┐
    │  Aktuell: ""                 │      │
    │  Soll:    "Max"              │      │  Poll-Intervall
    │  Match?   NEIN               │      │  (0.1s default)
    └──────────┬───────────────────┘      │
               │                          │
               ▼                          │
         Timeout erreicht? ───NEIN───────►┘
               │
              JA
               ▼
         FAIL: "Erwartet 'Max', gelesen ''"
```

Die **Standard-Timeouts** (10 Sekunden fuer Werte, 2 Sekunden fuer Zustaende)
passen fuer die meisten Anwendungen. In bestimmten Situationen muessen sie
angepasst werden:

| Situation | Empfehlung |
|-----------|------------|
| **Langsame Applikation** (z.B. komplexe Berechnungen, Backend-Calls) | Timeout erhoehen (`20s`, `30s`) |
| **Schnelle Unit-/Widget-Tests** (lokale HTML-Seite, kein Backend) | Timeout reduzieren (`3s`, `5s`) fuer schnelleres Feedback |
| **CI/CD-Umgebung** (langsamere VMs, parallele Last) | Timeout erhoehen (`15s`–`30s`) |
| **Asynchrones Laden** (AJAX, WebSocket-Updates) | Timeout erhoehen + ggf. Poll-Intervall anpassen |
| **Einzelnes traege Element** (z.B. Dashboard-Widget) | Per YAML-Instanz ueberschreiben |

---

## Drei Wege zum Setzen

OKW bietet drei Wege, um Parameter zu setzen. Sie unterscheiden sich in Reichweite
und Einsatzzweck:

### 1. Variables-Section (statisch, Suite-weit)

Direkt in der Robot-Datei oder in einer Resource-Datei. Gilt fuer die gesamte
Suite und alle importierenden Suites.

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Variables ***
${OKW_TIMEOUT_VERIFY_VALUE}     20
${OKW_TIMEOUT_VERIFY_EXIST}      5
${OKW_POLL_VERIFY}             0.2

*** Test Cases ***
Langsamer Backend-Call
    SetValue     Suchfeld    Roboter
    ClickOn      Suchen
    # VerifyValue wartet jetzt bis zu 20s (statt default 10s)
    VerifyValue  Ergebnis    42 Treffer gefunden
```

**Wann verwenden?** Wenn die gesamte Applikation generell langsamer/schneller ist
und alle Tests einheitlich konfiguriert werden sollen.

### 2. SetOKWParameter-Keyword (dynamisch, zur Laufzeit)

Setzt den Parameter als Suite-Variable zur Laufzeit. Kann im Test Case, in
Suite Setup/Teardown oder in eigenen Keywords verwendet werden.

```robotframework
*** Settings ***
Library       okw_web_selenium.library.OkwWebSeleniumLibrary
Suite Setup   Timeouts fuer CI setzen

*** Keywords ***
Timeouts fuer CI setzen
    SetOKWParameter    TimeOutVerifyValue    30
    SetOKWParameter    TimeOutVerifyExist     5
    SetOKWParameter    PollVerify           0.2

*** Test Cases ***
Login mit langsamem Backend
    SetValue     Benutzer    admin
    SetValue     Passwort    geheim
    ClickOn      Anmelden
    # Wartet bis zu 30s auf das Ergebnis
    VerifyValue  Status      Willkommen, admin!
```

**Wann verwenden?** Wenn Timeouts kontextabhaengig gesetzt werden muessen,
z.B. basierend auf Umgebungsvariablen (CI vs. lokal) oder wenn ein einzelner Test
abweichende Werte braucht.

### 3. YAML-Instanz-Konfiguration (pro Widget)

Im Locator-YAML kann fuer ein einzelnes Widget ein individuelles Timeout gesetzt
werden. Dies ist der praeziseste Weg und ueberschreibt alle globalen Einstellungen.

```yaml
# locators/Dashboard.yaml
Dashboard:
  __self__:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="dashboard"]' }

  # Dieses Widget laedt immer langsam (komplexe Aggregation)
  Umsatz Monat:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="revenue-month"]' }
    wait:
      write:
        timeout: 30
      read:
        timeout: 30

  # Standard-Widget, braucht keine Anpassung
  Seitenname:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="page-title"]' }
```

**Wann verwenden?** Wenn ein einzelnes GUI-Objekt abweichendes Verhalten zeigt und
die globalen Timeouts fuer den Rest der Applikation passen.

---

## Praxisbeispiele

### Beispiel 1: CI-Umgebung mit erhoehten Timeouts

```robotframework
*** Settings ***
Library       okw_web_selenium.library.OkwWebSeleniumLibrary
Suite Setup   CI Timeouts konfigurieren

*** Keywords ***
CI Timeouts konfigurieren
    ${ci}=    Get Environment Variable    CI    default=false
    IF    '${ci}' == 'true'
        SetOKWParameter    TimeOutVerifyValue    30
        SetOKWParameter    TimeOutVerifyExist    10
        Log    CI-Modus: Timeouts erhoeht
    END
```

### Beispiel 2: Schnelle lokale Tests

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Variables ***
# Lokale HTML-Seite, keine Netzwerklatenz
${OKW_TIMEOUT_VERIFY_VALUE}      3
${OKW_TIMEOUT_VERIFY_EXIST}      1
${OKW_POLL_VERIFY}             0.05

*** Test Cases ***
TextField Eingabe
    StartApp    WidgetsDemo
    SetValue     Name    Max Mustermann
    VerifyValue  Name    Max Mustermann
    StopApp
```

### Beispiel 3: Einzelnes Timeout im Test aendern

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Test Cases ***
Report-Generierung abwarten
    SetValue     Von-Datum     01.01.2025
    SetValue     Bis-Datum     31.12.2025
    ClickOn      Report erstellen
    # Report-Generierung dauert bis zu 60 Sekunden
    SetOKWParameter    TimeOutVerifyValue    60
    VerifyValue  Status    Report fertig
    # Zuruecksetzen auf Normalwert
    SetOKWParameter    TimeOutVerifyValue    10
```

### Beispiel 4: Resource-Datei fuer Projektstandards

```robotframework
# resources/projekt_timeouts.resource
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Variables ***
${OKW_TIMEOUT_VERIFY_VALUE}          15
${OKW_TIMEOUT_VERIFY_PLACEHOLDER}    10
${OKW_TIMEOUT_VERIFY_TOOLTIP}        10
${OKW_TIMEOUT_VERIFY_EXIST}           5
${OKW_TIMEOUT_VERIFY_VISIBLE}         5
${OKW_POLL_VERIFY}                   0.1
```

```robotframework
# tests/MeineTests.robot
*** Settings ***
Resource    ../resources/projekt_timeouts.resource

*** Test Cases ***
Login Test
    StartApp    MeineApp
    SetValue    Benutzer    testuser
    ...
```

---

## Parameter-Referenz

### Verify-Timeouts (Wert-Pruefungen)

| Variable | Default | Betroffene Keywords |
|----------|---------|---------------------|
| `${OKW_TIMEOUT_VERIFY_VALUE}` | 10 | VerifyValue, VerifyValueWCM, VerifyValueREGX |
| `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}` | 10 | VerifyPlaceholder, VerifyPlaceholderWCM, VerifyPlaceholderREGX |
| `${OKW_TIMEOUT_VERIFY_TOOLTIP}` | 10 | VerifyTooltip, VerifyTooltipWCM, VerifyTooltipREGX |
| `${OKW_TIMEOUT_VERIFY_LABEL}` | 10 | VerifyLabel, VerifyLabelWCM, VerifyLabelREGX |
| `${OKW_TIMEOUT_VERIFY_CAPTION}` | 10 | VerifyCaption, VerifyCaptionWCM, VerifyCaptionREGX |
| `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` | 10 | VerifyAttribute |

### Verify-Timeouts (Zustands-Pruefungen)

| Variable | Default | Betroffene Keywords |
|----------|---------|---------------------|
| `${OKW_TIMEOUT_VERIFY_EXIST}` | 2.0 | VerifyExist |
| `${OKW_TIMEOUT_VERIFY_VISIBLE}` | 2.0 | VerifyVisible |
| `${OKW_TIMEOUT_VERIFY_ENABLED}` | 2.0 | VerifyEnabled |
| `${OKW_TIMEOUT_VERIFY_EDITABLE}` | 2.0 | VerifyEditable |
| `${OKW_TIMEOUT_VERIFY_FOCUSABLE}` | 2.0 | VerifyFocusable |
| `${OKW_TIMEOUT_VERIFY_CLICKABLE}` | 2.0 | VerifyClickable |
| `${OKW_TIMEOUT_VERIFY_FOCUS}` | 2.0 | VerifyHasFocus |
| `${OKW_TIMEOUT_VERIFY_TABLE}` | 2.0 | VerifyTableCellValue, VerifyTableHeaders |

### Polling und Steuerung

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `${OKW_POLL_VERIFY}` | 0.1 | Polling-Intervall (Sekunden) fuer alle Verify-Schleifen |
| `${OKW_IGNORE_EMPTY}` | NO | Leere Werte global ignorieren (No-Op) fuer Set/Select/TypeKey/Verify* |

### SetOKWParameter-Mapping

Das Keyword `SetOKWParameter` akzeptiert folgende Namen (case-insensitive):

| Name | Setzt Variable |
|------|---------------|
| `TimeOutVerifyValue` | `${OKW_TIMEOUT_VERIFY_VALUE}` |
| `TimeOutVerifyPlaceholder` | `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}` |
| `TimeOutVerifyTooltip` | `${OKW_TIMEOUT_VERIFY_TOOLTIP}` |
| `TimeOutVerifyLabel` | `${OKW_TIMEOUT_VERIFY_LABEL}` |
| `TimeOutVerifyCaption` | `${OKW_TIMEOUT_VERIFY_CAPTION}` |
| `TimeOutVerifyAttribute` | `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` |
| `TimeOutVerifyExist` | `${OKW_TIMEOUT_VERIFY_EXIST}` |
| `TimeOutVerifyVisible` | `${OKW_TIMEOUT_VERIFY_VISIBLE}` |
| `TimeOutVerifyEnabled` | `${OKW_TIMEOUT_VERIFY_ENABLED}` |
| `TimeOutVerifyEditable` | `${OKW_TIMEOUT_VERIFY_EDITABLE}` |
| `TimeOutVerifyFocusable` | `${OKW_TIMEOUT_VERIFY_FOCUSABLE}` |
| `TimeOutVerifyClickable` | `${OKW_TIMEOUT_VERIFY_CLICKABLE}` |
| `TimeOutVerifyFocus` | `${OKW_TIMEOUT_VERIFY_FOCUS}` |
| `TimeOutVerifyTable` | `${OKW_TIMEOUT_VERIFY_TABLE}` |
| `PollVerify` | `${OKW_POLL_VERIFY}` |

### Wertformate

Timeouts akzeptieren:
- **Ganzzahlen**: `10` (Sekunden)
- **Dezimalzahlen**: `2.5` (Sekunden)
- **Robot-Zeitformat**: `10s`, `1 min`, `1 min 30s`, `500 ms`

---

## Zusammenspiel mit Synchronisation

Die Verify-Timeouts steuern die **inhaltliche** Pruefung: „Hat das Element den
richtigen Wert?" Die Sync-Timeouts (dokumentiert in
[synchronization_strategy.md](synchronization_strategy.md)) steuern die
**technische** Vorbedingung: „Ist das Element ueberhaupt da, sichtbar, klickbar?"

```
Ablauf bei VerifyValue:

1. _wait_before("read")     ← Sync-Timeouts (OKW_SYNC_TIMEOUT_READ)
   └── exists? visible?        Stellt sicher, dass das Element bereit ist

2. Verify-Loop               ← Verify-Timeout (OKW_TIMEOUT_VERIFY_VALUE)
   └── Wert lesen, vergleichen, ggf. wiederholen
       bis Match oder Timeout
```

Beide Timeout-Gruppen sind unabhaengig konfigurierbar und addieren sich im
Worst Case.

---

## Ignore-Regel (${OKW_IGNORE_EMPTY})

Steuert, ob leere Werte (`""`, reine Leerzeichen) als „nichts tun" interpretiert
werden. Nuetzlich fuer datengetriebene Tests, bei denen nicht alle Felder in jedem
Datensatz gefuellt werden:

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Variables ***
${OKW_IGNORE_EMPTY}    YES

*** Test Cases ***
Datengetriebener Test
    [Template]    Felder befuellen
    Max       Mustermann    max@test.de
    Anna      ${EMPTY}      anna@test.de

*** Keywords ***
Felder befuellen
    [Arguments]    ${vorname}    ${nachname}    ${email}
    SetValue    Vorname     ${vorname}
    # Bei "Anna" wird SetValue fuer Nachname uebersprungen (No-Op)
    SetValue    Nachname    ${nachname}
    SetValue    Email       ${email}
```

Akzeptierte Werte: `YES`, `NO`, `TRUE`, `FALSE`, `1`, `0`

> **Hinweis:** Der spezielle Wert `$IGNORE` wird **immer** als No-Op behandelt,
> unabhaengig von `${OKW_IGNORE_EMPTY}`.
