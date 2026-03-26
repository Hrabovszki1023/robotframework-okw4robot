# OKW4Robot – Keyword CheatSheet

> Compact reference for all OKW4Robot keywords.
> Full documentation: [KEYWORDS.md](KEYWORDS.md) · [CONTRACT.md](CONTRACT.md)

---

## 1. Context (Host / App / Window)

| Keyword | Parameters | Description |
|---|---|---|
| `StartHost` | `<Host>` | Start host adapter (from YAML) |
| `SelectHost` | `<Host>` | Verify active host |
| `StopHost` | | Stop active host |
| `StartApp` | `<App>` `[Config]` | Load app model (from YAML), auto-start adapter |
| `SelectWindow` | `<Window>` | Set active window context |
| `StopApp` | `[App]` | Stop active app |

```robot
*** Test Cases ***
Login erfolgreich
    StartApp       web/LoginApp
    SelectWindow   LoginDialog
    SetValue       Benutzer       admin
    SetValue       Passwort       geheim
    ClickOn        OK
    StopApp
```

---

## 2. Actions

| Keyword | Parameters | Description |
|---|---|---|
| `ClickOn` | `<Name>` | Click widget |
| `DoubleClickOn` | `<Name>` `[Value]` | Double-click widget (or entry within) |
| `SetValue` | `<Name>` `<Value>` | Set widget value |
| `Select` | `<Name>` `<Value>` | Select option (ComboBox, ListBox, ...) |
| `SelectMenu` | `<Name>` `[Value]` | Select menu item; with value: idempotent |
| `TypeKey` | `<Name>` `<Key>` | Type text/keys (appends, does not overwrite) |
| `Delete` | `<Name>` | Clear widget content |
| `SetFocus` | `<Name>` | Set keyboard focus |

### SelectMenu Details

```robot
SelectMenu    DateiNeu                          # click (JMenuItem)
SelectMenu    Statusleiste                      # toggle (JCheckBoxMenuItem)
SelectMenu    Statusleiste       Checked        # idempotent set
SelectMenu    Statusleiste       Unchecked      # idempotent unset
SelectMenu    AnsichtKompakt                    # select (JRadioButtonMenuItem)
```

---

## 3. Verify (with timeout polling)

### Value / Caption / Label / Tooltip / Placeholder

Each property has three match modes:

| Suffix | Mode | Example Pattern |
|---|---|---|
| _(none)_ | EXACT | `Hello World` |
| `WCM` | Wildcard | `Hello*` · `H?llo` |
| `REGX` | Regex | `Hello\s+\w+` |

| Keyword Pattern | Parameters |
|---|---|
| `Verify<Property>` | `<Name>` `<Expected>` |
| `Verify<Property>WCM` | `<Name>` `<WildcardPattern>` |
| `Verify<Property>REGX` | `<Name>` `<RegexPattern>` |

Where `<Property>` is one of:

| Property | Widget Method | Reads... |
|---|---|---|
| `Value` | `okw_get_value()` | Current value/content |
| `Caption` | `okw_get_text()` | Visible text (button label, menu text) |
| `Label` | `okw_get_label()` | Field label (associated `<label>`) |
| `Tooltip` | `okw_get_tooltip()` | Tooltip text |
| `Placeholder` | `okw_get_placeholder()` | Placeholder text |

```robot
VerifyValue        Benutzer       admin
VerifyValueWCM     Benutzer       adm*
VerifyValueREGX    Benutzer       ^adm.*$
VerifyCaption      BtnOK          OK
VerifyTooltipWCM   BtnSave        *speichern*
```

### Attribute

| Keyword | Parameters |
|---|---|
| `VerifyAttribute` | `<Name>` `<AttrName>` `<Expected>` |
| `VerifyAttributeWCM` | `<Name>` `<AttrName>` `<WildcardPattern>` |
| `VerifyAttributeREGX` | `<Name>` `<AttrName>` `<RegexPattern>` |

