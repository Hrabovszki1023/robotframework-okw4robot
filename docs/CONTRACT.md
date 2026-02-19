# CONTRACT – robotframework-okw4robot

This document defines the public contract of `robotframework-okw4robot`.

## Library Import

```robot
Library    okw4robot.library.OKW4RobotLibrary
```

---

## Keywords (Public API)

### Host Lifecycle

| Keyword       | Parameters      | Description |
|---------------|----------------|-------------|
| `StartHost`   | `<name>`        | Loads the host YAML (`locators/<name>.yaml`), instantiates the adapter (e.g. Selenium) and registers it in the global Context. |
| `SelectHost`  | `<name>`        | Asserts that the named host/adapter is currently active. |
| `StopHost`    |                 | Stops the active host/adapter and clears the Context. |

### App Lifecycle

| Keyword        | Parameters      | Description |
|----------------|----------------|-------------|
| `StartApp`     | `<name>`        | Loads the app YAML (`locators/<name>.yaml`), sets the active app model in the Context. |
| `SelectWindow` | `<name>`        | Selects the named window/view from the active app model. All widget keywords operate on this window. |
| `StopApp`      |                 | Clears the active app context. |

### Widget – Write / Interact

| Keyword         | Parameters          | Description |
|-----------------|---------------------|-------------|
| `SetValue`      | `<name>` `<value>`  | Sets the value of a widget. Delegates to `okw_set_value(value)`. |
| `Select`        | `<name>` `<value>`  | Selects a value/option on a widget. Delegates to `okw_select(value)`. |
| `TypeKey`       | `<name>` `<key>`    | Simulates keyboard input. Delegates to `okw_type_key(key)`. |
| `ClickOn`       | `<name>`            | Clicks a widget. Delegates to `okw_click()`. |
| `DoubleClickOn` | `<name>`            | Double-clicks a widget. Delegates to `okw_double_click()`. |
| `SetFocus`      | `<name>`            | Moves keyboard focus to a widget via `adapter.focus(locator)`. |

### Widget – Verify Value

| Keyword           | Parameters                | Default | Description |
|-------------------|--------------------------|---------|-------------|
| `VerifyValue`     | `<name>` `<expected>`    |         | EXACT match on widget value. |
| `VerifyValueWCM`  | `<name>` `<pattern>`     |         | Wildcard match (`*` = any chars, `?` = one char). |
| `VerifyValueREGX` | `<name>` `<regex>`       |         | Regex match (Python `re.search`, not anchored). |

Timeout: `${OKW_TIMEOUT_VERIFY_VALUE}` (default: 10s).

### Widget – Verify State

| Keyword             | Parameters              | Default | Description |
|---------------------|------------------------|---------|-------------|
| `VerifyExist`       | `<name>` `<expected>`  |         | Asserts element exists (`YES`) or not (`NO`). |
| `VerifyIsVisible`   | `<name>` `<expected>`  |         | Asserts element is visible (`YES`) or not (`NO`). |
| `VerifyIsEnabled`   | `<name>` `<expected>`  |         | Asserts element is enabled (`YES`) or not (`NO`). |
| `VerifyIsEditable`  | `<name>` `<expected>`  |         | Asserts element is editable (`YES`) or not (`NO`). |
| `VerifyIsFocusable` | `<name>` `<expected>`  |         | Asserts element is focusable (`YES`) or not (`NO`). |
| `VerifyIsClickable` | `<name>` `<expected>`  |         | Asserts element is clickable (`YES`) or not (`NO`). |
| `VerifyHasFocus`    | `<name>` `<expected>`  |         | Asserts element has keyboard focus (`YES`) or not (`NO`). |

The `expected` parameter accepts `YES`/`NO`, `TRUE`/`FALSE`, or `1`/`0` (case-insensitive).
Timeouts: `${OKW_TIMEOUT_VERIFY_EXIST}`, `${OKW_TIMEOUT_VERIFY_VISIBLE}`, etc. (default: 2s).

### Widget – Memorize / Log

