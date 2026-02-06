from robot.api.deco import keyword
from ..runtime.context import context


def _get_time(var_name: str, default_seconds: float) -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        to = BuiltIn().get_variable_value(var_name, default=default_seconds)
        return float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
    except Exception:
        return float(default_seconds)


def _get_poll() -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        po = BuiltIn().get_variable_value("${OKW_POLL_VERIFY}", default=0.1)
        return float(po) if isinstance(po, (int, float)) else BuiltIn().convert_time(str(po))
    except Exception:
        return 0.1


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
        import time
        w = _resolve_widget(name)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_LIST}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        while time.time() < end:
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
        import time
        w = _resolve_widget(name)
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_LIST}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        while time.time() < end:
            try:
                got = int(w.okw_get_selected_count())
            except NotImplementedError as e:
                raise RuntimeError(f"[VerifySelectedCount] Not supported by widget '{name}': {e}")
            if got == exp:
                return
            time.sleep(poll)
        got = int(w.okw_get_selected_count())
        raise AssertionError(f"[VerifySelectedCount] Expected {exp}, got {got}")

