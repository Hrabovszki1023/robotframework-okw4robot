# Table Tokens (Parsing Helpers)

Standardized tokens to describe table content in Verify* keywords.

Defaults (override via Robot variables if needed):
- `${OKW_TABLE_CELL_SEP_TOKEN}` = `$TAB` (cell separator within a row)
- `${OKW_TABLE_ROW_SEP_TOKEN}` = `$LF` (row separator)
- `${OKW_TABLE_EMPTY_CELL_TOKEN}` = `$EMPTY` (empty cell)
- `${OKW_TABLE_EMPTY_COL_TOKEN}` = `$EMPTYCOL` (column with no values)
- `${OKW_TABLE_EMPTY_TABLE_TOKEN}` = `$EMPTYTABLE` (no data rows)

Escaping
- Prefix a backslash to treat tokens literally: `\$TAB`, `\$LF`, `\$EMPTY`, …

Examples
- Row content: `Value1$TABValue2$TABValue3`
- Column content: `A$LFB$LFC`
- Whole table (2x2): `Z11$TABZ12$LFZ21$TABZ22`
- Empty cell inside row: `A$TAB$EMPTY$TABC`
- Empty column: `$EMPTYCOL`
- Empty table: `$EMPTYTABLE`
- Literal token in cell: `Text with \$TAB inside$TABok`

Python helpers
- Module: `src/okw4robot/utils/table_tokens.py`
  - `parse_row_pattern(str) -> list[str]`
  - `parse_column_pattern(str) -> list[str]`
  - `parse_table_pattern(str) -> list[list[str]]`
  - `compile_wcm_to_regex(str) -> str`
  - Token lookup: `get_tokens()`; predicates: `is_empty_cell_token`, `is_empty_col_token`, `is_empty_table_token`

Notes
- `$IGNORE` remains a No-Op at keyword level (skip verification).
- `${OKW_IGNORE_EMPTY}` is unrelated to `$EMPTY` token; `$EMPTY` is a content assertion.

