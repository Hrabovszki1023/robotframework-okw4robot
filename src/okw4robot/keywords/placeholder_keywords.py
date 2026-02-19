import time
from robot.api.deco import keyword
from robot.api import logger
from ..utils.okw_helpers import should_ignore, get_robot_timeout, get_robot_poll, resolve_widget


class PlaceholderKeywords:
    @keyword("VerifyPlaceholder")
    def verify_placeholder(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholder] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        if not hasattr(w, 'okw_verify_placeholder'):
            raise NotImplementedError(f"Widget '{name}' does not support VerifyPlaceholder")
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        poll = get_robot_poll()
        end = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < end:
            try:
                w.okw_verify_placeholder(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(poll)
        if last_error:
            raise last_error

    @keyword("VerifyPlaceholderWCM")
    def verify_placeholder_wcm(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholderWCM] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        if not hasattr(w, 'okw_verify_placeholder_wcm'):
            raise NotImplementedError(f"Widget '{name}' does not support VerifyPlaceholderWCM")
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        poll = get_robot_poll()
        end = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < end:
            try:
                w.okw_verify_placeholder_wcm(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(poll)
        if last_error:
            raise last_error

    @keyword("VerifyPlaceholderREGX")
    def verify_placeholder_regx(self, name, expected):
        if should_ignore(expected):
            logger.info(f"[VerifyPlaceholderREGX] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        if not hasattr(w, 'okw_verify_placeholder_regex'):
            raise NotImplementedError(f"Widget '{name}' does not support VerifyPlaceholderREGX")
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_PLACEHOLDER}", 10.0)
        poll = get_robot_poll()
        end = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < end:
            try:
                w.okw_verify_placeholder_regex(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(poll)
        if last_error:
            raise last_error