### State (YES/NO)

| Keyword | Parameters | Checks... |
|---|---|---|
| `VerifyExist` | `<Name>` `YES/NO` | Widget exists in UI |
| `VerifyHasFocus` | `<Name>` `YES/NO` | Widget has keyboard focus |
| `VerifyIsVisible` | `<Name>` `YES/NO` | Widget is visible |
| `VerifyIsEnabled` | `<Name>` `YES/NO` | Widget is enabled |
| `VerifyIsEditable` | `<Name>` `YES/NO` | Widget is editable |
| `VerifyIsFocusable` | `<Name>` `YES/NO` | Widget is focusable |
| `VerifyIsClickable` | `<Name>` `YES/NO` | Widget is clickable |

```robot
VerifyExist       LoginButton    YES
VerifyIsEnabled   Submit         NO
VerifyHasFocus    Benutzer       YES
```

---

## 4. Memorize & Log

| Keyword Pattern | Parameters | Purpose |
|---|---|---|
| `Memorize<Property>` | `<Name>` `<VarName>` | Store value in `${VarName}` |
| `Log<Property>` | `<Name>` | Log value to console |

Where `<Property>`: `Value`, `Caption`, `Label`, `Tooltip`, `Placeholder`

Special: `MemorizeAttribute` / `LogAttribute` take an additional `<AttrName>` parameter.

```robot
MemorizeValue      Benutzer       SAVED_USER
VerifyValue        Anzeige        ${SAVED_USER}
LogCaption         BtnOK
```

---

## 5. Lists

| Keyword | Parameters | Description |
|---|---|---|
| `VerifyListCount` | `<Name>` `<Count>` | Verify number of items |
| `VerifySelectedCount` | `<Name>` `<Count>` | Verify number of selected items |

---

## 6. Tables

### Index-based (1-based, header = row 0)

| Keyword | Parameters |
|---|---|
| `VerifyTableCellValue` | `<Name>` `<Row>` `<Col>` `<Expected>` |
| `VerifyTableRowContent` | `<Name>` `<Row>` `<RowPattern>` |
| `VerifyTableColumnContent` | `<Name>` `<Col>` `<ColPattern>` |
| `VerifyTableRowCount` | `<Name>` `<Count>` |
| `VerifyTableColumnCount` | `<Name>` `<Count>` |
| `VerifyTableHasRow` | `<Name>` `<RowPattern>` |
| `VerifyTableContent` | `<Name>` `<TablePattern>` |

### Click (select cells)

| Keyword | Parameters |
|---|---|
| `ClickOnTableCell` | `<Name>` `<Row>` `<Col>` |
| `ClickOnTableCellByHeaders` | `<Name>` `<RowKey>` `<ColHeader>` |

```robot
ClickOnTableCell            tblPersonen    2    1
ClickOnTableCellByHeaders   tblPersonen    Mueller    Stadt
```

### Set (write values into cells)

| Keyword | Parameters |
|---|---|
| `SetTableCellValue` | `<Name>` `<Row>` `<Col>` `<Value>` |
| `SetTableCellValueByHeaders` | `<Name>` `<RowKey>` `<ColHeader>` `<Value>` |

`$DELETE` and `$EMPTY` clear the cell. `$IGNORE` skips.

```robot
SetTableCellValue           tblPersonen    1    3    Koeln
SetTableCellValueByHeaders  tblPersonen    Mueller    Stadt    Koeln
```

### Header-based (Verify)

| Keyword | Parameters |
|---|---|
| `VerifyTableCellValueByHeaders` | `<Name>` `<RowKey>` `<ColHeader>` `<Expected>` |
| `VerifyTableRowContentByHeader` | `<Name>` `<RowHeader>` `<RowKey>` `<RowPattern>` |
| `VerifyTableColumnContentByHeader` | `<Name>` `<ColHeader>` `<ColPattern>` |

REGX variants: append `REGX` to any header-based keyword.

---

## 7. Global Tokens

