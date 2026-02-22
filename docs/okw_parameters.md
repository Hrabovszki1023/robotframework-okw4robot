# OKW Parameters and Timeouts

OKW uses configurable timeout and control parameters to adjust the behavior
of verify keywords, synchronization, and ignore rules. This page describes
the **five scopes** in which parameters can be set, and how they override
each other.

> **Deutsche Version:** [okw_parameters_de.md](okw_parameters_de.md)

---

## Why Adjust Timeouts?

OKW verify keywords (`VerifyValue`, `VerifyExist`, `VerifyTooltip`, ...) do
**not** perform a single comparison. Instead, they run in a **polling loop**:
the current value is read repeatedly and compared to the expected value until
it matches or the timeout expires.

```
Flow (simplified):

    VerifyValue "Username" "Max"
         │
         ▼
    ┌──────────────────────────┐
    │  Read value (okw_get_value)  │◄─────┐
    │  Actual: ""                  │      │
    │  Expected: "Max"             │      │  Poll interval
    │  Match?   NO                 │      │  (0.1s default)
    └──────────┬───────────────────┘      │
               │                          │
               ▼                          │
         Timeout reached? ───NO──────────►┘
               │
              YES
               ▼
         FAIL: "Expected 'Max', got ''"
```

The **default timeouts** (10 seconds for values, 2 seconds for states) work
for most applications. In certain situations they need to be adjusted:

| Situation | Recommendation | Scope |
|-----------|---------------|-------|
| **Slow application** (complex calculations, backend calls) | Increase timeout (`20s`, `30s`) | Project |
| **Fast unit/widget tests** (local HTML page, no backend) | Reduce timeout (`3s`, `5s`) for faster feedback | Project |
| **CI/CD environment** (slower VMs, parallel load) | Increase timeout (`15s`–`30s`) | Execution |
| **Asynchronous loading** (AJAX, WebSocket updates) | Increase timeout + adjust poll interval | Project / Widget |
| **Single slow element** (e.g. dashboard widget) | Override via YAML instance | Widget |
| **One test needs more time** (report generation, export) | `SetOKWParameter` in the test | Test case |
| **Debugging a single test** | `--variable` on the command line | Execution |

---

## The Five Scopes (Override Cascade)

Parameters are set in five scopes. Each more specific scope overrides the
broader one:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Global (OKW Default)        — Hard-coded in OKW          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  2. Project                  — Resource / __init__      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  3. Widget                — YAML wait: block      │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  4. Test case          — SetOKWParameter    │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  5. Execution       — robot --variable │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

More specific scope wins:  Global < Project < Widget < Test case < Execution
```

---

### Scope 1: Global (OKW Default)

The default values hard-coded in OKW. They apply when no other scope
overrides a parameter. Nothing to do — these values are always present.

| Parameter | Default |
|-----------|---------|
| `${OKW_TIMEOUT_VERIFY_VALUE}` | 10 |
| `${OKW_TIMEOUT_VERIFY_EXIST}` | 2.0 |
| `${OKW_POLL_VERIFY}` | 0.1 |
| `${OKW_IGNORE_EMPTY}` | NO |
| ... | (see reference below) |

---

### Scope 2: Project

Project-wide settings that apply to **all tests in the project**.
Two variants:

#### a) Resource file (recommended)

A central resource file imported by all test suites:

```robotframework
# resources/project_timeouts.resource
*** Variables ***
${OKW_TIMEOUT_VERIFY_VALUE}          15
${OKW_TIMEOUT_VERIFY_PLACEHOLDER}    10
${OKW_TIMEOUT_VERIFY_TOOLTIP}        10
${OKW_TIMEOUT_VERIFY_EXIST}           5
${OKW_TIMEOUT_VERIFY_VISIBLE}         5
${OKW_POLL_VERIFY}                   0.1
```

```robotframework
# tests/MyTests.robot
*** Settings ***
Library     okw_web_selenium.library.OkwWebSeleniumLibrary
Resource    ../resources/project_timeouts.resource

*** Test Cases ***
Login Test
    StartApp    MyApp
    SetValue    Username    testuser
    # All verify keywords now use the project timeouts
    VerifyValue  Welcome    Hello testuser
    StopApp
```

#### b) Suite init (`__init__.robot`)

For projects that use a directory structure with `__init__.robot`:

```robotframework
# tests/__init__.robot
*** Settings ***
Library       okw_web_selenium.library.OkwWebSeleniumLibrary
Suite Setup   Set Project Timeouts

