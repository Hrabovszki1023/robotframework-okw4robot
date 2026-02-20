from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_label(w) -> str:
    try:
        return w.okw_get_label() or ""
    except Exception:
        return ""


class LabelKeywords:
    @keyword("VerifyLabel")
    def verify_label(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyLabel] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LABEL}", 10.0)
        verify_with_timeout(lambda: _get_label(w), expected, MatchMode.EXACT, timeout, f"[VerifyLabel] '{name}'")

    @keyword("VerifyLabelWCM")
    def verify_label_wcm(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyLabelWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LABEL}", 10.0)
        verify_with_timeout(lambda: _get_label(w), expected, MatchMode.WCM, timeout, f"[VerifyLabelWCM] '{name}'")

    @keyword("VerifyLabelREGX")
    def verify_label_regx(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyLabelREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LABEL}", 10.0)
        verify_with_timeout(lambda: _get_label(w), expected, MatchMode.REGX, timeout, f"[VerifyLabelREGX] '{name}'")

    @keyword("MemorizeLabel")
    def memorize_label(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_label(w)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogLabel")
    def log_label(self, name):
        w = resolve_widget(name)
        value = _get_label(w)
        logger.info(f"[LogLabel] {value}")
