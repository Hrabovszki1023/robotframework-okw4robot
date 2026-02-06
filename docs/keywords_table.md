# Table Verify Keywords

Diese Seite dokumentiert die Tabellen‑bezogenen Verify‑Keywords und ihre Muster‑Syntax.

Siehe auch: `docs/table_tokens.md` für Token‑Definitionen ($TAB, $LF, $EMPTY, …) und Escaping.

---

## Grundlagen

- `row`/`col` sind 1‑basiert.
- Header‑Unterstützung:
  - `VerifyTableRowContent` mit `row=0` prüft die Spaltenüberschriften (Header), sofern vorhanden.
  - `VerifyTableCellValue` unterstützt `row=0` für Header‑Zellen.
  - Spalten‑ und Tabellen‑Vergleiche (Column/Content) beziehen sich auf Datenzeilen (Header ausgeschlossen).
- Wildcards (WCM) sind erlaubt: `*` (beliebig viele Zeichen), `?` (ein Zeichen).
- Tokens (standard): `$TAB` (Zellen trennt), `$LF` (Zeilen trennt), `$EMPTY` (leere Zelle), `$EMPTYCOL`, `$EMPTYTABLE`.
- Literal‑Tokens mit Backslash escapen (z. B. `\$TAB`).

Timeout: Alle Table‑Keywords verwenden `${OKW_TIMEOUT_VERIFY_TABLE}` (Default z. B. 2.0 s) und `${OKW_POLL_VERIFY}` (Default 0.1 s) für Polling bis zum Sollzustand.

---

## Keywords

- `VerifyTableCellValue    <Name>    <Row>    <Col>    <Expected>`
  - Prüft den Zellenwert (Header: `Row=0`).
  - Beispiel: `VerifyTableCellValue    DemoTable    2    2    $EMPTY`

- `VerifyTableRowContent   <Name>    <Row>    <RowPattern>`
  - Prüft eine komplette Zeile; Zellen per `$TAB` trennen; `Row=0` prüft Header.
  - Beispiel: `VerifyTableRowContent    DemoTable    2    A21$TAB$EMPTY$TABA23`

- `VerifyTableColumnContent   <Name>    <Col>    <ColumnPattern>`
  - Prüft eine komplette Spalte (Datenzeilen); Zeilen per `$LF` trennen.
  - Beispiel: `VerifyTableColumnContent    DemoTable    2    A12$LF$EMPTY$LFA32`

- `VerifyTableRowCount    <Name>    <ExpectedCount>`
  - Anzahl der Datenzeilen (ohne Header).
  - Beispiel: `VerifyTableRowCount    DemoTable    3`

- `VerifyTableColumnCount    <Name>    <ExpectedCount>`
  - Anzahl der Spalten (aus Header abgeleitet, sonst Maximum der Datenzeilen).
  - Beispiel: `VerifyTableColumnCount    DemoTable    3`

- `VerifyTableHasRow    <Name>    <RowPattern>`
  - Prüft, dass mindestens eine Datenzeile dem Muster entspricht; Zellen per `$TAB` trennen.
  - Beispiel: `VerifyTableHasRow    DemoTable    A21$TAB$EMPTY$TABA23`

- `VerifyTableContent    <Name>    <TablePattern>`
  - Prüft den gesamten Tabelleninhalt (nur Datenzeilen): Zeilen per `$LF`, Zellen per `$TAB`.
  - Beispiel: `VerifyTableContent    DemoTable    A11$TABA12$TABA13$LFA21$TAB$EMPTY$TABA23$LFA31$TABA32$TABA33`

---

## Code‑Referenzen

- Keywords: `src/okw4robot/keywords/table_keywords.py`
- Widget: `src/okw4robot/widgets/common/table.py`
- Tokens/Parser: `src/okw4robot/utils/table_tokens.py`, `docs/table_tokens.md`