*** Keywords ***
Set Project Timeouts
    SetOKWParameter    TimeOutVerifyValue    15
    SetOKWParameter    TimeOutVerifyExist     5
```

**When to use?** The application is generally slower/faster than the OKW
defaults and all tests should be configured uniformly.

---

### Scope 3: Widget

A **single GUI object** receives individual timeout values via its YAML
locator. These override the project scope — but only for this one widget.

```yaml
# locators/Dashboard.yaml
Dashboard:
  __self__:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="dashboard"]' }

  # This widget always loads slowly (complex aggregation)
  Monthly Revenue:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="revenue-month"]' }
    wait:
      write:
        timeout: 30
      read:
        timeout: 30

  # Standard widget, uses project/global timeouts
  Page Title:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { css: '[data-testid="page-title"]' }
```

**When to use?** A single GUI object shows divergent timing behavior
(e.g. dashboard aggregation, lazy loading), while the rest of the
application works fine with the project timeouts.

> See also [synchronization_strategy.md](synchronization_strategy.md) for the
> full `wait:` configuration including sync checks (exists, visible, enabled, ...).

---

### Scope 4: Test Case

A **single test case** (or a section within it) needs different values.
Set with the keyword `SetOKWParameter` directly in the test case or in `[Setup]`.

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Test Cases ***
Wait For Report Generation
    SetValue     From-Date     01.01.2025
    SetValue     To-Date       31.12.2025
    ClickOn      Generate Report
    # Report generation takes up to 60 seconds
    SetOKWParameter    TimeOutVerifyValue    60
    VerifyValue  Status    Report complete
    # Reset to project/global value
    SetOKWParameter    TimeOutVerifyValue    10

Normal Test
    # This test uses the project/global timeout again (10s)
    SetValue     Username    admin
    VerifyValue  Status      Logged in
```

Alternatively with `[Setup]` and `[Teardown]` for clean encapsulation:

```robotframework
*** Test Cases ***
Slow Export
    [Setup]       SetOKWParameter    TimeOutVerifyValue    60
    [Teardown]    SetOKWParameter    TimeOutVerifyValue    10
    ClickOn       Export CSV
    VerifyValue   Status    Export complete
```

**When to use?** A specific test has special requirements (slow operation,
known sluggish step), but all other tests in the project should remain
unaffected.

> **Note:** `SetOKWParameter` sets a suite variable. The value persists until
> the next call or suite end. For test-case-specific usage, an explicit reset
> in `[Teardown]` is recommended.

---

### Scope 5: Execution (Command Line)

Parameters are set via `--variable` on the `robot` command line. This scope
overrides **all** others — this is standard Robot Framework behavior.

```bash
# CI pipeline: increase timeouts
robot --variable OKW_TIMEOUT_VERIFY_VALUE:30 \
      --variable OKW_TIMEOUT_VERIFY_EXIST:10 \
      --variable OKW_POLL_VERIFY:0.2 \
      tests/

# Debugging: run a single test with plenty of time
robot --variable OKW_TIMEOUT_VERIFY_VALUE:120 \
      --test "Wait For Report Generation" \
      tests/

# Quick run: minimize timeouts for smoke test
robot --variable OKW_TIMEOUT_VERIFY_VALUE:3 \
      --variable OKW_TIMEOUT_VERIFY_EXIST:1 \
      --include smoke \
      tests/
```

**When to use?** When the same tests should run in different environments
with different timeouts — **without changing a single file**. Typical
scenarios:

- CI/CD pipeline (slower VMs)
- Debugging (very high timeouts so the test does not abort)
- Smoke tests (minimal timeouts for fast feedback)

> **Important:** `--variable` **always** has the highest priority in Robot
> Framework and overrides variables sections, resource files, and
> `SetOKWParameter` calls.

---

## Summary: When to Use Which Scope?

| Scope | Mechanism | When | Change files? |
|-------|-----------|------|---------------|
| **1. Global** | — (Default) | Works most of the time | No |
| **2. Project** | Resource file / `__init__.robot` | App generally slow/fast | Once, centrally |
| **3. Widget** | YAML `wait:` block | One widget is a special case | Only the YAML file |
| **4. Test case** | `SetOKWParameter` in test | One test needs more/less time | Only that test |
| **5. Execution** | `robot --variable` | CI, debug, smoke | None |

---

## Interaction with Synchronization

