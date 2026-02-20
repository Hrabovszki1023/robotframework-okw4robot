from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_tooltip(w) -> str:
    try:
        return w.okw_get_tooltip() or ""
    except Exception:
        return ""


class TooltipKeywords:
    @keyword("VerifyTooltip")
    def verify_tooltip(self, name, expected):
        """Verifies that a widget's tooltip equals the expected string.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Expected tooltip text (exact match).

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case-insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Delegates to ``widget.okw_get_tooltip()`` – driver-specific logic decides how to read the tooltip.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltip | HelpIcon | Opens settings |
        | VerifyTooltip | Hint     | $IGNORE        |
        """
        if should_ignore(expected):
            logger.info(f"[VerifyTooltip] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_TOOLTIP}", 10.0)
        verify_with_timeout(lambda: _get_tooltip(w), expected, MatchMode.EXACT, timeout, f"[VerifyTooltip] '{name}'")

    @keyword("VerifyTooltipWCM")
    def verify_tooltip_wcm(self, name, expected):
        """Verifies a widget's tooltip using wildcard matching (WCM).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Wildcard pattern where ``*`` = any sequence, ``?`` = one character.

        Behavior:
        - Delegates to ``widget.okw_get_tooltip()``.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltipWCM | HelpIcon | *settings* |
        | VerifyTooltipWCM | Hint     | Error?     |
        """
        if should_ignore(expected):
            logger.info(f"[VerifyTooltipWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_TOOLTIP}", 10.0)
        verify_with_timeout(lambda: _get_tooltip(w), expected, MatchMode.WCM, timeout, f"[VerifyTooltipWCM] '{name}'")

    @keyword("VerifyTooltipREGX")
    def verify_tooltip_regx(self, name, expected):
        """Verifies a widget's tooltip using a regular expression (regex).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Python regular expression used with ``re.search`` (not anchored).

        Behavior:
        - Delegates to ``widget.okw_get_tooltip()``.
        - Polls until ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` (default 10s); raises last error on timeout.

        Examples:
        | VerifyTooltipREGX | HelpIcon | ^Open.*settings$ |
        | VerifyTooltipREGX | Hint     | (?i)error        |
        """
        if should_ignore(expected):
            logger.info(f"[VerifyTooltipREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_TOOLTIP}", 10.0)
        verify_with_timeout(lambda: _get_tooltip(w), expected, MatchMode.REGX, timeout, f"[VerifyTooltipREGX] '{name}'")

    @keyword("MemorizeTooltip")
    def memorize_tooltip(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_tooltip(w)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogTooltip")
    def log_tooltip(self, name):
        w = resolve_widget(name)
        value = _get_tooltip(w)
        logger.info(f"[LogTooltip] {value}")