| Keyword         | Parameters                    | Description |
|-----------------|------------------------------|-------------|
| `MemorizeValue` | `<name>` `<variable>`        | Stores the widget value in `${variable}` via `Set Test Variable`. |
| `LogValue`      | `<name>`                     | Logs the current widget value. |
| `HasValue`      | `<name>`                     | Checks if the widget has a value (widget-specific). |

### Caption (visible element text)

| Keyword            | Parameters                | Default | Description |
|--------------------|--------------------------|---------|-------------|
| `VerifyCaption`    | `<name>` `<expected>`    |         | EXACT match on element text. |
| `VerifyCaptionWCM` | `<name>` `<pattern>`     |         | Wildcard match on element text. |
| `VerifyCaptionREGX`| `<name>` `<regex>`       |         | Regex match on element text. |
| `MemorizeCaption`  | `<name>` `<variable>`    |         | Stores element text in `${variable}`. |
| `LogCaption`       | `<name>`                 |         | Logs element text. |

Timeout: `${OKW_TIMEOUT_VERIFY_CAPTION}` (default: 10s).

### Label (associated label text)

| Keyword           | Parameters                | Default | Description |
|-------------------|--------------------------|---------|-------------|
| `VerifyLabel`     | `<name>` `<expected>`    |         | EXACT match on label text (aria-labelledby → label[for] → aria-label → own text). |
| `VerifyLabelWCM`  | `<name>` `<pattern>`     |         | Wildcard match on label text. |
| `VerifyLabelREGX` | `<name>` `<regex>`       |         | Regex match on label text. |
| `MemorizeLabel`   | `<name>` `<variable>`    |         | Stores label text in `${variable}`. |
| `LogLabel`        | `<name>`                 |         | Logs label text. |

Timeout: `${OKW_TIMEOUT_VERIFY_LABEL}` (default: 10s).

### Tooltip

| Keyword             | Parameters                | Default | Description |
|---------------------|--------------------------|---------|-------------|
| `VerifyTooltip`     | `<name>` `<expected>`    |         | EXACT match on tooltip (`title` attr, fallback `aria-label`). |
| `VerifyTooltipWCM`  | `<name>` `<pattern>`     |         | Wildcard match on tooltip. |
| `VerifyTooltipREGX` | `<name>` `<regex>`       |         | Regex match on tooltip. |
| `MemorizeTooltip`   | `<name>` `<variable>`    |         | Stores tooltip in `${variable}`. |
| `LogTooltip`        | `<name>`                 |         | Logs tooltip text. |

Timeout: `${OKW_TIMEOUT_VERIFY_TOOLTIP}` (default: 10s).

### Attribute (HTML element attribute)

| Keyword               | Parameters                           | Default | Description |
|-----------------------|-------------------------------------|---------|-------------|
| `VerifyAttribute`     | `<name>` `<attribute>` `<expected>` |         | EXACT match on HTML attribute value. |
| `VerifyAttributeWCM`  | `<name>` `<attribute>` `<pattern>`  |         | Wildcard match on attribute value. |
| `VerifyAttributeREGX` | `<name>` `<attribute>` `<regex>`    |         | Regex match on attribute value. |
| `MemorizeAttribute`   | `<name>` `<attribute>` `<variable>` |         | Stores attribute value in `${variable}`. |
| `LogAttribute`        | `<name>` `<attribute>`              |         | Logs attribute value. |

Timeout: `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}` (default: 10s).

### Placeholder

| Keyword                 | Parameters                | Default | Description |
|-------------------------|--------------------------|---------|-------------|
| `VerifyPlaceholder`     | `<name>` `<expected>`    |         | EXACT match on placeholder text. |
| `VerifyPlaceholderWCM`  | `<name>` `<pattern>`     |         | Wildcard match on placeholder. |
| `VerifyPlaceholderREGX` | `<name>` `<regex>`       |         | Regex match on placeholder. |

Timeout: `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}` (default: 10s).

### List / Selection

| Keyword               | Parameters                    | Description |
|-----------------------|------------------------------|-------------|
| `VerifyListCount`     | `<name>` `<expected_count>`  | Asserts the number of items in a list widget equals `expected_count`. |
| `VerifySelectedCount` | `<name>` `<expected_count>`  | Asserts the number of selected items equals `expected_count`. |

