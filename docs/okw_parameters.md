# OKW Parameter und Timeouts

OKW verwendet konfigurierbare Timeout- und Steuerungsparameter, um das Verhalten
von Verify-Keywords, Synchronisation und Ignore-Regeln anzupassen. Diese Seite
beschreibt die **fuenf Geltungsbereiche (Scopes)**, in denen Parameter gesetzt
werden koennen, und wie sie sich gegenseitig ueberschreiben.

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

| Situation | Empfehlung | Scope |
|-----------|------------|-------|
| **Langsame Applikation** (komplexe Berechnungen, Backend-Calls) | Timeout erhoehen (`20s`, `30s`) | Projekt |
| **Schnelle Unit-/Widget-Tests** (lokale HTML-Seite, kein Backend) | Timeout reduzieren (`3s`, `5s`) | Projekt |
| **CI/CD-Umgebung** (langsamere VMs, parallele Last) | Timeout erhoehen (`15s`–`30s`) | Ausfuehrung |
| **Asynchrones Laden** (AJAX, WebSocket-Updates) | Timeout + Poll-Intervall anpassen | Projekt / Widget |
| **Einzelnes traege Element** (z.B. Dashboard-Widget) | Per YAML-Instanz ueberschreiben | Widget |
| **Ein Test braucht mehr Zeit** (Report-Generierung, Export) | `SetOKWParameter` im Test | Testfall |
| **Debugging eines einzelnen Tests** | `--variable` auf der Kommandozeile | Ausfuehrung |

---

## Die fuenf Scopes (Override-Kaskade)

Parameter werden in fuenf Geltungsbereichen gesetzt. Jeder engere Scope
ueberschreibt den weiteren:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Global (OKW-Default)         — Hardcodiert in OKW       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  2. Projekt                   — Resource / __init__    │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  3. Widget                 — YAML wait:-Block    │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  4. Testfall            — SetOKWParameter   │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  5. Ausfuehrung     — robot --variable │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Spezifischer Scope gewinnt:  Global < Projekt < Widget < Testfall < Ausfuehrung
```

---

### Scope 1: Global (OKW-Default)

Die in OKW hardcodierten Standardwerte. Sie gelten, wenn kein anderer Scope
einen Parameter ueberschreibt. Es ist nichts zu tun — diese Werte sind immer da.

| Parameter | Default |
|-----------|---------|
| `${OKW_TIMEOUT_VERIFY_VALUE}` | 10 |
| `${OKW_TIMEOUT_VERIFY_EXIST}` | 2.0 |
| `${OKW_POLL_VERIFY}` | 0.1 |
| `${OKW_IGNORE_EMPTY}` | NO |
| ... | (siehe Referenz unten) |

---

### Scope 2: Projekt

Projektweite Einstellungen, die fuer **alle Tests des Projekts** gelten.
Zwei Varianten:

#### a) Resource-Datei (empfohlen)

Eine zentrale Resource-Datei, die von allen Test-Suites importiert wird:

```robotframework
# resources/projekt_timeouts.resource
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
Library     okw_web_selenium.library.OkwWebSeleniumLibrary
Resource    ../resources/projekt_timeouts.resource

*** Test Cases ***
Login Test
    StartApp    MeineApp
    SetValue    Benutzer    testuser
    # Alle Verify-Keywords nutzen jetzt die Projekt-Timeouts
    VerifyValue  Willkommen    Hallo testuser
    StopApp
```

#### b) Suite-Init (`__init__.robot`)

Fuer Projekte, die eine Verzeichnisstruktur mit `__init__.robot` verwenden:

```robotframework
# tests/__init__.robot
*** Settings ***
Library       okw_web_selenium.library.OkwWebSeleniumLibrary
Suite Setup   Projekt Timeouts setzen

*** Keywords ***
Projekt Timeouts setzen
    SetOKWParameter    TimeOutVerifyValue    15
    SetOKWParameter    TimeOutVerifyExist     5
```

**Wann verwenden?** Die Applikation ist generell langsamer/schneller als der
OKW-Default und alle Tests sollen einheitlich konfiguriert werden.

---

### Scope 3: Widget

Ein **einzelnes GUI-Objekt** bekommt per YAML-Locator individuelle Timeout-Werte.
Diese ueberschreiben den Projekt-Scope — aber nur fuer dieses eine Widget.

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

  # Standard-Widget, nutzt Projekt-/Global-Timeouts
  Seitenname:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="page-title"]' }
```

