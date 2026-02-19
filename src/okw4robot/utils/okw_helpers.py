"""OKW helper utilities for keyword implementations.

Central module for shared helpers used across all keyword classes.
Wraps okw-contract-utils tokens, matchers and timeout/polling helpers.
"""
from __future__ import annotations

from okw_contract_utils.tokens import is_ignore, is_empty_token, is_delete_token
from okw_contract_utils import MatchMode, assert_match


def blank_ignore_enabled() -> bool:
    """Return True if ${OKW_IGNORE_EMPTY}=YES is set in the Robot context."""
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value("${OKW_IGNORE_EMPTY}", default="NO")
        return str(val).strip().upper() in ("YES", "TRUE", "1")
    except Exception:
        return False


def should_ignore(value: object) -> bool:
    """Return True if *value* is the $IGNORE token or a blank that should be skipped.

    Rules:
    - ``$IGNORE`` / ``${IGNORE}`` (any case) → always ignore.
    - Empty / whitespace-only string → ignore only when ``${OKW_IGNORE_EMPTY}=YES``.
    """
    if isinstance(value, str):
        sv = value.strip()
        if is_ignore(sv):
            return True
        # Also handle Robot variable syntax ${IGNORE} → expands to literal string
        if sv.upper() in ("${IGNORE}",):
            return True
        if sv == "" and blank_ignore_enabled():
            return True
    return False


def is_empty(value: object) -> bool:
    """Return True if *value* is the $EMPTY token (``$EMPTY`` / ``${EMPTY}``)."""
    if isinstance(value, str):
        sv = value.strip()
        if is_empty_token(sv):
            return True
        if sv.upper() == "${EMPTY}":
            return True
    return False


def is_delete(value: object) -> bool:
    """Return True if *value* is the $DELETE token (``$DELETE`` / ``${DELETE}``)."""
    if isinstance(value, str):
        sv = value.strip()
        if is_delete_token(sv):
            return True
        if sv.upper() == "${DELETE}":
            return True
    return False


def get_robot_timeout(var_name: str, default_seconds: float) -> float:
    """Read a timeout variable from the Robot context, returning seconds as float."""
    try:
        from robot.libraries.BuiltIn import BuiltIn
        to = BuiltIn().get_variable_value(var_name, default=default_seconds)
        return float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
    except Exception:
        return float(default_seconds)


def get_robot_poll(default: float = 0.1) -> float:
    """Read ``${OKW_POLL_VERIFY}`` from the Robot context, returning seconds as float."""
    return get_robot_timeout("${OKW_POLL_VERIFY}", default)


def normalize_var_name(variable: str) -> str:
    """Normalise a user-supplied variable name to Robot ``${VAR}`` syntax."""
    var = str(variable).strip()
    if var.startswith("${") and var.endswith("}"):
        return var
    if var.startswith("$"):
        return "${" + var[1:] + "}"
    return "${" + var + "}"


def resolve_widget(name: str):
    """Resolve a logical widget name to a widget instance using the current context.

    Looks up *name* in the current window model, loads the widget class and
    returns an instantiated widget bound to the active adapter.

    Raises:
    - ``RuntimeError``: if no adapter/app/window is active.
    - ``KeyError``: if *name* is not found in the current window model.
    """
    from ..runtime.context import context
    from ..utils.loader import load_class

    model = context.get_current_window_model()
    if name not in model:
        raise KeyError(f"Widget '{name}' not found in current window.")
    entry = model[name]
    widget_class = load_class(entry["class"])
    adapter = context.get_adapter()
    extras = {k: v for k, v in entry.items() if k not in ("class", "locator")}
    return widget_class(adapter, entry.get("locator"), **extras)


def verify_yes_no_poll(
    get_actual_bool,
    expected: str,
    timeout_var: str,
    default_timeout: float,
    context_label: str,
) -> None:
    """Poll a boolean predicate until it matches a YES/NO expectation or timeout.

    Args:
        get_actual_bool: Zero-argument callable returning bool (current state).
        expected: ``"YES"`` or ``"NO"`` (and TRUE/FALSE/1/0 variants).
        timeout_var: Robot variable name for the timeout (e.g. ``"${OKW_TIMEOUT_VERIFY_EXIST}"``).
        default_timeout: Default timeout in seconds.
        context_label: Prepended to assertion error messages.
    """
    import time
    from okw_contract_utils.tokens import parse_yes_no, assert_exists

    yn = parse_yes_no(expected)
    timeout = get_robot_timeout(timeout_var, default_timeout)
    poll = get_robot_poll()
    end = time.monotonic() + timeout
    last = False
    while True:
        last = bool(get_actual_bool())
        from okw_contract_utils.tokens import OkwYesNo
        if (yn == OkwYesNo.YES and last) or (yn == OkwYesNo.NO and not last):
            return
        if time.monotonic() >= end:
            break
        time.sleep(poll)
    assert_exists(last, yn, context=context_label)


def verify_with_timeout(
    get_actual,
    expected: str,
    mode: MatchMode,
    timeout_s: float,
    context_label: str,
) -> None:
    """Poll *get_actual()* until it matches *expected* using *mode*, or timeout.

    Args:
        get_actual: Zero-argument callable returning the current string value.
        expected: The expected value / pattern.
        mode: ``MatchMode.EXACT``, ``MatchMode.WCM`` or ``MatchMode.REGX``.
        timeout_s: Maximum seconds to poll.
        context_label: Prepended to assertion error messages (e.g. ``"[VerifyValue] 'Username'"``)
    """
    import time
    from okw_contract_utils import is_match

    poll = get_robot_poll()
    end = time.monotonic() + timeout_s
    last_actual: str = ""
    while True:
        last_actual = get_actual() or ""
        result = is_match(last_actual, expected, mode)
        if result.ok:
            return
        if time.monotonic() >= end:
            break
        time.sleep(poll)
    # Raise the final mismatch as an assertion error
    assert_match(last_actual, expected, mode, context=context_label)