Timeout: `${OKW_TIMEOUT_VERIFY_LIST}` (default: 2s).

### JavaScript (Web only)

| Keyword     | Parameters   | Description |
|-------------|-------------|-------------|
| `ExecuteJS` | `<script>`  | Executes a JavaScript snippet in the browser context (Selenium adapter only). Returns the script result. |

---

## OKW Tokens

| Token      | Supported by              | Behavior |
|------------|--------------------------|----------|
| `$IGNORE`  | All keywords with `value`/`expected` | Keyword is skipped (PASS). No action, no assertion. |
| `$EMPTY`   | `SetValue`               | Sets an explicit empty string. Never ignored even with `${OKW_IGNORE_EMPTY}=YES`. |
| `$DELETE`  | `TypeKey`                | Clears the field content (`clear_text` or CTRL+A + DELETE). |

In Robot syntax: use `${IGNORE}` which expands to `$IGNORE`.

### Global Flag: `${OKW_IGNORE_EMPTY}`

Set to `YES` to treat blank/whitespace values as `$IGNORE` in `SetValue`, `Select`, `TypeKey` and all `Verify*` keywords. Default: `NO`.

```robot
Set Suite Variable    ${OKW_IGNORE_EMPTY}    YES
SetValue              Comment    ${EMPTY}     # ignored
SetValue              Comment    $EMPTY       # NOT ignored – explicitly sets empty string
```

---

## YES/NO Existence Model

All state-verification keywords (`VerifyExist`, `VerifyIsVisible`, etc.) use the OKW YES/NO model:

| Input     | Interpreted as |
|-----------|----------------|
| `YES`, `TRUE`, `1` | Element must be present / active |
| `NO`, `FALSE`, `0` | Element must be absent / inactive |

Input is case-insensitive.

---

## Locator YAML Format

Widgets are described in YAML files loaded by `StartApp`. Structure:

```yaml
# locators/web/LoginApp.yaml
LoginApp:
  LoginDialog:
    Username:
      class: okw4robot.widgets.common.text_field.TextField
      locator: id=user_input
    Password:
      class: okw4robot.widgets.common.text_field.TextField
      locator: id=password_input
    OK:
      class: okw4robot.widgets.common.button.Button
      locator: id=login_btn
    SubmitButton:
      class: okw4robot.widgets.common.button.Button
      locator: css=button[type=submit]
```

---

## Timeout Variables Reference

| Variable                             | Default | Keywords |
|--------------------------------------|---------|---------|
| `${OKW_TIMEOUT_VERIFY_VALUE}`        | 10s     | VerifyValue, VerifyValueWCM, VerifyValueREGX |
| `${OKW_TIMEOUT_VERIFY_EXIST}`        | 2s      | VerifyExist |
| `${OKW_TIMEOUT_VERIFY_VISIBLE}`      | 2s      | VerifyIsVisible |
| `${OKW_TIMEOUT_VERIFY_ENABLED}`      | 2s      | VerifyIsEnabled |
| `${OKW_TIMEOUT_VERIFY_EDITABLE}`     | 2s      | VerifyIsEditable |
| `${OKW_TIMEOUT_VERIFY_FOCUS}`        | 2s      | VerifyHasFocus |
| `${OKW_TIMEOUT_VERIFY_FOCUSABLE}`    | 2s      | VerifyIsFocusable |
| `${OKW_TIMEOUT_VERIFY_CLICKABLE}`    | 2s      | VerifyIsClickable |
| `${OKW_TIMEOUT_VERIFY_CAPTION}`      | 10s     | VerifyCaption, VerifyCaptionWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_LABEL}`        | 10s     | VerifyLabel, VerifyLabelWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_TOOLTIP}`      | 10s     | VerifyTooltip, VerifyTooltipWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_ATTRIBUTE}`    | 10s     | VerifyAttribute, VerifyAttributeWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_PLACEHOLDER}`  | 10s     | VerifyPlaceholder, VerifyPlaceholderWCM/REGX |
| `${OKW_TIMEOUT_VERIFY_LIST}`         | 2s      | VerifyListCount, VerifySelectedCount |
| `${OKW_POLL_VERIFY}`                 | 0.1s    | All Verify keywords (poll interval) |