The verify timeouts control the **content check**: "Does the element have
the right value?" The sync timeouts (documented in
[synchronization_strategy.md](synchronization_strategy.md)) control the
**technical precondition**: "Is the element present, visible, clickable?"

```
Flow for VerifyValue:

1. _wait_before("read")     ← Sync timeouts (OKW_SYNC_TIMEOUT_READ)
   └── exists? visible?        Ensures the element is ready

2. Verify loop               ← Verify timeout (OKW_TIMEOUT_VERIFY_VALUE)
   └── Read value, compare, repeat if needed
       until match or timeout
```

Both timeout groups are independently configurable and add up in the
worst case.

---

## Ignore Rule (${OKW_IGNORE_EMPTY})

Controls whether empty values (`""`, whitespace only) are interpreted as
"do nothing". Useful for data-driven tests where not every field is filled
in every data set:

```robotframework
*** Settings ***
Library    okw_web_selenium.library.OkwWebSeleniumLibrary

*** Variables ***
${OKW_IGNORE_EMPTY}    YES

*** Test Cases ***
Data-Driven Test
    [Template]    Fill Fields
    Max       Smith       max@test.com
    Anna      ${EMPTY}    anna@test.com

*** Keywords ***
Fill Fields
    [Arguments]    ${first_name}    ${last_name}    ${email}
    SetValue    First Name    ${first_name}
    # For "Anna", SetValue for Last Name is skipped (No-Op)
    SetValue    Last Name     ${last_name}
    SetValue    Email         ${email}
```

Accepted values: `YES`, `NO`, `TRUE`, `FALSE`, `1`, `0`

> **Note:** The special value `$IGNORE` is **always** treated as No-Op,
> regardless of `${OKW_IGNORE_EMPTY}`.

---

## Parameter Reference

### Verify Timeouts (Value Checks)

| Variable | Default | Affected Keywords |
|----------|---------|-------------------|
| `${OKW_TIMEOUT_VERIFY_VALUE}` | 10 | VerifyValue, VerifyValueWCM, VerifyValueREGX |
| `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}` | 10 | VerifyPlaceholder, VerifyPlaceholderWCM, VerifyPlaceholderREGX |
| `${OKW_TIMEOUT_VERIFY_TOOLTIP}` | 10 | VerifyTooltip, VerifyTooltipWCM, VerifyTooltipREGX |
| `${OKW_TIMEOUT_VERIFY_LABEL}` | 10 | VerifyLabel, VerifyLabelWCM, VerifyLabelREGX |
| `${OKW_TIMEOUT_VERIFY_CAPTION}` | 10 | VerifyCaption, VerifyCaptionWCM, VerifyCaptionREGX |
| `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` | 10 | VerifyAttribute |

### Verify Timeouts (State Checks)

| Variable | Default | Affected Keywords |
|----------|---------|-------------------|
| `${OKW_TIMEOUT_VERIFY_EXIST}` | 2.0 | VerifyExist |
| `${OKW_TIMEOUT_VERIFY_VISIBLE}` | 2.0 | VerifyVisible |
| `${OKW_TIMEOUT_VERIFY_ENABLED}` | 2.0 | VerifyEnabled |
| `${OKW_TIMEOUT_VERIFY_EDITABLE}` | 2.0 | VerifyEditable |
| `${OKW_TIMEOUT_VERIFY_FOCUSABLE}` | 2.0 | VerifyFocusable |
| `${OKW_TIMEOUT_VERIFY_CLICKABLE}` | 2.0 | VerifyClickable |
| `${OKW_TIMEOUT_VERIFY_FOCUS}` | 2.0 | VerifyHasFocus |
| `${OKW_TIMEOUT_VERIFY_TABLE}` | 2.0 | VerifyTableCellValue, VerifyTableHeaders |

### Polling and Control

| Variable | Default | Description |
|----------|---------|-------------|
| `${OKW_POLL_VERIFY}` | 0.1 | Poll interval (seconds) for all verify loops |
| `${OKW_IGNORE_EMPTY}` | NO | Globally ignore empty values (No-Op) for Set/Select/TypeKey/Verify* |

### SetOKWParameter Mapping

The keyword `SetOKWParameter` accepts the following names (case-insensitive):

| Name | Sets Variable |
|------|--------------|
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

### Value Formats

Timeouts accept:
- **Integers**: `10` (seconds)
- **Decimals**: `2.5` (seconds)
- **Robot time format**: `10s`, `1 min`, `1 min 30s`, `500 ms`
