import time
from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.okw_helpers import get_robot_timeout, get_robot_poll, resolve_widget


class ListKeywords:
    @keyword("VerifyListCount")
    def verify_list_count(self, name: str, expected_count):
        """Verifies the number of items in a list-like widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected_count``: Integer expected number of items.

        Behavior:
        - Resolves the widget and polls ``okw_get_list_count()`` until the count equals the expected.
        - Timing via ``${OKW_TIMEOUT_VERIFY_LIST}`` (default 2s) and ``${OKW_POLL_VERIFY}`` (default 0.1s).

        Supported widgets (base implementation): ListBox, RadioList, native <select> ComboBox.
        """
        try:
            exp = int(str(expected_count).strip())
        except Exception:
            raise ValueError(f"[VerifyListCount] Expected must be integer, got '{expected_count}'")
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LIST}", 2.0)
        poll = get_robot_poll()
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                got = int(w.okw_get_list_count())
            except NotImplementedError as e:
                raise RuntimeError(f"[VerifyListCount] Not supported by widget '{name}': {e}")
            if got == exp:
                return
            time.sleep(poll)
        got = int(w.okw_get_list_count())
        raise AssertionError(f"[VerifyListCount] Expected {exp}, got {got}")

    @keyword("VerifySelectedCount")
    def verify_selected_count(self, name: str, expected_count):
        """Verifies the number of selected items in a list-like widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected_count``: Integer expected selected count.

        Behavior:
        - Resolves the widget and polls ``okw_get_selected_count()`` until the count equals the expected.
        - Timing via ``${OKW_TIMEOUT_VERIFY_LIST}`` (default 2s) and ``${OKW_POLL_VERIFY}`` (default 0.1s).

        Supported widgets (base implementation): ListBox, RadioList, ComboBox (0/1).
        """
        try:
            exp = int(str(expected_count).strip())
        except Exception:
            raise ValueError(f"[VerifySelectedCount] Expected must be integer, got '{expected_count}'")
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_LIST}", 2.0)
        poll = get_robot_poll()
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                got = int(w.okw_get_selected_count())
            except NotImplementedError as e:
                raise RuntimeError(f"[VerifySelectedCount] Not supported by widget '{name}': {e}")
            if got == exp:
                return
            time.sleep(poll)
        got = int(w.okw_get_selected_count())
        raise AssertionError(f"[VerifySelectedCount] Expected {exp}, got {got}")