Tokens are **case-insensitive** and evaluated after Robot variable expansion.

| Token | Effect | Use with |
|---|---|---|
| `$IGNORE` | Keyword becomes no-op (PASS) | SetValue, Select, TypeKey, Verify* |
| `$EMPTY` | Target value is empty string | SetValue |
| `$DELETE` | Clear/delete content | TypeKey |

```robot
*** Variables ***
${IGNORE}    $IGNORE
${EMPTY}     $EMPTY
${DELETE}    $DELETE

*** Test Cases ***
Optionale Felder ueberspringen
    SetValue       Pflichtfeld    Wert
    SetValue       Optional       ${IGNORE}      # skipped
    TypeKey        Kommentar      ${DELETE}       # cleared
    VerifyValue    Pflichtfeld    Wert
    VerifyValue    Optional       ${IGNORE}      # skipped
```

---

## 8. Match Modes

| Mode | Suffix | Syntax | Example |
|---|---|---|---|
| EXACT | _(none)_ | Exact string equality | `Hello World` |
| WCM | `WCM` | `*` = any chars, `?` = one char | `Hello*`, `H?llo` |
| REGX | `REGX` | Python regex (`re.search`) | `^Hello\s+\w+$` |

Newlines are normalized (`\r\n` → `\n`) before matching.

---

## 9. YES/NO Model

For state-verification keywords (`VerifyExist`, `VerifyIsEnabled`, ...):

| Input | Parsed as |
|---|---|
| `YES`, `TRUE`, `1` | Must be true |
| `NO`, `FALSE`, `0` | Must be false |

---

## 10. Value Expansion

`$MEM{KEY}` placeholders are replaced from an in-memory store.
Missing keys raise an immediate error.

```
ssh $MEM{USER}@$MEM{HOST}  →  ssh admin@10.0.0.1
```

---

## 11. YAML Locator Quick Reference

```yaml
AppName:
  __self__:
    class: okw_web_selenium.adapters.SeleniumWebAdapter
  __configs__:
    staging:
      base_url: https://staging.example.com

  WindowName:
    WidgetName:
      class: <technology>.widgets.<WidgetClass>
      locator: { <strategy>: <value> }
      label_for: <target>          # optional: label → input
      tooltip: "Tooltip text"      # optional: expected tooltip
      menu_path: "Datei|Speichern" # menu items only
```

### Locator Strategies

| Strategy | Technology | Example |
|---|---|---|
| `id` | Web | `locator: { id: loginBtn }` |
| `css` | Web | `locator: { css: "input.email" }` |
| `xpath` | Web | `locator: { xpath: "//div[@role='button']" }` |
| `name` | Swing | `locator: { name: txtName }` |

---

## 12. Timeout Configuration

| Variable | Default | Used by |
|---|---|---|
| `${OKW_TIMEOUT_VERIFY_VALUE}` | 10s | VerifyValue, VerifyCaption, ... |
| `${OKW_TIMEOUT_VERIFY_EXIST}` | 2s | VerifyExist |
| `${OKW_TIMEOUT_VERIFY_FOCUS}` | 2s | VerifyHasFocus |
| `${OKW_TIMEOUT_VERIFY_VISIBLE}` | 2s | VerifyIsVisible |
| `${OKW_TIMEOUT_VERIFY_ENABLED}` | 2s | VerifyIsEnabled |
| `${OKW_TIMEOUT_VERIFY_EDITABLE}` | 2s | VerifyIsEditable |
| `${OKW_TIMEOUT_VERIFY_FOCUSABLE}` | 2s | VerifyIsFocusable |
| `${OKW_TIMEOUT_VERIFY_CLICKABLE}` | 2s | VerifyIsClickable |
| `${OKW_POLL_VERIFY}` | 0.1s | Poll interval for all Verify* |

```robot
*** Settings ***
Suite Setup    Set Suite Variable    ${OKW_TIMEOUT_VERIFY_VALUE}    20s
```
