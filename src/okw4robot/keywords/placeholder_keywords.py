from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_placeholder(w) -> str:
    try:
        return w.okw_get_placeholder() or ""
    except Exception:
        return ""


class PlaceholderKeywords:
    @keyword("VerifyPlaceholder")
    def verify_placeholder(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholder] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        verify_with_timeout(lambda: _get_placeholder(w), expected, MatchMode.EXACT, timeout, f"[VerifyPlaceholder] '{name}'")

    @keyword("VerifyPlaceholderWCM")
    def verify_placeholder_wcm(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholderWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        verify_with_timeout(lambda: _get_placeholder(w), expected, MatchMode.WCM, timeout, f"[VerifyPlaceholderWCM] '{name}'")

    @keyword("VerifyPlaceholderREGX")
    def verify_placeholder_regx(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholderREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        verify_with_timeout(lambda: _get_placeholder(w), expected, MatchMode.REGX, timeout, f"[VerifyPlaceholderREGX] '{name}'")

    @keyword("MemorizePlaceholder")
    def memorize_placeholder(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_placeholder(w)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogPlaceholder")
    def log_placeholder(self, name):
        w = resolve_widget(name)
        value = _get_placeholder(w)
        logger.info(f"[LogPlaceholder] {value}")
