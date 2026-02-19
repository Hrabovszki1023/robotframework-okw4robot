from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_attr(widget, attr_name: str) -> str:
    try:
        val = widget.adapter.get_attribute(widget.locator, attr_name)
        return "" if val is None else str(val)
    except Exception:
        return ""


class AttributeKeywords:
    @keyword("VerifyAttribute")
    def verify_attribute(self, name, attribute, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyAttribute] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_ATTRIBUTE}", 10.0)
        verify_with_timeout(lambda: _get_attr(w, attribute), expected, MatchMode.EXACT, timeout, f"[VerifyAttribute] '{name}'")

    @keyword("VerifyAttributeWCM")
    def verify_attribute_wcm(self, name, attribute, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyAttributeWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_ATTRIBUTE}", 10.0)
        verify_with_timeout(lambda: _get_attr(w, attribute), expected, MatchMode.WCM, timeout, f"[VerifyAttributeWCM] '{name}'")

    @keyword("VerifyAttributeREGX")
    def verify_attribute_regx(self, name, attribute, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyAttributeREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_ATTRIBUTE}", 10.0)
        verify_with_timeout(lambda: _get_attr(w, attribute), expected, MatchMode.REGX, timeout, f"[VerifyAttributeREGX] '{name}'")

    @keyword("MemorizeAttribute")
    def memorize_attribute(self, name, attribute, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_attr(w, attribute)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogAttribute")
    def log_attribute(self, name, attribute):
        w = resolve_widget(name)
        value = _get_attr(w, attribute)
        logger.info(f"[LogAttribute] {value}")
