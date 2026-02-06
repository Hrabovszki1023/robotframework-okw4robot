from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.loader import load_class
from ..utils.table_tokens import (
    parse_row_pattern,
    parse_column_pattern,
    compile_wcm_to_regex,
    is_empty_cell_token,
)

def _get_time(var_name: str, default_seconds: float) -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        to = BuiltIn().get_variable_value(var_name, default=default_seconds)
        return float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
    except Exception:
        return float(default_seconds)

def _get_poll() -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        po = BuiltIn().get_variable_value("${OKW_POLL_VERIFY}", default=0.1)
        return float(po) if isinstance(po, (int, float)) else BuiltIn().convert_time(str(po))
    except Exception:
        return 0.1

def _get_time(var_name: str, default_seconds: float) -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        to = BuiltIn().get_variable_value(var_name, default=default_seconds)
        return float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
    except Exception:
        return float(default_seconds)

def _get_poll() -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        po = BuiltIn().get_variable_value("${OKW_POLL_VERIFY}", default=0.1)
        return float(po) if isinstance(po, (int, float)) else BuiltIn().convert_time(str(po))
    except Exception:
        return 0.1


def _resolve_table(name):
    model = context.get_current_window_model()
    if name not in model:
        raise KeyError(f"Table '{name}' not found in current window.")
    entry = model[name]
    widget_class = load_class(entry["class"])
    adapter = context.get_adapter()
    extras = {k: v for k, v in entry.items() if k not in ("class", "locator")}
    return widget_class(adapter, entry.get("locator"), **extras)


def _match_wcm(actual: str, expected: str) -> bool:
    import re
    if expected is None:
        return actual == ""
    # Support wildcard matching by compiling expected to regex
    rx = re.compile(compile_wcm_to_regex(expected), re.DOTALL)
    return bool(rx.match(actual or ""))


def _get_header_names(tbl):
    """Return list of column headers from the table widget.

    Requires the widget to provide a header API. Preferred: ``get_header_names()``.
    If not available, tries ``get_headers()``. Otherwise raises.
    """
    if hasattr(tbl, 'get_header_names'):
        return list(tbl.get_header_names())
    if hasattr(tbl, 'get_headers'):
        return list(tbl.get_headers())
    # fallback: use header row texts if available
    try:
        return list(tbl.get_row_texts(0))
    except Exception:
        pass
    raise RuntimeError("Table widget does not provide header names (expected 'get_header_names').")


def _get_row_key_column_index(tbl) -> int:
    """Return 1-based index of the column used for row key matching.

    Preferred: ``get_row_key_column_index()`` on the widget. Fallback to 1.
    """
    if hasattr(tbl, 'get_row_key_column_index'):
        try:
            idx = int(tbl.get_row_key_column_index())
            return idx if idx >= 1 else 1
        except Exception:
            return 1
    return 1


