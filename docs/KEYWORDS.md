# OKW4Robot – KEYWORDS

Diese Datei fasst alle Keywords zusammen und dient als **Contract-Referenz**
fuer `robotframework-okw4robot`.

> Ziel: **technik-unabhaengige Keywords** – die konkrete Umsetzung erfolgt im jeweiligen Treiber-Paket (z.B. okw-web-selenium, okw-java-remoteswing).

---

## 1. Aktionen ohne Eingabewert

Aktionen, die keine Werte übergeben bekommen (z. B. Klicks/Fokus/Hover).

- `ClickOn       <Name>`
- `DoubleClickOn <Name>`
- `MoveOver      <Name>`
- `SetFocus      <Name>`
- `DragTo        <Source>  <Target>`
- `DragStart     <Name>`
- `DragOver      <Name>`
- `Drop          <Name>`

### MoveOver

Bewegt den Mauszeiger ueber ein Widget (Hover), ohne zu klicken.
Nuetzlich, um versteckte Elemente sichtbar zu machen, die erst bei
Mouse-Hover erscheinen (Tooltips, Overlays, Dropdown-Menues).

```robot
SelectWindow   HoversPage
MoveOver       Avatar1
VerifyValue    Username1    user1
```

**Widget-Methode:** `okw_move_over()`
**Pre-Condition:** `_pre_read()` (exists)
**Screenshots:** Vorher/Nachher automatisch im Robot Log

**Unterstützte Widgets (aus Doku):** Button, TextField, MultilineField, CheckBox,  
(Fokus: zusätzlich Label, ComboBox, RadioList, ListBox)

### Drag & Drop

Drag-&-Drop-Keywords folgen dem **Collect → Execute**-Pattern:
`DragStart` und `DragOver` sind vorbereitend (sammeln nur Element-Referenzen).
Erst `Drop` fuehrt die gesamte Drag-Sequenz atomar aus.

- `DragTo       <Source>  <Target>`
- `DragStart    <Name>`
- `DragOver     <Name>`
- `Drop         <Name>`

**DragTo** ist der Shortcut fuer den einfachen Fall (Source direkt auf Target,
keine Zwischenstopps):

```robot
SelectWindow   DragDropPage
DragTo         SpalteA    SpalteB
VerifyValue    SpalteA    B
VerifyValue    SpalteB    A
```

**DragStart + DragOver + Drop** fuer Szenarien mit Zwischenzielen
(z.B. TreeView-Knoten aufklappen waehrend des Ziehens):

```robot
SelectWindow   TreeView
DragStart      SourceNode
DragOver       FolderNode1
DragOver       FolderNode2
Drop           TargetNode
```

**Widget-Methoden:** `okw_drag_start()`, `okw_drag_over()`, `okw_drop()`
**Pre-Condition:** `_pre_read()` (exists) fuer alle drei; `Drop` fuehrt aus
**Screenshots:** Vorher/Nachher bei `Drop` und `DragTo`
**Adapter:** JS-basierte HTML5-Event-Simulation (DragEvent + DataTransfer)

---

## 2. Aktionen mit Eingabewert

Aktionen, die einen Wert/Parameter benötigen (Eingaben, Auswahlen).

- `SetValue    <Name>    <Value>`
- `Select      <Name>    <Value>`
- `SelectMenu  <Name>    [Value]`
- `Delete      <Name>`
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

### Exist / State
- `VerifyExists       <Name>  <YES/NO>`
- `VerifyHasFocus     <Name>  <YES/NO>`
- `VerifyIsVisible    <Name>  <YES/NO>`
- `VerifyIsEnabled    <Name>  <YES/NO>`
- `VerifyIsEditable   <Name>  <YES/NO>`
- `VerifyIsFocusable  <Name>  <YES/NO>`
- `VerifyIsClickable  <Name>  <YES/NO>`

---

## 4. Memorize

Liest Werte/Attribute und speichert sie in Robot-Variablen.

- `MemorizeValue     <Name>  <VarName>`
- `MemorizeTooltip   <Name>  <VarName>`
- `MemorizeLabel     <Name>  <VarName>`
- `MemorizeCaption   <Name>  <VarName>`
- `MemorizePlaceholder <Name>  <VarName>`
- `MemorizeAttribute   <Name>  <AttributeName>  <VarName>`

---

## 5. Log

Loggt Werte/Attribute für Diagnosezwecke.

- `LogValue     <Name>`
- `LogTooltip   <Name>`
- `LogLabel     <Name>`
- `LogCaption   <Name>`
- `LogAttribute <Name>  <AttributeName>`

---

## 6. Tabellen

Tabellen-Keywords (technologieuebergreifend). Syntax/Token siehe `docs/table_tokens.md`.

### Click (Zellen anklicken)
- `ClickOnTableCell                 <Name>  <Row>  <Col>`
- `ClickOnTableCellByHeaders        <Name>  <RowKeyWCM>  <ColHeaderExact>`
- `DoubleClickOnTableCell           <Name>  <Row>  <Col>`
- `DoubleClickOnTableCellByHeaders  <Name>  <RowKeyWCM>  <ColHeaderExact>`

### Set (Werte schreiben)
- `SetTableCellValue            <Name>  <Row>  <Col>  <Value>`
- `SetTableCellValueByHeaders   <Name>  <RowKeyWCM>  <ColHeaderExact>  <Value>`

### Log (Zellwert loggen)
- `LogTableCellValue            <Name>  <Row>  <Col>`
- `LogTableCellValueByHeaders   <Name>  <RowKeyWCM>  <ColHeaderExact>`

### Memorize (Zellwert merken)
- `MemorizeTableCellValue            <Name>  <Row>  <Col>  <VarName>`
- `MemorizeTableCellValueByHeaders   <Name>  <RowKeyWCM>  <ColHeaderExact>  <VarName>`

### Verify -- Basis (Index-basiert; 1-basiert, Header ist Zeile 0)
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

## 7. Listen

- `VerifyListCount     <Name>  <ExpectedCount>`
- `VerifySelectedCount <Name>  <ExpectedCount>`

---

## 8. Fail-Klassifizierung (NOISE / FAIL)

- `OnFailNOISE          <Keyword>    [Param1]    [Param2]    ...`
- `OnFailIgnoreNOISE    <Keyword>    [Param1]    [Param2]    ...`

`OnFailNOISE` wraps ein beliebiges Keyword. Bei Fehler wird die Meldung
mit `[N]` (NOISE) prefixed statt `[X]` (FAIL). Fuer Vorbereitungsphasen
(Reset, Umgebung, Navigation).

`OnFailIgnoreNOISE` wraps ein beliebiges Keyword. Bei Fehler wird
`[N][IGNORED]` geloggt und der Test laeuft weiter. Fuer optionale
Vorbereitungsschritte (z.B. Werbung entfernen, Cookie-Banner schliessen).

Siehe [keywords_noise.md](keywords_noise.md).

---

## 9. Host / App / Window (Kontext-Keywords)

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
