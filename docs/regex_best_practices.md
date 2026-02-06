Regex Best Practices (Robot Framework)

This guide summarizes practical tips for writing regex patterns in Robot test data that are consumed by OKW4Robot REGX keywords.

- Backslashes and escaping
  - Prefer character classes like `[0-9]` instead of `\d`, and `[A-Za-z]` instead of `\w`.
  - If you want to use a backslash escape, double-escape it in Robot tables: `\\d`, `\\s`, `\\w`.
  - Example (Robot): `^A3\\d$` matches `A30..A39`.

- Anchors and groups
  - Use `^` and `$` to anchor full matches when needed.
  - Non-capturing groups `(?:...)` are fine; alternation `a|b` works as usual.

- Inline flags (case, multiline, dotall)
  - Case-insensitive: `(?i)hello` matches `Hello`/`HELLO`.
  - Multiline: `(?m)` changes `^`/`$` to line boundaries.
  - Dot matches newline: `(?s)` (aka DOTALL). Some OKW REGX checks already use DOTALL; add `(?s)` yourself if needed.

- Multiline content
  - When verifying values that may contain newlines, consider `(?s)` or explicit classes like `[\s\S]`.
  - Example: `(?s)^Hello\s+world$`.

- Empty checks with tokens
  - Many table and value keywords treat `$EMPTY` as a special token for an empty string. Prefer `$EMPTY` over regex like `^$` when supported.

- Keep patterns readable
  - Start with a simple pattern, then refine.
  - Quote special characters with `\` if they should be literal (e.g., `\+`, `\?`, `\.`).

- Robot variables and regex
  - If composing patterns using variables, ensure backslashes remain escaped after substitution. You can prebuild the exact pattern with `Set Variable`.

- Quick examples (Robot Framework)
  - `VerifyValueREGX    Title    (?i)^hello\s+world$`
  - `VerifyTooltipREGX  OK       ^Click\s+here$`
  - `VerifyTableCellValueByHeadersREGX   DemoTable   A3*   Col2   ^A3[0-9]$`

Refer to the specific keyword docs for details on whether they use full-string matching, `re.search`, and whether DOTALL is enabled by default.
