# OKW4Robot

Treiberunabhaengige Keyword-Architektur fuer das [Robot Framework](https://robotframework.org/).

Ein einheitlicher Satz von Schluessselwoertern fuer verschiedene GUI-Technologien
(Web/Selenium, Web/Playwright, Java Swing, ...) – die konkrete Umsetzung erfolgt
im jeweiligen Treiber-Paket.

---

## OKW-Oekosystem

```
┌─────────────────────────────────────────────────────────┐
│                    Robot-Tests (.robot)                  │
│     StartHost Chrome / SetValue Name "Mustermann"       │
└──────────────────────────┬──────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │      okw4robot        │  Treiberunabhaengiger Kern
               │  Keywords, OkwWidget  │  pip install -e .
               │  Context, Contracts   │
               └───┬───────────────┬───┘
                   │               │
        ┌──────────▼──┐     ┌─────▼──────────┐
        │ okw-web-    │     │ okw-java-      │     (weitere Treiber
        │ selenium    │     │ swing          │      z.B. okw-web-
        │ WebSe_*     │     │ JavaSw_*       │      playwright)
        └─────────────┘     └────────────────┘
```

| Paket | Namespace | Status | Beschreibung |
|-------|-----------|--------|-------------|
| **okw4robot** | `okw4robot` | Stabil | Kern: Keywords, OkwWidget-Interface, Context, Contracts |
| **okw-web-selenium** | `okw_web_selenium` | Stabil (53 Tests) | Selenium WebDriver + WebSe_*-Widgets |
| **okw-java-swing** | `okw_java_swing` | In Arbeit | Java Swing via JSON-RPC |
| **okw-contract-utils** | `okw_contract_utils` | Stabil (PyPI) | Shared Contracts (Matchers, Tokens, YES/NO) |
| **okw-remote-ssh** | `robotframework_okw_remote_ssh` | Beta (PyPI) | SSH-Kommandos und SFTP |

---

## Erste Schritte

### 1. Kern installieren

```bash
pip install -e .
```

### 2. Treiber-Paket installieren (z.B. Selenium)

```bash
cd ../robotframework-okw-web-selenium
pip install -e .
```

### 3. Robot-Test schreiben

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Test Cases ***
Login Test
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    SetValue      URL              https://example.com/login
    StartApp      MeineApp
    SelectWindow  LoginDialog
    SetValue      Benutzer         admin
    SetValue      Passwort         geheim
    ClickOn       Anmelden
    VerifyValue   Status           Angemeldet
    StopHost
```

> **Hinweis:** Der Test importiert die *Treiber-Library* (`OkwWebSeleniumLibrary`),
> nicht `OKW4RobotLibrary` direkt. Die Treiber-Library erbt alle Keywords vom Kern.

---

## Architektur: Delegation statt Steuerung

Keywords rufen keine Adapter-Methoden direkt auf, sondern delegieren an genau
**eine** `okw_*`-Methode des Widgets:

```
Keyword SetValue "Name" "Mustermann"
    │
    ▼
widget = resolve_widget("Name")        # YAML-Locator → WebSe_TextField
widget.okw_set_value("Mustermann")     # Widget weiss, wie.
```

Das `OkwWidget`-Interface (in `okw4robot`) definiert alle `okw_*`-Methoden
mit `NotImplementedError`. Treiber-Pakete implementieren sie:

| okw4robot (Interface) | okw-web-selenium (Implementierung) |
|-----------------------|------------------------------------|
| `OkwWidget.okw_set_value()` | `WebSe_TextField.okw_set_value()` → Selenium `clear` + `input_text` |
| `OkwWidget.okw_click()` | `WebSe_Base.okw_click()` → Selenium `click_element` |
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
      widget_keywords.py        # SetValue, ClickOn, VerifyValue, ...
      attribute_keywords.py     # VerifyAttribute, MemorizeAttribute, LogAttribute
      caption_keywords.py       # VerifyCaption, MemorizeCaption, LogCaption
      label_keywords.py         # VerifyLabel, MemorizeLabel, LogLabel
      placeholder_keywords.py   # VerifyPlaceholder, ...
      tooltip_keywords.py       # VerifyTooltip, ...
      table_keywords.py         # VerifyTableCellValue, ...
      list_keywords.py          # VerifyListCount, VerifySelectedCount
      params.py                 # SetOKWParameter (Timeouts)
    runtime/
      context.py                # Zentraler Laufzeitkontext (Adapter, App, Window)
    widgets/
      okw_widget.py             # OkwWidget-Interface (NotImplementedError-Defaults)
    utils/
      yaml_loader.py            # YAML-Locator Suche (Projekt → Treiber-Pakete)
      loader.py                 # Dynamisches Laden von Klassen
      okw_helpers.py            # resolve_widget(), should_ignore(), ...
      logging_mixin.py          # LoggingMixin fuer alle Klassen
      table_tokens.py           # $TAB/$LF Token-Parser
  tests/
    unit/                       # 53 pytest Unit-Tests mit MockWidget
  docs/
    CONTRACT.md                 # Oeffentlicher Vertrag
    KEYWORDS.md                 # Keyword-Referenz (alle Keywords)
    SPECIFICATION.md            # Semantische Spezifikation
    keywords_*.md               # Keyword-Dokumentation pro Thema
    okw_parameters.md           # Timeout-/Sync-Parameter
    synchronization_strategy.md # Sync-Strategie (wait_before)
    ...
```

---

## Dokumentation

### Vertraege und Spezifikation

- [CONTRACT.md](docs/CONTRACT.md) – Oeffentlicher Vertrag (Architektur, YAML-Fallback)
- [KEYWORDS.md](docs/KEYWORDS.md) – Keyword-Referenz (alle Keywords auf einen Blick)
- [SPECIFICATION.md](docs/SPECIFICATION.md) – Semantische Keyword-Spezifikation

### Keywords

- [keywords_host_app.md](docs/keywords_host_app.md) – Host/App/Window Keywords
- [keywords_attribute.md](docs/keywords_attribute.md) – VerifyAttribute, MemorizeAttribute, LogAttribute
- [keywords_caption.md](docs/keywords_caption.md) – VerifyCaption, MemorizeCaption, LogCaption
- [keywords_label.md](docs/keywords_label.md) – VerifyLabel, MemorizeLabel, LogLabel
- [keywords_placeholder.md](docs/keywords_placeholder.md) – VerifyPlaceholder, ...
- [keywords_tooltip.md](docs/keywords_tooltip.md) – VerifyTooltip, ...
- [keywords_table.md](docs/keywords_table.md) – Tabellen-Keywords (index-basiert)
- [keywords_table_headers.md](docs/keywords_table_headers.md) – Tabellen-Keywords (header-basiert)
- [keywords_list.md](docs/keywords_list.md) – VerifyListCount, VerifySelectedCount
- [keywords_ignore_rule.md](docs/keywords_ignore_rule.md) – $IGNORE, $EMPTY, $DELETE

### Konzepte

- [context.md](docs/context.md) – Laufzeitkontext (Adapter, App, Window)
- [objektzustaende.md](docs/objektzustaende.md) – Widget-Zustaende (exists, visible, enabled, ...)
- [okw_parameters.md](docs/okw_parameters.md) – Timeouts und Parameter
- [synchronization_strategy.md](docs/synchronization_strategy.md) – Sync-Strategie
- [widgets_common.md](docs/widgets_common.md) – Widget-Hierarchie und OkwWidget-Interface
- [table_tokens.md](docs/table_tokens.md) – $TAB/$LF Token-Syntax
- [regex_best_practices.md](docs/regex_best_practices.md) – Regex-Tipps fuer Robot Framework

---

## Lizenz

- **Community** (nicht-kommerziell): siehe [LICENSE](LICENSE)
- **Kommerziell**: siehe [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)
- **FAQ**: [docs/license_faq.md](docs/license_faq.md)

---

## Warten auf Werte und Synchronisation

Verify-Keywords warten automatisch auf Sollwerte (mit Timeout und Polling):

```robotframework
# Timeout setzen (optional, Default: 10s)
SetOKWParameter    TimeOutVerifyValue    15

# Keyword wartet bis zu 15s auf den erwarteten Wert
VerifyValue    Status    Angemeldet
```

Schreibende Aktionen (Click, SetValue, TypeKey, Select) pruefen vorher:
`exists → scroll_into_view → visible → enabled → editable → until_not_visible`

Details: [docs/synchronization_strategy.md](docs/synchronization_strategy.md),
[docs/okw_parameters.md](docs/okw_parameters.md)
