"""
Utilities for parsing table patterns with special tokens.

Tokens (defaults; can be overridden by Robot variables):
- ${OKW_TABLE_CELL_SEP_TOKEN}   (default: '$TAB')
- ${OKW_TABLE_ROW_SEP_TOKEN}    (default: '$LF')
- ${OKW_TABLE_EMPTY_CELL_TOKEN} (default: '$EMPTY')
- ${OKW_TABLE_EMPTY_COL_TOKEN}  (default: '$EMPTYCOL')
- ${OKW_TABLE_EMPTY_TABLE_TOKEN}(default: '$EMPTYTABLE')

Escaping: prefix a backslash to treat a token literally (e.g. '\\$TAB').
"""

from __future__ import annotations

from typing import List, Tuple


def _get_var(name: str, default: str) -> str:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value(name, default=default)
        return str(val) if val is not None else default
    except Exception:
        return default


def get_tokens() -> dict:
    return {
        'CELL_SEP': _get_var('${OKW_TABLE_CELL_SEP_TOKEN}', '$TAB'),
        'ROW_SEP': _get_var('${OKW_TABLE_ROW_SEP_TOKEN}', '$LF'),
        'EMPTY_CELL': _get_var('${OKW_TABLE_EMPTY_CELL_TOKEN}', '$EMPTY'),
        'EMPTY_COL': _get_var('${OKW_TABLE_EMPTY_COL_TOKEN}', '$EMPTYCOL'),
        'EMPTY_TABLE': _get_var('${OKW_TABLE_EMPTY_TABLE_TOKEN}', '$EMPTYTABLE'),
    }


def _split_escaped(s: str, sep: str) -> List[str]:
    """Split string by token 'sep' while supporting backslash-escaping.

    Example: 'A$TABB\\$TABC$TABD' with sep='$TAB' -> ['A', 'B$TABC', 'D']
    """
    if not s:
        return [""]
    parts: List[str] = []
    buf: List[str] = []
    i = 0
    n = len(s)
    sl = len(sep)
    while i < n:
        ch = s[i]
        # escape handling
        if ch == '\\':
            if i + 1 < n:
                buf.append(s[i + 1])
                i += 2
                continue
            # trailing backslash -> keep it
            buf.append('\\')
            i += 1
            continue
        # separator match
        if sl > 0 and s.startswith(sep, i):
            parts.append(''.join(buf))
            buf = []
            i += sl
            continue
        buf.append(ch)
        i += 1
    parts.append(''.join(buf))
    return parts


def parse_row_pattern(row_pattern: str) -> List[str]:
    """Split a row pattern into cell patterns using the cell separator token.
    Returns list of cell string patterns (not evaluated).
    """
    t = get_tokens()
    cells = _split_escaped(str(row_pattern or ''), t['CELL_SEP'])
    # normalize $EMPTY cells to '' for downstream exact/regex matching convenience
    empty_token = t['EMPTY_CELL']
    return ["" if c == empty_token else c for c in cells]


def parse_column_pattern(col_pattern: str) -> List[str]:
    """Split a column pattern into row entries using the row separator token."""
    t = get_tokens()
    rows = _split_escaped(str(col_pattern or ''), t['ROW_SEP'])
    empty = t['EMPTY_CELL']
    # Special case: $EMPTYCOL means column with zero non-empty values -> represent as empty list
    if len(rows) == 1 and rows[0] == t['EMPTY_COL']:
        return []
    return ["" if r == empty else r for r in rows]


def parse_table_pattern(table_pattern: str) -> List[List[str]]:
    """Split a whole-table pattern into rows and cells.
    Returns a list of rows; each row is a list of cell string patterns.
    """
    t = get_tokens()
    pat = str(table_pattern or '')
    if pat == t['EMPTY_TABLE']:
        return []
    row_strs = _split_escaped(pat, t['ROW_SEP'])
    return [parse_row_pattern(r) for r in row_strs]


def is_empty_cell_token(s: str) -> bool:
    return str(s) == get_tokens()['EMPTY_CELL']


def is_empty_col_token(s: str) -> bool:
    return str(s) == get_tokens()['EMPTY_COL']


def is_empty_table_token(s: str) -> bool:
    return str(s) == get_tokens()['EMPTY_TABLE']


def compile_wcm_to_regex(pattern: str) -> str:
    """Compile a wildcard (*, ?) pattern into a regex string (with ^$ anchors)."""
    import re
    if pattern is None:
        return r'^$'
    # Escape regex metachars, then replace wildcards
    esc = re.escape(str(pattern))
    esc = esc.replace(r'\*', '.*').replace(r'\?', '.')
    return '^' + esc + '$'

