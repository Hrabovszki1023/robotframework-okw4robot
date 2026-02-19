from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, resolve_widget, verify_with_timeout, normalize_var_name
from okw_contract_utils import MatchMode


def _get_label_text(widget) -> str:
    a = widget.adapter
    # 1) aria-labelledby
    try:
        aria = a.get_attribute(widget.locator, 'aria-labelledby')
        if aria:
            parts = [p for p in str(aria).split() if p]
            texts = []
            for pid in parts:
                try:
                    texts.append(a.get_text({'id': pid}) or '')
                except Exception:
                    pass
            joined = ' '.join(t.strip() for t in texts if t is not None)
            if joined.strip():
                return joined
    except Exception:
        pass
    # 2) <label for="id">
    try:
        elem_id = a.get_attribute(widget.locator, 'id')
        if elem_id:
            try:
                txt = a.get_text({'css': f'label[for="{elem_id}"]'})
                if txt and txt.strip():
                    return txt
            except Exception:
                pass
    except Exception:
        pass
    # 3) aria-label as last resort
    try:
        aria_label = a.get_attribute(widget.locator, 'aria-label')
        if aria_label:
            return aria_label
    except Exception:
        pass
    # 4) fallback to element's own visible text (buttons/links/labels)
    try:
        return a.get_text(widget.locator) or ""
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
        verify_with_timeout(lambda: _get_label_text(w), expected, MatchMode.EXACT, timeout, f"[VerifyLabel] '{name}'")

    @keyword("VerifyLabelWCM")
    def verify_label_wcm(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyLabelWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LABEL}", 10.0)
        verify_with_timeout(lambda: _get_label_text(w), expected, MatchMode.WCM, timeout, f"[VerifyLabelWCM] '{name}'")

    @keyword("VerifyLabelREGX")
    def verify_label_regx(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyLabelREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LABEL}", 10.0)
        verify_with_timeout(lambda: _get_label_text(w), expected, MatchMode.REGX, timeout, f"[VerifyLabelREGX] '{name}'")

    @keyword("MemorizeLabel")
    def memorize_label(self, name, variable):
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        value = _get_label_text(w)
        BuiltIn().set_test_variable(normalize_var_name(variable), value)

    @keyword("LogLabel")
    def log_label(self, name):
        w = resolve_widget(name)
        value = _get_label_text(w)
        logger.info(f"[LogLabel] {value}")
