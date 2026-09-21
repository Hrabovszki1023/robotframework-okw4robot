# OKW4Robot

[![PyPI](https://img.shields.io/pypi/v/robotframework-okw4robot)](https://pypi.org/project/robotframework-okw4robot/)
[![Python](https://img.shields.io/pypi/pyversions/robotframework-okw4robot)](https://pypi.org/project/robotframework-okw4robot/)
[![License](https://img.shields.io/badge/License-OKW_Community-orange.svg)](LICENSE)

Treiberunabhängige Keyword-Architektur für [Robot Framework](https://robotframework.org/) — ein Satz Keywords für Web, Java Swing, SAP GUI und mehr.

> **English version:** [README.md](README.md)

> **ISO/IEC/IEEE 29119-5:2024:** OKW4Robot implementiert den internationalen Standard
> für Keyword-Driven Testing — strukturell seit 2003.
> Siehe [ISO 29119-5 Conformity](docs/iso-29119-5-conformity.md).

## Signal vs. NOISE

| Signal (dein Test) | NOISE (versteckt durch OKW) |
|---|---|
| `SetValue Benutzer admin` | Selenium/Swing/SAP-Adapter-Auswahl |
| `VerifyValue Status Logged in` | Polling-Schleife, Timeout, Match-Modus |
| `ClickOn Login` | Element-Suche, Scroll, Wait, Click |

Testcode enthält nur **was** getestet wird (Signal). **Wie** es ausgeführt wird (NOISE) steckt in YAML-Locators, Widget-Klassen und Adaptern.

### Die Trinität: Test — YAML — Widget

OKW entkoppelt Fachlichkeit und Technik durch drei Schichten:

```
Test (.robot)          YAML Locator (.yaml)       Widget + Adapter (.py)
─────────────          ────────────────────       ──────────────────────
Fachsprache        →   Mapping-Schicht        →   Technische Umsetzung
SetValue Name admin    Name:                      RemoteSw_TextField
                         locator: {name: "txtName"}  → clear + typeIntoTextField
```

Der **Test** spricht die Sprache des Testers. Die **YAML-Datei** übersetzt
Fachbegriffe in technische Bezeichner. **Widget + Adapter** kapseln den
Treiber. Wenn sich die GUI ändert, ändert sich nur die YAML-Datei —
der Test bleibt gleich. Wenn die Technologie wechselt (Web → SAP),
ändern sich nur YAML und Adapter — der Test bleibt gleich.

### Widget-Benennungsregel

YAML-Widget-Schlüssel sind **Fachbegriffe**, keine technischen Bezeichner.
Der Schlüssel erscheint im Testcode (`SetValue Name admin`) und muss die
Fachsprache sprechen. Typ-Präfixe (`txt`, `btn`, `chk`, `lbl`, `cb`)
sind NOISE — der Typ ist bereits in `class` und `locator` kodiert.
Dieses NOISE wird durch **DRY** eliminiert: der technische Typ wird an
genau einer Stelle gepflegt — in der YAML-Locator-Datei — und nirgendwo sonst.

| Falsch (technisch) | Richtig (fachlich) | Warum |
|---|---|---|
| `txtName` | `Name` | Heute ein TextField, morgen ein MultilineField — der Test bleibt gleich |
| `btnOK` | `OK` | Der Test sagt "klick OK", nicht "klick Button OK" |
| `cbStatus` | `Status` | Wenn die ComboBox eine RadioList wird, keine Teständerung |

---

## OKW-Ökosystem

```
┌─────────────────────────────────────────────────────────┐
│                    Robot Tests (.robot)                   │
│     StartApp MyApp / SetValue Name "Smith"               │
└──────────────────────────┬──────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │      okw4robot        │  Treiberunabhängiger Core
               │  Keywords, OkwWidget  │  pip install robotframework-okw4robot
               │  Context, Contracts   │
               └───┬───────────────┬───┘
                   │               │
        ┌──────────▼──┐     ┌─────▼──────────┐
        │ okw-web-    │     │ okw-java-      │     (weitere Treiber
        │ selenium    │     │ remoteswing    │      z.B. okw-web-
        │ WebSe_*     │     │ RemoteSw_*     │      playwright)
        └─────────────┘     └────────────────┘
```

| Paket | Namespace | Status | Beschreibung |
|-------|-----------|--------|--------------|
| **okw4robot** | `okw4robot` | Stabil | Core: Keywords, OkwWidget-Interface, Context, Contracts |
| **okw-web-selenium** | `okw_web_selenium` | Stabil (53 Tests) | Selenium WebDriver + WebSe_*-Widgets |
| **okw-java-remoteswing** | `okw_java_remoteswing` | Stabil (106 Tests) | Java Swing via RemoteSwingLibrary + RemoteSw_*-Widgets |
| **okw-contract-utils** | `okw_contract_utils` | Stabil (PyPI) | Gemeinsame Contracts (Matcher, Tokens, YES/NO) |
| **okw-remote-ssh** | `robotframework_okw_remote_ssh` | Beta (PyPI) | SSH-Kommandos und SFTP |

---

## Erste Schritte

### 1. Core installieren

```bash
pip install robotframework-okw4robot
```

### 2. Treiber-Paket installieren (z.B. Selenium)

```bash
pip install robotframework-okw-web-selenium
```

### 3. Robot-Test schreiben

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Test Cases ***
Login Test
    StartApp      MyApp
    SelectWindow  LoginDialog
    SetValue      Username         admin
    SetValue      Password         secret
    ClickOn       Login
    VerifyValue   Status           Logged in
```

`StartApp` lädt die App-YAML. Wenn die YAML eine `__self__`-Sektion mit
der Adapter-Klasse enthält, wird der Adapter automatisch gestartet — kein
separater `StartHost`-Aufruf nötig.

> **Hinweis:** Der Test importiert die *Treiber-Bibliothek* (`OkwWebSeleniumLibrary`),
> nicht `OKW4RobotLibrary` direkt. Die Treiber-Bibliothek erbt alle Keywords
> vom Core.

---

## Architektur: Delegation, nicht Kontrolle

Keywords rufen Adapter-Methoden nicht direkt auf. Stattdessen delegieren sie
an genau **eine** `okw_*`-Methode auf dem Widget:

```
Keyword SetValue "Name" "Smith"
    │
    ▼
widget = resolve_widget("Name")        # YAML-Locator → WebSe_TextField
widget.okw_set_value("Smith")          # Widget weiss wie.
```

Das `OkwWidget`-Interface (in `okw4robot`) definiert alle `okw_*`-Methoden
mit `NotImplementedError`. Treiber-Pakete implementieren sie:

| okw4robot (Interface) | okw-web-selenium (Implementierung) |
|-----------------------|------------------------------------|
| `OkwWidget.okw_set_value()` | `WebSe_TextField.okw_set_value()` → Selenium `clear` + `input_text` |
| `OkwWidget.okw_click()` | `WebSe_Base.okw_click()` → Selenium `click_element` |
| `OkwWidget.okw_move_over()` | `WebSe_Base.okw_move_over()` → Selenium `ActionChains.move_to_element` |
| `OkwWidget.okw_exists()` | `WebSe_Base.okw_exists()` → Selenium `find_elements` |

---

## Projektstruktur

```
robotframework-okw4robot/
  src/okw4robot/
    library.py                  # OKW4RobotLibrary (alle Keyword-Mixins)
    keywords/
      host.py                   # StartHost, StopHost, SelectHost
      app.py                    # StartApp, StopApp, SelectWindow
      widget_keywords.py        # SetValue, ClickOn, MoveOver, VerifyValue, ...
      attribute_keywords.py     # VerifyAttribute, MemorizeAttribute, LogAttribute
      caption_keywords.py       # VerifyCaption, MemorizeCaption, LogCaption
      label_keywords.py         # VerifyLabel, MemorizeLabel, LogLabel
      placeholder_keywords.py   # VerifyPlaceholder, ...
      tooltip_keywords.py       # VerifyTooltip, ...
      table_keywords.py         # VerifyTableCellValue, ...
      list_keywords.py          # VerifyListCount, VerifySelectedCount
      noise_keywords.py         # OnFailNOISE, OnFailIgnoreNOISE (NOISE/FAIL-Klassifikation)
      params.py                 # SetOKWParameter (Timeouts)
    runtime/
      context.py                # Zentraler Laufzeit-Kontext (Adapter, App, Fenster)
    widgets/
      okw_widget.py             # OkwWidget-Interface (NotImplementedError-Defaults)
    utils/
      yaml_loader.py            # YAML-Locator-Suche (Projekt → Treiber-Pakete)
      loader.py                 # Dynamisches Laden von Klassen
      okw_helpers.py            # resolve_widget(), should_ignore(), ...
      logging_mixin.py          # LoggingMixin für alle Klassen
      table_tokens.py           # $TAB/$LF Token-Parser
  tests/
    unit/                       # 53 pytest-Unit-Tests mit MockWidget
  docs/
    CONTRACT.md                 # Öffentlicher Vertrag
    KEYWORDS.md                 # Keyword-Referenz (alle Keywords)
    SPECIFICATION.md            # Semantische Spezifikation
    keywords_*.md               # Keyword-Dokumentation pro Thema
    okw_parameters.md           # Timeouts und Parameter
    synchronization_strategy.md # Sync-Strategie (wait_before)
    ...
```

---

## Dokumentation

### Standards

- [iso-29119-5-conformity.md](docs/iso-29119-5-conformity.md) – ISO/IEC/IEEE 29119-5:2024 Konformität (Architektur, Keyword-Mapping, Framework-Komponenten)

### Verträge und Spezifikation

- [CONTRACT.md](docs/CONTRACT.md) – Öffentlicher Vertrag (Architektur, YAML-Fallback)
- [KEYWORDS.md](docs/KEYWORDS.md) – Keyword-Referenz (alle Keywords auf einen Blick)
- [SPECIFICATION.md](docs/SPECIFICATION.md) – Semantische Keyword-Spezifikation

### Keywords

- [keywords_host_app.md](docs/keywords_host_app.md) – Host/App/Window-Keywords
- [keywords_attribute.md](docs/keywords_attribute.md) – VerifyAttribute, MemorizeAttribute, LogAttribute
- [keywords_caption.md](docs/keywords_caption.md) – VerifyCaption, MemorizeCaption, LogCaption
- [keywords_label.md](docs/keywords_label.md) – VerifyLabel, MemorizeLabel, LogLabel
- [keywords_placeholder.md](docs/keywords_placeholder.md) – VerifyPlaceholder, ...
- [keywords_tooltip.md](docs/keywords_tooltip.md) – VerifyTooltip, ...
- [keywords_table.md](docs/keywords_table.md) – Tabellen-Keywords (indexbasiert)
- [keywords_table_headers.md](docs/keywords_table_headers.md) – Tabellen-Keywords (headerbasiert)
- [keywords_list.md](docs/keywords_list.md) – VerifyListCount, VerifySelectedCount
- [keywords_ignore_rule.md](docs/keywords_ignore_rule.md) – $IGNORE, $EMPTY, $DELETE
- [keywords_noise.md](docs/keywords_noise.md) – OnFailNOISE, OnFailIgnoreNOISE (NOISE/FAIL-Klassifikation)

### Konzepte

- [context.md](docs/context.md) – Laufzeit-Kontext (Adapter, App, Fenster)
- [objektzustaende.md](docs/objektzustaende.md) – Widget-Zustände (exists, visible, enabled, ...)
- [okw_parameters.md](docs/okw_parameters.md) – Timeouts und Parameter ([DE](docs/okw_parameters_de.md))
- [synchronization_strategy.md](docs/synchronization_strategy.md) – Sync-Strategie
- [widgets_common.md](docs/widgets_common.md) – Widget-Hierarchie und OkwWidget-Interface
- [table_tokens.md](docs/table_tokens.md) – $TAB/$LF Token-Syntax
- [regex_best_practices.md](docs/regex_best_practices.md) – Regex-Tipps für Robot Framework

---

## Warten auf Werte und Synchronisation

Verify-Keywords warten automatisch auf erwartete Werte (mit Timeout und Polling):

```robotframework
# Timeout setzen (optional, Standard: 10s)
SetOKWParameter    TimeOutVerifyValue    15

# Keyword wartet bis zu 15s auf den erwarteten Wert
VerifyValue    Status    Logged in
```

Schreib-Aktionen (Click, SetValue, TypeKey, Select) prüfen Vorbedingungen:
`exists → scroll_into_view → visible → enabled → editable → until_not_visible`

Details: [docs/okw_parameters.md](docs/okw_parameters.md),
[docs/synchronization_strategy.md](docs/synchronization_strategy.md)

---

## KI-Testgenerierung

Testfälle können mit jeder KI (Claude, ChatGPT, Copilot, ...) generiert werden.
OKWs Architektur bietet gegenüber dem Page Object Model (POM) einen
entscheidenden Vorteil:

| | POM | OKW |
|---|---|---|
| **Was muss die KI lernen?** | Projekt-spezifische Klassenhierarchie, Konventionen, Base-Page-Methoden | Keyword-Liste + YAML-Schema (kompakt, einheitlich) |
| **Prompt-Größe** | Groß — gesamte Klassenhierarchie als Kontext nötig | Klein — Keyword-Tabelle + ein YAML-Beispiel reichen |
| **Übertragbarkeit** | Gelernt für ein Projekt, nicht übertragbar | Einmal gelernt, gilt für alle Projekte und Technologien |
| **Bausteine vorhanden?** | Nein — jede Page-Klasse wird von Grund auf geschrieben | Ja — elementare Keywords (`SetValue`, `ClickOn`, `VerifyValue`) sind fertige Bausteine |
| **Fehlerraum** | Groß — Kompilierfehler, falsche Vererbung, fehlende Imports | Klein — falscher Widget-Name oder Locator, sofort erkennbar |

Die System-Prompts für die KI-gestützte Testgenerierung werden pro
Bibliothek in [`prompts/`](prompts/) gepflegt.

## Lauffähige Beispiele

[okw-examples](https://github.com/Hrabovszki1023/okw-examples) — lauffähige Robot Framework Tests für Web, Java Swing, SAP GUI, REST, SSH, Kafka.

## Handbuch

[OKW4Robot Handbuch](https://hrabovszki1023.github.io/okw-examples/) — Schritt-für-Schritt-Anleitung.

## Lizenz

- **Community** (nicht-kommerziell): siehe [LICENSE](LICENSE)
- **Kommerziell**: siehe [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)
- **FAQ**: [docs/license_faq.md](docs/license_faq.md)
