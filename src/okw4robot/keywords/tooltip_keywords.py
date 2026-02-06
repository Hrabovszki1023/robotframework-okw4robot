from robot.api.deco import keyword
from ..runtime.context import context


def _blank_ignore_enabled() -> bool:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value("${OKW_IGNORE_EMPTY}", default="NO")
        return str(val).strip().upper() in ("YES", "TRUE", "1")
    except Exception:
        return False


def _should_ignore(value) -> bool:
    if isinstance(value, str):
        sv = value.strip()
        t = sv.upper()
        if t in ("$IGNORE", "${IGNORE}"):
            return True
        if sv == "" and _blank_ignore_enabled():
            return True
    return False


def _resolve_widget(name):
    model = context.get_current_window_model()
    if name not in model:
        raise KeyError(f"Widget '{name}' not found in current window.")
    entry = model[name]
    from ..utils.loader import load_class
    widget_class = load_class(entry["class"])
    adapter = context.get_adapter()
    extras = {k: v for k, v in entry.items() if k not in ("class", "locator")}
    return widget_class(adapter, entry.get("locator"), **extras)


def _get_tooltip(widget) -> str:
    # Prefer HTML 'title' attribute, fallback to 'aria-label'
    try:
        val = widget.adapter.get_attribute(widget.locator, 'title')
        if val:
            return val
    except Exception:
        pass
    try:
        val = widget.adapter.get_attribute(widget.locator, 'aria-label')
        if val:
            return val
    except Exception:
        pass
    return ""


class TooltipKeywords:
    @keyword("VerifyTooltip")
    def verify_tooltip(self, name, expected):
        """Verifies that a widget's tooltip equals the expected string.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Expected tooltip text (exact match).

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Reads tooltip via element attributes (prefers ``title``, falls back to ``aria-label``).
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltip | HelpIcon | Opens settings |
        | VerifyTooltip | Hint     | $IGNORE        |
        """
        if _should_ignore(expected):
            print(f"[VerifyTooltip] '{name}' ignored (blank or $IGNORE)")
            return
        import time
        from robot.libraries.BuiltIn import BuiltIn
        w = _resolve_widget(name)
        # Resolve default verify-timeout; allow override via ${OKW_VERIFY_TIMEOUT}
        try:
            verify_to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_TOOLTIP}", default=10)
            if isinstance(verify_to, (int, float)):
                deadline = time.time() + float(verify_to)
            else:
                deadline = time.time() + BuiltIn().convert_time(str(verify_to))
        except Exception:
            deadline = time.time() + 10.0
        last = None
        while time.time() < deadline:
            last = _get_tooltip(w)
            if last == expected:
                return
            time.sleep(0.1)
        raise AssertionError("[VerifyTooltip] Expected '" + str(expected) + "', last seen '" + str(last) + "'")

    @keyword("VerifyTooltipWCM")
    def verify_tooltip_wcm(self, name, expected):
        """Verifies a widget's tooltip using wildcard matching (WCM).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Wildcard pattern where ``*`` = any sequence, ``?`` = one character.

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Converts the wildcard pattern to a case‑sensitive regex anchored with ``^...$`` (DOTALL).
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltipWCM | HelpIcon | *settings* |
        | VerifyTooltipWCM | Hint     | Error?     |
        """
        if _should_ignore(expected):
            print(f"[VerifyTooltipWCM] '{name}' ignored (blank or $IGNORE)")
            return
        import re, time
        from robot.libraries.BuiltIn import BuiltIn
        w = _resolve_widget(name)
        pattern = '^' + re.escape(expected).replace(r'\\*', '.*').replace(r'\\?', '.') + '$'
        try:
            verify_to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_TOOLTIP}", default=10)
            if isinstance(verify_to, (int, float)):
                deadline = time.time() + float(verify_to)
            else:
                deadline = time.time() + BuiltIn().convert_time(str(verify_to))
        except Exception:
            deadline = time.time() + 10.0
        last = None
        rx = re.compile(pattern, re.DOTALL)
        while time.time() < deadline:
            last = _get_tooltip(w)
            if rx.match(last or ""):
                return
            time.sleep(0.1)
        raise AssertionError("[VerifyTooltipWCM] Value '" + str(last) + "' does not match pattern '" + str(expected) + "'")

    @keyword("VerifyTooltipREGX")
    def verify_tooltip_regx(self, name, expected):
        """Verifies a widget's tooltip using a regular expression (regex).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Python regular expression used with ``re.search`` (not anchored).

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Case‑sensitive search within the tooltip text; use inline flags like ``(?i)`` for case‑insensitive.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltipREGX | HelpIcon | ^Open.*settings$ |
        | VerifyTooltipREGX | Hint     | (?i)error        |
        """
        if _should_ignore(expected):
            print(f"[VerifyTooltipREGX] '{name}' ignored (blank or $IGNORE)")
            return
        import re, time
        from robot.libraries.BuiltIn import BuiltIn
        w = _resolve_widget(name)
        try:
            verify_to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_TOOLTIP}", default=10)
            if isinstance(verify_to, (int, float)):
                deadline = time.time() + float(verify_to)
            else:
                deadline = time.time() + BuiltIn().convert_time(str(verify_to))
        except Exception:
            deadline = time.time() + 10.0
        last = None
        while time.time() < deadline:
            last = _get_tooltip(w)
            try:
                if re.search(expected, last or ""):
                    return
            except Exception:
                # Invalid regex -> surface the error now
                raise
            time.sleep(0.1)
        raise AssertionError("[VerifyTooltipREGX] Value '" + str(last) + "' does not match regex '" + str(expected) + "'")

    

    @keyword("MemorizeTooltip")
    def memorize_tooltip(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = _resolve_widget(name)
        value = _get_tooltip(w)
        var = str(variable).strip()
        if var.startswith("${") and var.endswith("}"):
            var_name = var
        elif var.startswith("$"):
            var_name = "${" + var[1:] + "}"
        else:
            var_name = "${" + var + "}"
        BuiltIn().set_test_variable(var_name, value)

    @keyword("LogTooltip")
    def log_tooltip(self, name):
        w = _resolve_widget(name)
        print("LOG:", _get_tooltip(w))
