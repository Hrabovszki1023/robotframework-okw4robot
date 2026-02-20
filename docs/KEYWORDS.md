# OKW4Robot – KEYWORDS

Diese Datei fasst alle Keywords zusammen und dient als **Contract-Referenz**
fuer `robotframework-okw4robot`.

> Ziel: **technik-unabhaengige Keywords** – die konkrete Umsetzung erfolgt im jeweiligen Treiber-Paket (z.B. okw-web-selenium, okw-java-swing).

---

## 1. Aktionen ohne Eingabewert

Aktionen, die keine Werte übergeben bekommen (z. B. Klicks/Fokus).

- `ClickOn    <Name>`
- `DoubleClickOn    <Name>`
- `SetFocus    <Name>`

**Unterstützte Widgets (aus Doku):** Button, TextField, MultilineField, CheckBox,  
(Fokus: zusätzlich Label, ComboBox, RadioList, ListBox)

---

## 2. Aktionen mit Eingabewert

Aktionen, die einen Wert/Parameter benötigen (Eingaben, Auswahlen).

- `SetValue    <Name>    <Value>`
- `Select      <Name>    <Value>`
- `TypeKey     <Name>    <Key>`

Hinweis (aus Doku):
- `TypeKey` ist auf Widget-Ebene nicht zwingend implementiert; das Literal `$DELETE` löscht Inhalte bei textbasierten Widgets.

---

## 3. Verify (wartend, mit Timeout)

Prüfungen warten bis zum Sollzustand oder Timeout (Polling).

### Value
- `VerifyValue        <Name>  <ExpectedExact>`
- `VerifyValueWCM     <Name>  <ExpectedWCM>`
- `VerifyValueREGX    <Name>  <ExpectedRegex>`

### Placeholder
- `VerifyPlaceholder        <Name>  <ExpectedExact>`
- `VerifyPlaceholderWCM     <Name>  <ExpectedWCM>`
- `VerifyPlaceholderREGX    <Name>  <ExpectedRegex>`

### Tooltip
- `VerifyTooltip        <Name>  <ExpectedExact>`
- `VerifyTooltipWCM     <Name>  <ExpectedWCM>`
- `VerifyTooltipREGX    <Name>  <ExpectedRegex>`

### Label
- `VerifyLabel        <Name>  <ExpectedExact>`
- `VerifyLabelWCM     <Name>  <ExpectedWCM>`
- `VerifyLabelREGX    <Name>  <ExpectedRegex>`

### Caption
- `VerifyCaption        <Name>  <ExpectedExact>`
- `VerifyCaptionWCM     <Name>  <ExpectedWCM>`
- `VerifyCaptionREGX    <Name>  <ExpectedRegex>`

### Attribute (beliebige HTML-Attribute)
- `VerifyAttribute        <Name>  <AttributeName>  <ExpectedExact>`
- `VerifyAttributeWCM     <Name>  <AttributeName>  <ExpectedWCM>`
- `VerifyAttributeREGX    <Name>  <AttributeName>  <ExpectedRegex>`

### Exist / Focus
- `VerifyExist     <Name>`
- `VerifyHasFocus  <Name>`

---

## 4. Memorize

Liest Werte/Attribute und speichert sie in Robot-Variablen.

- `MemorizeValue     <Name>  <VarName>`
- `MemorizeTooltip   <Name>  <VarName>`
- `MemorizeLabel     <Name>  <VarName>`
- `MemorizeCaption   <Name>  <VarName>`
- `MemorizeAttribute <Name>  <AttributeName>  <VarName>`

---

## 5. Log

Loggt Werte/Attribute für Diagnosezwecke.

- `LogValue     <Name>`
- `LogTooltip   <Name>`
- `LogLabel     <Name>`
- `LogCaption   <Name>`
- `LogAttribute <Name>  <AttributeName>`

---

## 6. Tabellen (Web)

Tabellen-Verifikationen (nur Web). Syntax/Token siehe Tabellen-Doku.

### Basis (Index-basiert; 1-basiert, Header ist Zeile 0)
- `VerifyTableCellValue      <Name>  <Row>  <Col>  <ExpectedWCM>`
- `VerifyTableRowContent     <Name>  <Row>  <RowPatternWCM>`
- `VerifyTableColumnContent  <Name>  <Col>  <ColumnPatternWCM>`
- `VerifyTableRowCount       <Name>  <ExpectedCount>`
- `VerifyTableColumnCount    <Name>  <ExpectedCount>`
- `VerifyTableHasRow         <Name>  <RowPatternWCM>`
- `VerifyTableContent        <Name>  <TablePatternWCM>`

### Header-basiert
- `VerifyTableCellValueByHeaders     <Name>  <RowKeyWCM>  <ColHeaderExact>  <ExpectedWCM>`
- `VerifyTableRowContentByHeader     <Name>  <RowHeaderExact>  <RowKeyWCM>  <RowPatternWCM>`
- `VerifyTableColumnContentByHeader  <Name>  <ColHeaderExact>  <ColumnPatternWCM>`

### Regex-Varianten
- `VerifyTableCellValueByHeadersREGX     <Name>  <RowKeyWCM>  <ColHeaderExact>  <ExpectedRegex>`
- `VerifyTableRowContentByHeaderREGX     <Name>  <RowHeaderExact>  <RowKeyWCM>  <RowRegexes>`
- `VerifyTableColumnContentByHeaderREGX  <Name>  <ColHeaderExact>  <ColumnRegexes>`

---

## 7. Listen (Web)

- `VerifyListCount     <Name>  <ExpectedCount>`
- `VerifySelectedCount <Name>  <ExpectedCount>`

---

## 8. Host / App / Window (Kontext-Keywords)

Diese Keywords steuern den Ausführungskontext (Host/App/Window), siehe Kontext-Doku.

- `StartHost     <Host>`
- `StopHost      <Host>`
- `StartApp      <App>`
- `StopApp       <App>`
- `SelectHost    <Host>`
- `SelectWindow  <Window>`

---

## Begriffs-/Semantik-Hinweise (aus Doku)

- **WCM**: Wildcards `*` (beliebige Sequenz), `?` (ein Zeichen).
- **REGX**: Regular Expressions; in Robot ggf. Backslashes doppelt escapen.
- **Label**: Feldbeschriftung (z. B. via `aria-labelledby`, `<label for=…>`, `aria-label`, Fallback Text).
- **Caption**: sichtbarer Text des Elements selbst (nicht Label, nicht Value).
- **Tooltip**: aus `title`, Fallback `aria-label`.
- **Placeholder**: aus `placeholder` (bei nativen `<select>` in der Regel leer).
