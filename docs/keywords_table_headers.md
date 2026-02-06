# Table Verify Keywords — Header-based and REGX variants

Dieser Nachtrag ergänzt die headerbasierten und Regex‑Varianten der Tabellen‑Keywords.
Sie bauen auf den gleichen Token‑ und WCM‑Regeln wie die Basiskommandos auf.

Siehe auch: docs/table_tokens.md für Token‑Definitionen ($TAB, $LF, $EMPTY, …) und Escaping.

---

## Header‑basiert (WCM für Zeilen, exakter Header für Spalten)

- `VerifyTableCellValueByHeaders    <Name>    <RowKeyWCM>    <ColHeaderExact>    <ExpectedWCM>`
  - Wählt eine eindeutige Zeile über ein WCM‑Muster auf der Row‑Key‑Spalte (Standard: erste Spalte) und eine Spalte über exakten Spaltenkopf.
  - `ExpectedWCM` nutzt Wildcards; `$EMPTY` bedeutet leer.
  - Beispiel: `VerifyTableCellValueByHeaders    DemoTable    A2*    Col2    $EMPTY`

- `VerifyTableRowContentByHeader    <Name>    <RowHeaderExact>    <RowKeyWCM>    <RowPatternWCM>`
  - Identifiziert genau eine Zeile über exakten Spaltenkopf + WCM auf dessen Zellen und prüft die ganze Zeile (`$TAB`‑getrennt).
  - Beispiel: `VerifyTableRowContentByHeader    DemoTable    Col1    A31    A31$TABA32$TABA33`

- `VerifyTableColumnContentByHeader    <Name>    <ColHeaderExact>    <ColumnPatternWCM>`
  - Wählt die Spalte über exakten Spaltenkopf und prüft die Datenzeilen (`$LF`‑getrennt).
  - Beispiel: `VerifyTableColumnContentByHeader    DemoTable    Col2    A12$LF$EMPTY$LFA32`

---

## Regex‑Varianten

- `VerifyTableCellValueByHeadersREGX    <Name>    <RowKeyWCM>    <ColHeaderExact>    <ExpectedRegex>`
  - Wie oben, aber der Sollwert wird per Regex (Python `re.search`) geprüft; `$EMPTY` verlangt leere Zelle.
  - Beispiel: `VerifyTableCellValueByHeadersREGX    DemoTable    A3*    Col2    ^A3\d$`

- `VerifyTableRowContentByHeaderREGX    <Name>    <RowHeaderExact>    <RowKeyWCM>    <RowRegexes>`
  - Wie oben, aber jede Zelle der Zeile wird per Regex geprüft (`$TAB`‑getrennt). `$EMPTY` verlangt leere Zelle.
  - Beispiel: `VerifyTableRowContentByHeaderREGX    DemoTable    Col1    A31    ^A31$ $TAB ^A3\d$ $TAB ^A3\d$`

- `VerifyTableColumnContentByHeaderREGX    <Name>    <ColHeaderExact>    <ColumnRegexes>`
  - Wie oben, aber jede Zelle der Spalte wird per Regex geprüft (`$LF`‑getrennt). `$EMPTY` verlangt leere Zelle.
  - Beispiel: `VerifyTableColumnContentByHeaderREGX    DemoTable    Col3    ^A1\d$ $LF ^A2\d$ $LF ^A3\d$`

---

## Zeitsteuerung & Eindeutigkeit

- Alle Keywords nutzen `${OKW_TIMEOUT_VERIFY_TABLE}` (Default z. B. 2s) und `${OKW_POLL_VERIFY}` (Default 0.1s).
- Zeilenselektion muss eindeutig sein (0 oder >1 Treffer führen zu einem Fehler).
- Spaltenköpfe werden exakt gematcht (case‑sensitiv). 

Hinweis zu Regex in Robot
- In Robot‑Tabellen können Backslashes als Escape behandelt werden. Verwende nach Möglichkeit klassen wie `[0-9]` statt `\d`, oder escapen doppelt (z. B. `^A3\\d$`).
 - Achte darauf, um Token‑Separatoren wie `$TAB`/`$LF` keine Leerzeichen zu setzen: Schreibe z. B. `^A31$$TAB^A3[0-9]$` statt `^A31$ $TAB ^A3[0-9]$`.