class TableKeywords:
    @keyword("VerifyTableRowContent")
    def verify_table_row_content(self, name: str, row: int, expected_row_pattern: str):
        """Verifies a row's cell contents using a wildcard pattern list.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row``: 1‑based row index.
        - ``expected_row_pattern``: Cells separated by the table cell token (default ``$TAB``).

        Special tokens / control parameters:
        - Cell separator: ``${OKW_TABLE_CELL_SEP_TOKEN}`` (default ``$TAB``)
        - Empty cell: ``${OKW_TABLE_EMPTY_CELL_TOKEN}`` (default ``$EMPTY``) → treated as ""
        - Wildcards: ``*`` any sequence, ``?`` single character
        - Escaping: prefix a backslash to treat tokens literally (e.g. ``\\$TAB``)

        Behavior:
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        - Expects exact number of cells and per‑cell wildcard match (full‑string, DOTALL).

        Examples:
        | VerifyTableRowContent | Items | 2 | Name$TABPrice$TAB$EMPTY |
        | VerifyTableRowContent | Items | 3 | Foo*$TAB?9.99$TABOK |
        """
        import time
        tbl = _resolve_table(name)
        exp_cells = parse_row_pattern(expected_row_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            act_cells = tbl.get_row_texts(int(row))
            if len(act_cells) == len(exp_cells) and all(_match_wcm(a, e) for a, e in zip(act_cells, exp_cells)):
                return
            last = act_cells
            time.sleep(poll)
        if last is None:
            last = tbl.get_row_texts(int(row))
        if len(last) != len(exp_cells):
            raise AssertionError(f"[VerifyTableRowContent] Row length mismatch: expected {len(exp_cells)}, got {len(last)}")
        for i, (a, e) in enumerate(zip(last, exp_cells), start=1):
            if not _match_wcm(a, e):
                raise AssertionError(f"[VerifyTableRowContent] Cell {i} mismatch: expected '{e}', got '{a}'")

    @keyword("VerifyTableColumnContent")
    def verify_table_column_content(self, name: str, col: int, expected_column_pattern: str):
        """Verifies a column's cell contents using a wildcard pattern list.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``col``: 1‑based column index.
        - ``expected_column_pattern``: Rows separated by the table row token (default ``$LF``).

        Special tokens / control parameters:
        - Row separator: ``${OKW_TABLE_ROW_SEP_TOKEN}`` (default ``$LF``)
        - Empty cell: ``${OKW_TABLE_EMPTY_CELL_TOKEN}`` (default ``$EMPTY``) → treated as ""
        - Empty column: ``${OKW_TABLE_EMPTY_COL_TOKEN}`` (default ``$EMPTYCOL``) → column with zero rows
        - Wildcards: ``*`` any sequence, ``?`` single character
        - Escaping: prefix a backslash to treat tokens literally

        Behavior:
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        - Expects exact number of rows and per‑cell wildcard match (full‑string, DOTALL).

        Examples:
        | VerifyTableColumnContent | Items | 2 | Price$LF9.99$LF$EMPTY |
        | VerifyTableColumnContent | Items | 3 | $EMPTYCOL |
        """
        import time
        tbl = _resolve_table(name)
        exp_rows = parse_column_pattern(expected_column_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            act_rows = tbl.get_column_texts(int(col))
            if len(exp_rows) == len(act_rows) and all(_match_wcm(a, e) for a, e in zip(act_rows, exp_rows)):
                return
            last = act_rows
            time.sleep(poll)
        if last is None:
            last = tbl.get_column_texts(int(col))
        if len(exp_rows) != len(last):
            raise AssertionError(f"[VerifyTableColumnContent] Column length mismatch: expected {len(exp_rows)}, got {len(last)}")
        for i, (a, e) in enumerate(zip(last, exp_rows), start=1):
            if not _match_wcm(a, e):
                raise AssertionError(f"[VerifyTableColumnContent] Row {i} mismatch: expected '{e}', got '{a}'")

    @keyword("VerifyTableCellValue")
    def verify_table_cell_value(self, name: str, row: int, col: int, expected: str):
        """Verifies a single cell value using wildcards; supports the empty‑cell token.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row``: 1‑based row index.
        - ``col``: 1‑based column index.
        - ``expected``: Expected content; ``$EMPTY`` token maps to empty string.

        Special tokens / control parameters:
        - Empty cell: ``${OKW_TABLE_EMPTY_CELL_TOKEN}`` (default ``$EMPTY``)
        - Wildcards: ``*`` any sequence, ``?`` single character

        Behavior:
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        - Full‑string wildcard matching (DOTALL).

        Examples:
        | VerifyTableCellValue | Items | 2 | 3 | $EMPTY |
        | VerifyTableCellValue | Items | 1 | 2 | *9.9? |
        """
        import time
        tbl = _resolve_table(name)
        if is_empty_cell_token(expected):
            expected = ""
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            a = tbl.get_cell_text(int(row), int(col))
            if _match_wcm(a, expected):
                return
            last = a
            time.sleep(poll)
        if last is None:
            last = tbl.get_cell_text(int(row), int(col))
        raise AssertionError(f"[VerifyTableCellValue] Expected '{expected}', got '{last}' at r{row}c{col}")

    @keyword("VerifyTableRowCount")
    def verify_table_row_count(self, name: str, expected_count):
        """Verifies the total number of rows.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``expected_count``: Integer row count.

        Behavior:
        - Polls ``get_row_count()`` until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s).

        Examples:
        | VerifyTableRowCount | Items | 5 |
        """
        import time
        tbl = _resolve_table(name)
        try:
            exp = int(str(expected_count).strip())
        except Exception:
            raise ValueError(f"[VerifyTableRowCount] Expected must be integer, got '{expected_count}'")
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        while time.time() < end:
            got = int(tbl.get_row_count())
            if got == exp:
                return
            time.sleep(poll)
        got = int(tbl.get_row_count())
        raise AssertionError(f"[VerifyTableRowCount] Expected {exp} rows, got {got}")

    @keyword("VerifyTableColumnCount")
    def verify_table_column_count(self, name: str, expected_count):
        """Verifies the total number of columns.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``expected_count``: Integer column count.

        Behavior:
        - Polls ``get_column_count()`` until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s).

        Examples:
        | VerifyTableColumnCount | Items | 3 |
        """
        import time
        tbl = _resolve_table(name)
        try:
            exp = int(str(expected_count).strip())
        except Exception:
            raise ValueError(f"[VerifyTableColumnCount] Expected must be integer, got '{expected_count}'")
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        while time.time() < end:
            got = int(tbl.get_column_count())
            if got == exp:
                return
            time.sleep(poll)
        got = int(tbl.get_column_count())
        raise AssertionError(f"[VerifyTableColumnCount] Expected {exp} columns, got {got}")

    @keyword("VerifyTableHasRow")
    def verify_table_has_row(self, name: str, expected_row_pattern: str):
        """Verifies that at least one row matches the given wildcard pattern list.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``expected_row_pattern``: Cells separated by the cell token (default ``$TAB``).

        Special tokens / control parameters:
        - Cell separator: ``${OKW_TABLE_CELL_SEP_TOKEN}`` (default ``$TAB``)
        - Empty cell: ``${OKW_TABLE_EMPTY_CELL_TOKEN}`` (default ``$EMPTY``)
        - Wildcards: ``*`` any sequence, ``?`` single character

        Behavior:
        - Iterates all rows until a matching row is found; polls until timeout
          ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.

        Examples:
        | VerifyTableHasRow | Items | Foo*$TAB9.99$TABOK |
        """
        import time
        tbl = _resolve_table(name)
        exp_cells = parse_row_pattern(expected_row_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        while time.time() < end:
            rc = tbl.get_row_count()
            for r in range(1, rc + 1):
                act = tbl.get_row_texts(r)
                if len(act) != len(exp_cells):
                    continue
                if all(_match_wcm(a, e) for a, e in zip(act, exp_cells)):
                    return
            time.sleep(poll)
        raise AssertionError("[VerifyTableHasRow] No row matched the expected pattern")

    @keyword("VerifyTableContent")
    def verify_table_content(self, name: str, expected_table_pattern: str):
        """Verifies the entire table content against a wildcard pattern matrix.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``expected_table_pattern``: Table described by rows and cells using tokens.

        Special tokens / control parameters:
        - Row separator: ``${OKW_TABLE_ROW_SEP_TOKEN}`` (default ``$LF``)
        - Cell separator: ``${OKW_TABLE_CELL_SEP_TOKEN}`` (default ``$TAB``)
        - Empty cell: ``${OKW_TABLE_EMPTY_CELL_TOKEN}`` (default ``$EMPTY``)
        - Empty table: ``${OKW_TABLE_EMPTY_TABLE_TOKEN}`` (default ``$EMPTYTABLE``)
        - Wildcards: ``*`` any sequence, ``?`` single character
        - Escaping: prefix a backslash to treat tokens literally

        Behavior:
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        - Expects exact row and column counts to match, and per‑cell wildcard match (full‑string, DOTALL).

        Examples:
        | VerifyTableContent | Items | Name$TABPrice$LFFoo*$TAB9.9?$LF$EMPTY$TABOK |
        | VerifyTableContent | Items | $EMPTYTABLE |
        """
        import time
        from ..utils.table_tokens import parse_table_pattern
        tbl = _resolve_table(name)
        exp_rows = parse_table_pattern(expected_table_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_rows = None
        while time.time() < end:
            rc = tbl.get_row_count()
            act_rows = [tbl.get_row_texts(r) for r in range(1, rc + 1)]
            ok = True
            if len(act_rows) != len(exp_rows):
                ok = False
            else:
                for act, exp in zip(act_rows, exp_rows):
                    if len(act) != len(exp) or any(not _match_wcm(a, e) for a, e in zip(act, exp)):
                        ok = False
                        break
            if ok:
                return
            last_rows = act_rows
            time.sleep(poll)
        if last_rows is None:
            rc = tbl.get_row_count()
            last_rows = [tbl.get_row_texts(r) for r in range(1, rc + 1)]
        if len(last_rows) != len(exp_rows):
            raise AssertionError(f"[VerifyTableContent] Row count mismatch: expected {len(exp_rows)}, got {len(last_rows)}")
        for i, (act, exp) in enumerate(zip(last_rows, exp_rows), start=1):
            if len(act) != len(exp):
                raise AssertionError(f"[VerifyTableContent] Row {i} length mismatch: expected {len(exp)}, got {len(act)}")
            for j, (a, e) in enumerate(zip(act, exp), start=1):
                if not _match_wcm(a, e):
                    raise AssertionError(f"[VerifyTableContent] Mismatch at r{i}c{j}: expected '{e}', got '{a}'")

    @keyword("VerifyTableCellValueByHeaders")
    def verify_table_cell_value_by_headers(self, name: str, row: str, col: str, expected: str):
        """Verifies a single cell selected by row key (WCM) and column header (exact).

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row``: Row key pattern (wildcard match, applied to the row key column).
        - ``col``: Exact column header name (case‑sensitive).
        - ``expected``: Expected content; ``$EMPTY`` token maps to empty string. Wildcards supported.

        Behavior:
        - Uses the row key column (``get_row_key_column_index()`` if provided by the widget; otherwise column 1)
          to find exactly one matching row via wildcard pattern.
        - Resolves the column index by exact header name (via ``get_header_names()``).
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.

        Examples:
        | VerifyTableCellValueByHeaders | Items | ID*123 | Price  | 9.99   |
        | VerifyTableCellValueByHeaders | Items | Kunde* | Status | $EMPTY |
        """
        import time
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            col_idx = headers.index(str(col)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableCellValueByHeaders] Column header not found: '{col}'")
        rk_idx = _get_row_key_column_index(tbl)
        if is_empty_cell_token(expected):
            expected = ""
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_val = None
        last_rows = None
        while time.time() < end:
            rc = int(tbl.get_row_count())
            matches = []
            for r in range(1, rc + 1):
                key_val = tbl.get_cell_text(r, rk_idx)
                if _match_wcm(key_val, row):
                    matches.append(r)
            if len(matches) == 1:
                val = tbl.get_cell_text(matches[0], col_idx)
                if _match_wcm(val, expected):
                    return
                last_val = val
            last_rows = matches
            time.sleep(poll)
        if last_rows is None:
            rc = int(tbl.get_row_count())
            last_rows = [r for r in range(1, rc + 1) if _match_wcm(tbl.get_cell_text(r, rk_idx), row)]
        if len(last_rows) == 0:
            raise AssertionError(f"[VerifyTableCellValueByHeaders] No row matched key pattern '{row}'")
        if len(last_rows) > 1:
            raise AssertionError(f"[VerifyTableCellValueByHeaders] Row not unique for key pattern '{row}': matched {len(last_rows)} rows")
        if last_val is None:
            last_val = tbl.get_cell_text(last_rows[0], col_idx)
        raise AssertionError(f"[VerifyTableCellValueByHeaders] Expected '{expected}', got '{last_val}' at row key '{row}', col '{col}'")

    @keyword("VerifyTableRowContentByHeader")
    def verify_table_row_content_by_header(self, name: str, row_header: str, row_value: str, expected_row_pattern: str):
        """Verifies a row's content identified by a specific header/value pair.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row_header``: Exact header name of the key column (case‑sensitive).
        - ``row_value``: Row key pattern (wildcard match) used to select the unique row.
        - ``expected_row_pattern``: Cells separated by the cell token (default ``$TAB``), wildcards supported.

        Behavior:
        - Resolves the key column by exact header name; finds exactly one matching row via WCM on that column.
        - Verifies the entire row with wildcard matching per cell; polls with table timeouts.

        Examples:
        | VerifyTableRowContentByHeader | Items | ID   | 12345 | 12345$TABFoo*$TAB9.9? |
        """
        import time
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            key_col = headers.index(str(row_header)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableRowContentByHeader] Column header not found: '{row_header}'")
        exp_cells = parse_row_pattern(expected_row_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_row_vals = None
        last_matches = None
        while time.time() < end:
            rc = int(tbl.get_row_count())
            matches = []
            for r in range(1, rc + 1):
                key_val = tbl.get_cell_text(r, key_col)
                if _match_wcm(key_val, row_value):
                    matches.append(r)
            if len(matches) == 1:
                act_cells = tbl.get_row_texts(matches[0])
                if len(act_cells) == len(exp_cells) and all(_match_wcm(a, e) for a, e in zip(act_cells, exp_cells)):
                    return
                last_row_vals = act_cells
            last_matches = matches
            time.sleep(poll)
        if last_matches is None:
            rc = int(tbl.get_row_count())
            last_matches = [r for r in range(1, rc + 1) if _match_wcm(tbl.get_cell_text(r, key_col), row_value)]
        if len(last_matches) == 0:
            raise AssertionError(f"[VerifyTableRowContentByHeader] No row matched pattern '{row_value}' in column '{row_header}'")
        if len(last_matches) > 1:
            raise AssertionError(f"[VerifyTableRowContentByHeader] Row not unique for pattern '{row_value}' in column '{row_header}': matched {len(last_matches)} rows")
        if last_row_vals is None:
            last_row_vals = tbl.get_row_texts(last_matches[0])
        if len(last_row_vals) != len(exp_cells):
            raise AssertionError(f"[VerifyTableRowContentByHeader] Row length mismatch: expected {len(exp_cells)}, got {len(last_row_vals)}")
        for i, (a, e) in enumerate(zip(last_row_vals, exp_cells), start=1):
            if not _match_wcm(a, e):
                raise AssertionError(f"[VerifyTableRowContentByHeader] Cell {i} mismatch: expected '{e}', got '{a}'")

    @keyword("VerifyTableColumnContentByHeader")
    def verify_table_column_content_by_header(self, name: str, col_header: str, expected_column_pattern: str):
        """Verifies a column's content selected by exact column header name.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``col_header``: Exact header name (case‑sensitive).
        - ``expected_column_pattern``: Rows separated by the row token (default ``$LF``), wildcards supported.

        Behavior:
        - Resolves the column by exact header name; verifies column cells with wildcard matching; polls with timeouts.

        Examples:
        | VerifyTableColumnContentByHeader | Items | Price  | Price$LF9.99$LF$EMPTY |
        | VerifyTableColumnContentByHeader | Items | Status | Status$LFOK$LFPending |
        """
        import time
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            col_idx = headers.index(str(col_header)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableColumnContentByHeader] Column header not found: '{col_header}'")
        exp_rows = parse_column_pattern(expected_column_pattern)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_vals = None
        while time.time() < end:
            act_rows = tbl.get_column_texts(int(col_idx))
            if len(exp_rows) == len(act_rows) and all(_match_wcm(a, e) for a, e in zip(act_rows, exp_rows)):
                return
            last_vals = act_rows
            time.sleep(poll)
        if last_vals is None:
            last_vals = tbl.get_column_texts(int(col_idx))
        if len(exp_rows) != len(last_vals):
            raise AssertionError(f"[VerifyTableColumnContentByHeader] Column length mismatch: expected {len(exp_rows)}, got {len(last_vals)}")
        for i, (a, e) in enumerate(zip(last_vals, exp_rows), start=1):
            if not _match_wcm(a, e):
                raise AssertionError(f"[VerifyTableColumnContentByHeader] Row {i} mismatch: expected '{e}', got '{a}'")

    @keyword("VerifyTableCellValueByHeadersREGX")
    def verify_table_cell_value_by_headers_regx(self, name: str, row: str, col: str, expected: str):
        """Verifies a single cell selected by row key (WCM) and column header (exact) using regex.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row``: Row key pattern (wildcard match, applied to the row key column).
        - ``col``: Exact column header name (case‑sensitive).
        - ``expected``: Python regular expression matched with ``re.search``. If ``$EMPTY``, requires empty value.

        Behavior:
        - Row selection via WCM on the row‑key column; must match exactly one row.
        - Column resolved by exact header name; value is verified via regex search.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        import time, re
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            col_idx = headers.index(str(col)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableCellValueByHeadersREGX] Column header not found: '{col}'")
        rk_idx = _get_row_key_column_index(tbl)
        want_empty = is_empty_cell_token(expected)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_val = None
        last_rows = None
        rx = None
        if not want_empty:
            try:
                rx = re.compile(str(expected))
            except Exception:
                # surface invalid regex immediately
                raise
        while time.time() < end:
            rc = int(tbl.get_row_count())
            matches = []
            for r in range(1, rc + 1):
                key_val = tbl.get_cell_text(r, rk_idx)
                if _match_wcm(key_val, row):
                    matches.append(r)
            if len(matches) == 1:
                val = tbl.get_cell_text(matches[0], col_idx)
                ok = (val == "") if want_empty else bool(rx.search(val or ""))
                if ok:
                    return
                last_val = val
            last_rows = matches
            time.sleep(poll)
        if last_rows is None:
            rc = int(tbl.get_row_count())
            last_rows = [r for r in range(1, rc + 1) if _match_wcm(tbl.get_cell_text(r, rk_idx), row)]
        if len(last_rows) == 0:
            raise AssertionError(f"[VerifyTableCellValueByHeadersREGX] No row matched key pattern '{row}'")
        if len(last_rows) > 1:
            raise AssertionError(f"[VerifyTableCellValueByHeadersREGX] Row not unique for key pattern '{row}': matched {len(last_rows)} rows")
        if last_val is None:
            last_val = tbl.get_cell_text(last_rows[0], col_idx)
        raise AssertionError(f"[VerifyTableCellValueByHeadersREGX] Regex '{expected}' did not match value '{last_val}' at row key '{row}', col '{col}'")

    @keyword("VerifyTableRowContentByHeaderREGX")
    def verify_table_row_content_by_header_regx(self, name: str, row_header: str, row_value: str, expected_row_pattern: str):
        """Verifies a row's content (per‑cell regex) identified by a specific header/value pair.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``row_header``: Exact header name of the key column (case‑sensitive).
        - ``row_value``: Row key pattern (wildcard match) used to select the unique row.
        - ``expected_row_pattern``: Cells separated by the cell token (default ``$TAB``), entries are regex patterns. ``$EMPTY`` requires empty cell.

        Behavior:
        - Resolves the key column by exact header; finds exactly one row via WCM on that column.
        - Verifies each cell against its regex (not anchored, DOTALL via ``re.search``). Empty token requires empty cell.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        import time, re
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            key_col = headers.index(str(row_header)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableRowContentByHeaderREGX] Column header not found: '{row_header}'")
        exps = parse_row_pattern(expected_row_pattern)
        # Precompile regex for non-empty patterns
        rx_list = []
        for pat in exps:
            if pat == "":
                rx_list.append(None)
            else:
                try:
                    rx_list.append(__import__('re').compile(str(pat), __import__('re').DOTALL))
                except Exception:
                    raise
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_vals = None
        last_matches = None
        while time.time() < end:
            rc = int(tbl.get_row_count())
            matches = []
            for r in range(1, rc + 1):
                key_val = tbl.get_cell_text(r, key_col)
                if _match_wcm(key_val, row_value):
                    matches.append(r)
            if len(matches) == 1:
                act = tbl.get_row_texts(matches[0])
                if len(act) == len(rx_list):
                    ok = True
                    for a, rx in zip(act, rx_list):
                        if rx is None:
                            if a != "":
                                ok = False; break
                        else:
                            if not rx.search(a or ""):
                                ok = False; break
                    if ok:
                        return
                last_vals = act
            last_matches = matches
            time.sleep(poll)
        if last_matches is None:
            rc = int(tbl.get_row_count())
            last_matches = [r for r in range(1, rc + 1) if _match_wcm(tbl.get_cell_text(r, key_col), row_value)]
        if len(last_matches) == 0:
            raise AssertionError(f"[VerifyTableRowContentByHeaderREGX] No row matched pattern '{row_value}' in column '{row_header}'")
        if len(last_matches) > 1:
            raise AssertionError(f"[VerifyTableRowContentByHeaderREGX] Row not unique for pattern '{row_value}' in column '{row_header}': matched {len(last_matches)} rows")
        if last_vals is None:
            last_vals = tbl.get_row_texts(last_matches[0])
        if len(last_vals) != len(rx_list):
            raise AssertionError(f"[VerifyTableRowContentByHeaderREGX] Row length mismatch: expected {len(rx_list)}, got {len(last_vals)}")
        for i, (a, rx) in enumerate(zip(last_vals, rx_list), start=1):
            if rx is None:
                if a != "":
                    raise AssertionError(f"[VerifyTableRowContentByHeaderREGX] Cell {i} expected empty, got '{a}'")
            else:
                if not rx.search(a or ""):
                    raise AssertionError(f"[VerifyTableRowContentByHeaderREGX] Cell {i} does not match regex: '{rx.pattern}', got '{a}'")

    @keyword("VerifyTableColumnContentByHeaderREGX")
    def verify_table_column_content_by_header_regx(self, name: str, col_header: str, expected_column_pattern: str):
        """Verifies a column's content (per‑cell regex) selected by exact header name.

        Arguments:
        - ``name``: Logical table name from the current window (YAML model).
        - ``col_header``: Exact header name (case‑sensitive).
        - ``expected_column_pattern``: Rows separated by the row token (default ``$LF``); entries are regex patterns. ``$EMPTY`` requires empty cell.

        Behavior:
        - Resolves the column by exact header name; each cell is verified via regex search (per row).
        - Polls until ``${OKW_TIMEOUT_VERIFY_TABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        import time, re
        tbl = _resolve_table(name)
        headers = _get_header_names(tbl)
        try:
            col_idx = headers.index(str(col_header)) + 1
        except ValueError:
            raise ValueError(f"[VerifyTableColumnContentByHeaderREGX] Column header not found: '{col_header}'")
        exps = parse_column_pattern(expected_column_pattern)
        rx_list = []
        for pat in exps:
            if pat == "":
                rx_list.append(None)
            else:
                try:
                    rx_list.append(re.compile(str(pat), re.DOTALL))
                except Exception:
                    raise
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_TABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last_vals = None
        while time.time() < end:
            act = tbl.get_column_texts(int(col_idx))
            if len(act) == len(rx_list):
                ok = True
                for a, rx in zip(act, rx_list):
                    if rx is None:
                        if a != "":
                            ok = False; break
                    else:
                        if not rx.search(a or ""):
                            ok = False; break
                if ok:
                    return
            last_vals = act
            time.sleep(poll)
        if last_vals is None:
            last_vals = tbl.get_column_texts(int(col_idx))
        if len(last_vals) != len(rx_list):
            raise AssertionError(f"[VerifyTableColumnContentByHeaderREGX] Column length mismatch: expected {len(rx_list)}, got {len(last_vals)}")
        for i, (a, rx) in enumerate(zip(last_vals, rx_list), start=1):
            if rx is None:
                if a != "":
                    raise AssertionError(f"[VerifyTableColumnContentByHeaderREGX] Row {i} expected empty, got '{a}'")
            else:
                if not rx.search(a or ""):
                    raise AssertionError(f"[VerifyTableColumnContentByHeaderREGX] Row {i} does not match regex: '{rx.pattern}', got '{a}'")
