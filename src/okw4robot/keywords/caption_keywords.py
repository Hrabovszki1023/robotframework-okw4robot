from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_caption(w) -> str:
    try:
        return w.okw_get_text() or ""
    except Exception:
        return ""


class CaptionKeywords:
    @keyword("VerifyCaption")
    def verify_caption(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyCaption] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_CAPTION}", 10.0)
        verify_with_timeout(lambda: _get_caption(w), expected, MatchMode.EXACT, timeout, f"[VerifyCaption] '{name}'")

    @keyword("VerifyCaptionWCM")
    def verify_caption_wcm(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyCaptionWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_CAPTION}", 10.0)
        verify_with_timeout(lambda: _get_caption(w), expected, MatchMode.WCM, timeout, f"[VerifyCaptionWCM] '{name}'")

    @keyword("VerifyCaptionREGX")
    def verify_caption_regx(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyCaptionREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_CAPTION}", 10.0)
        verify_with_timeout(lambda: _get_caption(w), expected, MatchMode.REGX, timeout, f"[VerifyCaptionREGX] '{name}'")

    @keyword("MemorizeCaption")
    def memorize_caption(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_caption(w)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogCaption")
    def log_caption(self, name):
        w = resolve_widget(name)
        value = _get_caption(w)
        logger.info(f"[LogCaption] {value}")
