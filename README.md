# OKW4Robot

[![PyPI](https://img.shields.io/pypi/v/robotframework-okw4robot)](https://pypi.org/project/robotframework-okw4robot/)
[![Python](https://img.shields.io/pypi/pyversions/robotframework-okw4robot)](https://pypi.org/project/robotframework-okw4robot/)
[![License](https://img.shields.io/badge/License-OKW_Community-orange.svg)](LICENSE)

Driver-agnostic keyword architecture for [Robot Framework](https://robotframework.org/) — one set of keywords for Web, Java Swing, SAP GUI, and more.

> **Deutsche Version:** [README_de.md](README_de.md)

> **ISO/IEC/IEEE 29119-5:2024:** OKW4Robot implements the international standard
> for Keyword-Driven Testing — structurally since 2003.
> See [ISO 29119-5 Conformity](docs/iso-29119-5-conformity.md).

## Signal vs. NOISE

| Signal (your test) | NOISE (hidden by OKW) |
|---|---|
| `SetValue Benutzer admin` | Selenium/Swing/SAP adapter selection |
| `VerifyValue Status Logged in` | Polling loop, timeout, match mode |
| `ClickOn Login` | Element lookup, scroll, wait, click |

Test code contains only **what** is tested (Signal). **How** it is executed (NOISE) stays in YAML locators, widget classes, and adapters.

### The Trinity: Test — YAML — Widget

OKW decouples business logic from technical implementation through three layers:

```
Test (.robot)          YAML locator (.yaml)       Widget + Adapter (.py)
─────────────          ────────────────────       ──────────────────────
Business language  →   Mapping layer          →   Technical implementation
SetValue Name admin    Name:                      RemoteSw_TextField
                         locator: {name: "txtName"}  → clear + typeIntoTextField
```

The **test** speaks the tester's language. The **YAML file** translates
business terms into technical identifiers. The **widget + adapter**
encapsulate the driver. When the GUI changes, only the YAML changes —
the test stays the same. When the technology changes (Web → SAP),
only the YAML and adapter change — the test stays the same.

### Widget Naming Rule

YAML widget keys are **business names**, not technical identifiers.
The key appears in test code (`SetValue Name admin`) and must speak
the domain language. Type prefixes (`txt`, `btn`, `chk`, `lbl`, `cb`)
are NOISE — the type is already encoded in `class` and `locator`.
This NOISE is eliminated by applying **DRY**: the technical type is
maintained in exactly one place — the YAML locator file — and nowhere else.

| Wrong (technical) | Right (business) | Why |
|---|---|---|
| `txtName` | `Name` | Today a TextField, tomorrow a MultilineField — test stays the same |
| `btnOK` | `OK` | The test says "click OK", not "click button OK" |
| `cbStatus` | `Status` | If the ComboBox becomes a RadioList, no test change |

---

## OKW Ecosystem

```
┌─────────────────────────────────────────────────────────┐
│                    Robot Tests (.robot)                   │
│     StartApp MyApp / SetValue Name "Smith"               │
└──────────────────────────┬──────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │      okw4robot        │  Driver-agnostic core
               │  Keywords, OkwWidget  │  pip install robotframework-okw4robot
               │  Context, Contracts   │
               └───┬───────────────┬───┘
                   │               │
        ┌──────────▼──┐     ┌─────▼──────────┐
        │ okw-web-    │     │ okw-java-      │     (more drivers
        │ selenium    │     │ remoteswing    │      e.g. okw-web-
        │ WebSe_*     │     │ RemoteSw_*     │      playwright)
        └─────────────┘     └────────────────┘
```

| Package | Namespace | Status | Description |
|---------|-----------|--------|-------------|
| **okw4robot** | `okw4robot` | Stable | Core: keywords, OkwWidget interface, context, contracts |
| **okw-web-selenium** | `okw_web_selenium` | Stable (53 tests) | Selenium WebDriver + WebSe_* widgets |
| **okw-java-remoteswing** | `okw_java_remoteswing` | Stable (106 tests) | Java Swing via RemoteSwingLibrary + RemoteSw_* widgets |
| **okw-contract-utils** | `okw_contract_utils` | Stable (PyPI) | Shared contracts (matchers, tokens, YES/NO) |
| **okw-remote-ssh** | `robotframework_okw_remote_ssh` | Beta (PyPI) | SSH commands and SFTP |

---

## Getting Started

### 1. Install the core

```bash
pip install robotframework-okw4robot
```

### 2. Install a driver package (e.g. Selenium)

```bash
pip install robotframework-okw-web-selenium
```

### 3. Write a Robot test

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

`StartApp` loads the app YAML. If the YAML contains a `__self__` section with
the adapter class, the adapter is started automatically — no separate `StartHost`
needed.

> **Note:** The test imports the *driver library* (`OkwWebSeleniumLibrary`),
> not `OKW4RobotLibrary` directly. The driver library inherits all keywords
> from the core.

---

## Architecture: Delegation, Not Control

Keywords do not call adapter methods directly. Instead, they delegate to
exactly **one** `okw_*` method on the widget:

```
Keyword SetValue "Name" "Smith"
    │
    ▼
widget = resolve_widget("Name")        # YAML locator → WebSe_TextField
widget.okw_set_value("Smith")          # Widget knows how.
```

The `OkwWidget` interface (in `okw4robot`) defines all `okw_*` methods
with `NotImplementedError`. Driver packages implement them:

| okw4robot (Interface) | okw-web-selenium (Implementation) |
|-----------------------|-----------------------------------|
| `OkwWidget.okw_set_value()` | `WebSe_TextField.okw_set_value()` → Selenium `clear` + `input_text` |
| `OkwWidget.okw_click()` | `WebSe_Base.okw_click()` → Selenium `click_element` |
| `OkwWidget.okw_move_over()` | `WebSe_Base.okw_move_over()` → Selenium `ActionChains.move_to_element` |
| `OkwWidget.okw_exists()` | `WebSe_Base.okw_exists()` → Selenium `find_elements` |

---

## Project Structure

```
robotframework-okw4robot/
  src/okw4robot/
    library.py                  # OKW4RobotLibrary (all keyword mixins)
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
      noise_keywords.py         # OnFailNOISE, OnFailIgnoreNOISE (NOISE/FAIL classification)
      params.py                 # SetOKWParameter (timeouts)
    runtime/
      context.py                # Central runtime context (adapter, app, window)
    widgets/
      okw_widget.py             # OkwWidget interface (NotImplementedError defaults)
    utils/
      yaml_loader.py            # YAML locator search (project → driver packages)
      loader.py                 # Dynamic class loading
      okw_helpers.py            # resolve_widget(), should_ignore(), ...
      logging_mixin.py          # LoggingMixin for all classes
      table_tokens.py           # $TAB/$LF token parser
  tests/
    unit/                       # 53 pytest unit tests with MockWidget
  docs/
    CONTRACT.md                 # Public contract
    KEYWORDS.md                 # Keyword reference (all keywords)
    SPECIFICATION.md            # Semantic specification
    keywords_*.md               # Keyword documentation per topic
    okw_parameters.md           # Timeouts and parameters
    synchronization_strategy.md # Sync strategy (wait_before)
    ...
```

---

## Documentation

### Standards

- [iso-29119-5-conformity.md](docs/iso-29119-5-conformity.md) – ISO/IEC/IEEE 29119-5:2024 conformity (architecture, keyword mapping, framework components)

### Contracts and Specification

- [CONTRACT.md](docs/CONTRACT.md) – Public contract (architecture, YAML fallback)
- [KEYWORDS.md](docs/KEYWORDS.md) – Keyword reference (all keywords at a glance)
- [SPECIFICATION.md](docs/SPECIFICATION.md) – Semantic keyword specification

### Keywords

- [keywords_host_app.md](docs/keywords_host_app.md) – Host/App/Window keywords
- [keywords_attribute.md](docs/keywords_attribute.md) – VerifyAttribute, MemorizeAttribute, LogAttribute
- [keywords_caption.md](docs/keywords_caption.md) – VerifyCaption, MemorizeCaption, LogCaption
- [keywords_label.md](docs/keywords_label.md) – VerifyLabel, MemorizeLabel, LogLabel
- [keywords_placeholder.md](docs/keywords_placeholder.md) – VerifyPlaceholder, ...
- [keywords_tooltip.md](docs/keywords_tooltip.md) – VerifyTooltip, ...
- [keywords_table.md](docs/keywords_table.md) – Table keywords (index-based)
- [keywords_table_headers.md](docs/keywords_table_headers.md) – Table keywords (header-based)
- [keywords_list.md](docs/keywords_list.md) – VerifyListCount, VerifySelectedCount
- [keywords_ignore_rule.md](docs/keywords_ignore_rule.md) – $IGNORE, $EMPTY, $DELETE
- [keywords_noise.md](docs/keywords_noise.md) – OnFailNOISE, OnFailIgnoreNOISE (NOISE/FAIL classification)

### Concepts

- [context.md](docs/context.md) – Runtime context (adapter, app, window)
- [objektzustaende.md](docs/objektzustaende.md) – Widget states (exists, visible, enabled, ...)
- [okw_parameters.md](docs/okw_parameters.md) – Timeouts and parameters ([DE](docs/okw_parameters_de.md))
- [synchronization_strategy.md](docs/synchronization_strategy.md) – Sync strategy
- [widgets_common.md](docs/widgets_common.md) – Widget hierarchy and OkwWidget interface
- [table_tokens.md](docs/table_tokens.md) – $TAB/$LF token syntax
- [regex_best_practices.md](docs/regex_best_practices.md) – Regex tips for Robot Framework

---

## Waiting for Values and Synchronization

Verify keywords automatically wait for expected values (with timeout and polling):

```robotframework
# Set timeout (optional, default: 10s)
SetOKWParameter    TimeOutVerifyValue    15

# Keyword waits up to 15s for the expected value
VerifyValue    Status    Logged in
```

Write actions (Click, SetValue, TypeKey, Select) check preconditions first:
`exists → scroll_into_view → visible → enabled → editable → until_not_visible`

Details: [docs/okw_parameters.md](docs/okw_parameters.md),
[docs/synchronization_strategy.md](docs/synchronization_strategy.md)

---

## Runnable Examples

[okw-examples](https://github.com/Hrabovszki1023/okw-examples) — working Robot Framework tests for Web, Java Swing, SAP GUI, REST, SSH, Kafka.

## Handbuch

[OKW4Robot Handbuch](https://hrabovszki1023.github.io/okw-examples/) — step-by-step guide (German).

## License

- **Community** (non-commercial): see [LICENSE](LICENSE)
- **Commercial**: see [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)
- **FAQ**: [docs/license_faq.md](docs/license_faq.md)