**Wann verwenden?** Ein einzelnes GUI-Objekt zeigt abweichendes Timing-Verhalten
(z.B. Dashboard-Aggregation, Lazy-Loading), waehrend der Rest der Applikation
mit den Projekt-Timeouts gut funktioniert.

> Siehe auch [synchronization_strategy.md](synchronization_strategy.md) fuer die
> vollstaendige `wait:`-Konfiguration inkl. Sync-Checks (exists, visible, enabled, ...).

---

### Scope 4: Testfall

Ein **einzelner Testfall** (oder ein Abschnitt darin) braucht abweichende Werte.
Gesetzt mit dem Keyword `SetOKWParameter` direkt im Test Case oder im `[Setup]`.

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
    # Zuruecksetzen auf Projekt-/Global-Wert
    SetOKWParameter    TimeOutVerifyValue    10

Normaler Test
    # Dieser Test nutzt wieder den Projekt-/Global-Timeout (10s)
    SetValue     Benutzer    admin
    VerifyValue  Status      Angemeldet
```

Alternativ mit `[Setup]` und `[Teardown]` fuer saubere Kapselung:

```robotframework
*** Test Cases ***
Langsamer Export
    [Setup]       SetOKWParameter    TimeOutVerifyValue    60
    [Teardown]    SetOKWParameter    TimeOutVerifyValue    10
    ClickOn       CSV exportieren
    VerifyValue   Status    Export abgeschlossen
```

**Wann verwenden?** Ein bestimmter Test hat spezielle Anforderungen
(langsame Operation, bekannt traeger Schritt), aber alle anderen Tests im
Projekt sollen davon nicht beeinflusst werden.

> **Hinweis:** `SetOKWParameter` setzt eine Suite-Variable. Der Wert bleibt
> bis zum naechsten Aufruf oder Suite-Ende bestehen. Bei testfallspezifischer
> Nutzung empfiehlt sich ein explizites Zuruecksetzen im `[Teardown]`.

---

### Scope 5: Ausfuehrung (Kommandozeile)

Parameter werden beim `robot`-Aufruf per `--variable` gesetzt. Dieser Scope
ueberschreibt **alle** anderen — das ist Standard-Robot-Framework-Verhalten.

```bash
# CI-Pipeline: Timeouts erhoehen
robot --variable OKW_TIMEOUT_VERIFY_VALUE:30 \
      --variable OKW_TIMEOUT_VERIFY_EXIST:10 \
      --variable OKW_POLL_VERIFY:0.2 \
      tests/

# Debugging: Einzelnen Test mit viel Zeit ausfuehren
robot --variable OKW_TIMEOUT_VERIFY_VALUE:120 \
      --test "Report-Generierung abwarten" \
      tests/

# Schnelllauf: Timeouts minimieren fuer Smoke-Test
robot --variable OKW_TIMEOUT_VERIFY_VALUE:3 \
      --variable OKW_TIMEOUT_VERIFY_EXIST:1 \
      --include smoke \
      tests/
```

**Wann verwenden?** Wenn die gleichen Tests in verschiedenen Umgebungen
mit unterschiedlichen Timeouts laufen sollen — **ohne eine einzige Datei
zu aendern**. Typische Szenarien:

- CI/CD-Pipeline (langsamere VMs)
- Debugging (sehr hohe Timeouts, damit der Test nicht abbricht)
- Smoke-Tests (minimale Timeouts fuer schnelles Feedback)

> **Wichtig:** `--variable` hat in Robot Framework **immer** die hoechste
> Prioritaet und ueberschreibt Variables-Sections, Resource-Dateien und
> `SetOKWParameter`-Aufrufe.

---

## Zusammenfassung: Wann welchen Scope verwenden?

| Scope | Mechanismus | Wann | Dateien aendern? |
|-------|------------|------|------------------|
| **1. Global** | — (Default) | Passt meistens | Nein |
| **2. Projekt** | Resource-Datei / `__init__.robot` | App generell langsam/schnell | Einmal zentral |
| **3. Widget** | YAML `wait:`-Block | Ein Widget ist Sonderfall | Nur die YAML-Datei |
| **4. Testfall** | `SetOKWParameter` im Test | Ein Test braucht mehr/weniger Zeit | Nur den Test |
| **5. Ausfuehrung** | `robot --variable` | CI, Debug, Smoke | Keine |

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
