ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'
from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.loader import load_class

def _blank_ignore_enabled() -> bool:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value("${OKW_IGNORE_EMPTY}", default="NO")
        return str(val).strip().upper() in ("YES", "TRUE", "1")
    except Exception:
        return False

def _should_ignore(value) -> bool:
    """Return True if the keyword argument indicates 'ignore'.

    Rules:
    - Literal tokens '$IGNORE' or '${IGNORE}' (any case) -> ignore
    - Optionally, if ${OKW_IGNORE_EMPTY}=YES, then empty/whitespace-only -> ignore
    """
    if isinstance(value, str):
        sv = value.strip()
        t = sv.upper()
        if t in ("$IGNORE", "${IGNORE}"):
            return True
        if sv == "" and _blank_ignore_enabled():
            return True
    return False

def resolve_widget(name):
    model = context.get_current_window_model()
    if name not in model:
        raise KeyError(f"Widget '{name}' not found in current window.")
    entry = model[name]
    widget_class = load_class(entry["class"])
    adapter = context.get_adapter()
    extras = {k: v for k, v in entry.items() if k not in ("class", "locator")}
    return widget_class(adapter, entry.get("locator"), **extras)

def _require_adapter_method(adapter, method_name: str, widget, widget_name: str, keyword_name: str):
    if not hasattr(adapter, method_name):
        a = adapter.__class__.__name__
        w = widget.__class__.__name__ if widget else "<unknown>"
        loc = getattr(widget, 'locator', None)
        raise RuntimeError(
            f"[{keyword_name}] Not implemented by adapter: method '{method_name}' is missing on '{a}' "
            f"for widget '{widget_name}' ({w}), locator={loc}"
        )
    return getattr(adapter, method_name)

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

class WidgetKeywords:
    """Widget interactions and verifications.

    Provides high‑level Robot Framework keywords to interact with widgets
    defined in the current window model (YAML). See the individual
    keyword docstrings for arguments and examples.
    """
    @keyword("ClickOn")
    def click_on(self, name: str):
        """Click on a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Behavior:
        - Resolves the widget by name and triggers its ``okw_click()``.
        - Write intent: underlying widget/adapter typically performs pre‑click
          sync (exists → visible → enabled → optional scroll_into_view).

        Example (with window context):
        | SelectWindow | LoginDialog |
        | SetValue     | Benutzer    | admin  |
        | SetValue     | Passwort    | geheim |
        | *ClickOn*    | *OK*        |
        """
        resolve_widget(name).okw_click()

    @keyword("DoubleClickOn")
    def double_click_on(self, name: str):
        """Double‑click on a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Behavior:
        - Resolves the widget by name and triggers its ``okw_double_click()``.
        - Write intent: underlying widget/adapter typically performs the same
          pre‑action sync as for clicks (exists → visible → enabled → optional scroll).

        Example (with window context):
        | SelectWindow  | LoginDialog |
        | SetValue      | Benutzer    | admin  |
        | SetValue      | Passwort    | geheim |
        | *DoubleClickOn* | *OK*      |
        """
        resolve_widget(name).okw_double_click()

    @keyword("SetValue")
    def set_value(self, name, value):
        """Sets the value of a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``value``: Value to set.

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip this field — no action,
          no error.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.
        - ``$EMPTY`` or ``${EMPTY}`` (case‑insensitive): Explicitly set an empty string.
          This is NEVER ignored, even if ``${OKW_IGNORE_EMPTY}=YES`` is active.
        - ``$DELETE``: Not handled by ``SetValue`` (not supported).

        Behavior:
        - Resolves the widget by name and calls its ``okw_set_value(value)``.
        - If the value should be ignored (see above), a short message is logged
          and the keyword returns.

        Examples:
        | SelectWindow | LoginDialog |
        | SetValue     | Username    | admin  |
        | SetValue     | Password    | secret |
        | ClickOn      | OK          |

        | # Skip fields when needed
        | SetValue     | Comment     | $IGNORE |

        | # Ignore empty only when explicitly enabled
        | SetSuiteVariable | ${OKW_IGNORE_EMPTY} | YES |
        | SetValue        | ExtraInfo |    |    # ignored

        | # Explicitly clear content — never ignored
        | SetSuiteVariable | ${OKW_IGNORE_EMPTY} | YES |
        | SetValue        | Comment | $EMPTY |
        """
        # $EMPTY explizit unterstützen und NICHT ignorieren
        if isinstance(value, str) and value.strip().upper() in ("$EMPTY", "${EMPTY}"):
            resolve_widget(name).okw_set_value("")
            return
        if _should_ignore(value):
            print(f"[SetValue] '{name}' ignored (blank or $IGNORE)")
            return
        resolve_widget(name).okw_set_value(value)

    @keyword("Select")
    def select(self, name, value):
        """Selects a value on a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``value``: Value/option to select.

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip this field — no action,
          no error.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.
        - ``$DELETE``: Not handled by ``Select`` (not supported).

        Behavior:
        - Resolves the widget by name and calls its ``okw_select(value)``.
        - If the value should be ignored, a short message is logged and the keyword returns.

        Examples:
        | SelectWindow | Settings |
        | Select       | Language | English |

        | # Skip optional selection
        | Select       | Theme    | $IGNORE |

        | # Ignore empty only when explicitly enabled
        | SetSuiteVariable | ${OKW_IGNORE_EMPTY} | YES |
        | Select           | Region  |    |    # ignored
        """
        if _should_ignore(value):
            print(f"[Select] '{name}' ignored (blank or $IGNORE)")
            return
        resolve_widget(name).okw_select(value)

    @keyword("TypeKey")
    def type_key(self, name, key):
        """Simulates keyboard input on a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``key``: Text or key sequence to type.

        Special tokens / control parameters:
        - ``$DELETE`` or ``${DELETE}`` (case‑insensitive): Clear the current field value
          (adapter tries ``clear_text`` first; fallback ``CTRL+A`` + ``DELETE``).
        - ``$IGNORE`` or ``${IGNORE}``: Skip this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Existing content remains; this keyword types, it does not overwrite.
          Deletion happens only explicitly (e.g., via ``$DELETE`` or a key combo).
        - Resolves the widget and sends the input via ``okw_type_key(key)``.

        Examples:
        | SelectWindow | LoginDialog |
        | TypeKey      | Username    | admin |
        | TypeKey      | Password    | secret |

        | # Explicitly clear content
        | TypeKey      | Comment     | $DELETE |

        | # Skip a field if needed
        | TypeKey      | ExtraInfo   | $IGNORE |
        """
        # Handle special delete token
        if isinstance(key, str) and key.strip().upper() in ("$DELETE", "${DELETE}"):
            widget = resolve_widget(name)
            try:
                widget.adapter.clear_text(widget.locator)
                return
            except Exception:
                pass
            try:
                widget.adapter.click(widget.locator)
                widget.adapter.press_keys(widget.locator, "CTRL+A")
                widget.adapter.press_keys(widget.locator, "DELETE")
                return
            except Exception:
                pass
        if _should_ignore(key):
            print(f"[TypeKey] '{name}' ignored (blank or $IGNORE)")
            return
        resolve_widget(name).okw_type_key(key)

    @keyword("VerifyValue")
    def verify_value(self, name, expected):
        """Verifies that a widget's value equals the expected string.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Expected value (exact match).

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Resolves the widget and repeatedly verifies via ``okw_verify_value(expected)``
          until it passes or ``${OKW_TIMEOUT_VERIFY_VALUE}`` elapses (default 10s).
        - Re‑raises the last assertion error if the timeout is reached.

        Examples:
        | SelectWindow | LoginDialog |
        | VerifyValue  | Username    | admin |

        | # Skip optional verification
        | VerifyValue  | Comment     | $IGNORE |
        """
        if _should_ignore(expected):
            print(f"[VerifyValue] '{name}' ignored (blank or $IGNORE)")
            return
        import time
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        try:
            to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_VALUE}", default=10)
            timeout = float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
        except Exception:
            timeout = 10.0
        end = time.time() + timeout
        last_error = None
        while time.time() < end:
            try:
                w.okw_verify_value(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(0.1)
        if last_error:
            raise last_error

    @keyword("VerifyValueWCM")
    def verify_value_wcm(self, name, expected):
        """Verifies a widget's value using wildcard matching (WCM).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Wildcard pattern where ``*`` matches any sequence and ``?`` one character.

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Case‑sensitive full‑string match: internally converts the pattern to a regex
          anchored with ``^...$`` and matches with DOTALL.
        - Retries until ``${OKW_TIMEOUT_VERIFY_VALUE}`` elapses (default 10s), then re‑raises
          the last assertion error.

        Examples:
        | VerifyValueWCM | Username | adm*n |
        | VerifyValueWCM | Title    | Hello?World |
        """
        if _should_ignore(expected):
            print(f"[VerifyValueWCM] '{name}' ignored (blank or $IGNORE)")
            return
        import time
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        try:
            to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_VALUE}", default=10)
            timeout = float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
        except Exception:
            timeout = 10.0
        end = time.time() + timeout
        last_error = None
        while time.time() < end:
            try:
                w.okw_verify_value_wcm(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(0.1)
        if last_error:
            raise last_error

    @keyword("VerifyValueREGX")
    def verify_value_regx(self, name, expected):
        """Verifies a widget's value using a regular expression (regex).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Python regular expression used with ``re.search`` (not anchored).

        Special tokens / control parameters:
        - ``$IGNORE`` or ``${IGNORE}`` (case‑insensitive): Skip verification for this field.
        - Empty value (``""``) is ignored if ``${OKW_IGNORE_EMPTY}=YES`` is set.

        Behavior:
        - Case‑sensitive regex search against the current value. Use inline flags (e.g. ``(?i)``)
          for case‑insensitive matching if needed.
        - Retries until ``${OKW_TIMEOUT_VERIFY_VALUE}`` elapses (default 10s), then re‑raises
          the last assertion error.

        Examples:
        | VerifyValueREGX | Username | ^adm.*$ |
        | VerifyValueREGX | Title    | (?i)hello\s+world |
        """
        if _should_ignore(expected):
            print(f"[VerifyValueREGX] '{name}' ignored (blank or $IGNORE)")
            return
        import time
        from robot.libraries.BuiltIn import BuiltIn
        w = resolve_widget(name)
        try:
            to = BuiltIn().get_variable_value("${OKW_TIMEOUT_VERIFY_VALUE}", default=10)
            timeout = float(to) if isinstance(to, (int, float)) else BuiltIn().convert_time(str(to))
        except Exception:
            timeout = 10.0
        end = time.time() + timeout
        last_error = None
        while time.time() < end:
            try:
                w.okw_verify_value_regex(expected)
                return
            except AssertionError as e:
                last_error = e
                time.sleep(0.1)
        if last_error:
            raise last_error

    @keyword("VerifyExist")
    def verify_exist(self, name, expected):
        """Verifies whether a widget exists (present in the UI) or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Must be ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable. This keyword does not support ``$IGNORE`` or empty suppression.

        Behavior:
        - Resolves the widget and polls ``adapter.element_exists(locator)`` until
          ``${OKW_TIMEOUT_VERIFY_EXIST}`` (default 2s) using ``${OKW_POLL_VERIFY}`` (default 0.1s).
        - Passes when the actual existence matches ``expected``; otherwise raises AssertionError.

        Examples:
        | VerifyExist | LoginButton | YES |
        | VerifyExist | LegacyLink  | NO  |
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyExist] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_EXIST}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(adapter.element_exists(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyExist] Element '{name}' should exist, but it does not.")
        else:
            raise AssertionError(f"[VerifyExist] Element '{name}' should NOT exist, but it does.")

    @keyword("LogValue")
    def log_value(self, name):
        """Logs the current value/content of a widget to the console.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Resolves the widget and logs its value via ``okw_log_value()``.

        Examples:
        | LogValue | Username |
        """
        resolve_widget(name).okw_log_value()

    @keyword("HasValue")
    def has_value(self, name):
        resolve_widget(name).okw_has_value()

    @keyword("MemorizeValue")
    def memorize_value(self, name, variable):
        """Stores the current widget value into a Robot Framework variable.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``variable``: Target variable name without the ``${}`` brackets (e.g. ``USER_VAL``).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Reads the widget value via ``okw_memorize_value()`` and sets ``${variable}``
          using Robot's BuiltIn ``Set Test Variable``.

        Examples:
        | MemorizeValue   | Username | USER_VAL |
        | Should Be Equal | ${USER_VAL} | admin |
        """
        value = resolve_widget(name).okw_memorize_value()
        from robot.libraries.BuiltIn import BuiltIn
        BuiltIn().set_test_variable(f"${{{variable}}}", value)

    @keyword("SetFocus")
    def set_focus(self, name):
        """Sets keyboard focus to a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Resolves the widget and calls adapter ``focus(locator)`` to move focus to it.

        Examples:
        | SelectWindow | LoginDialog |
        | SetFocus     | Username    |
        | TypeKey      | Username    | admin |
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        adapter.focus(widget.locator)

    @keyword("VerifyHasFocus")
    def verify_has_focus(self, name, expected):
        """Verifies whether a widget currently has keyboard focus.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: Must be ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Polls ``adapter.has_focus(locator)`` until ``${OKW_TIMEOUT_VERIFY_FOCUS}`` (default 2s)
          using ``${OKW_POLL_VERIFY}`` (default 0.1s). Passes when state matches ``expected``;
          otherwise raises AssertionError.

        Examples:
        | SetFocus        | Username |
        | VerifyHasFocus  | Username | YES |
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyHasFocus] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_FOCUS}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(adapter.has_focus(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyHasFocus] Element '{name}' should have focus, but it does not.")
        else:
            raise AssertionError(f"[VerifyHasFocus] Element '{name}' should NOT have focus, but it does.")

    @keyword("VerifyIsVisible")
    def verify_visible(self, name, expected):
        """Verifies whether a widget is visible or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Requires adapter method ``is_visible(locator)``; polls until
          ``${OKW_TIMEOUT_VERIFY_VISIBLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        - Passes when state matches ``expected``; otherwise raises AssertionError.

        Examples:
        | VerifyIsVisible | Banner | YES |
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        # Strict: adapter must support method
        is_visible = _require_adapter_method(adapter, 'is_visible', widget, name, 'VerifyIsVisible')
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyIsVisible] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_VISIBLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(is_visible(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyIsVisible] Element '{name}' should be visible, but it is not.")
        else:
            raise AssertionError(f"[VerifyIsVisible] Element '{name}' should NOT be visible, but it is.")

    @keyword("VerifyIsEnabled")
    def verify_enabled(self, name, expected):
        """Verifies whether a widget is enabled or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Requires adapter method ``is_enabled(locator)``; polls until
          ``${OKW_TIMEOUT_VERIFY_ENABLED}`` (default 2s) using ``${OKW_POLL_VERIFY}``.

        Examples:
        | VerifyIsEnabled | Submit | YES |
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        is_enabled = _require_adapter_method(adapter, 'is_enabled', widget, name, 'VerifyIsEnabled')
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyIsEnabled] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_ENABLED}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(is_enabled(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyIsEnabled] Element '{name}' should be enabled, but it is not.")
        else:
            raise AssertionError(f"[VerifyIsEnabled] Element '{name}' should NOT be enabled, but it is.")

    @keyword("VerifyIsEditable")
    def verify_editable(self, name, expected):
        """Verifies whether a widget is editable or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Requires adapter method ``is_editable(locator)``; polls until
          ``${OKW_TIMEOUT_VERIFY_EDITABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        is_editable = _require_adapter_method(adapter, 'is_editable', widget, name, 'VerifyIsEditable')
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyIsEditable] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_EDITABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(is_editable(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyIsEditable] Element '{name}' should be editable, but it is not.")
        else:
            raise AssertionError(f"[VerifyIsEditable] Element '{name}' should NOT be editable, but it is.")

    @keyword("VerifyIsFocusable")
    def verify_focusable(self, name, expected):
        """Verifies whether a widget is focusable or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Requires adapter method ``is_focusable(locator)``; polls until
          ``${OKW_TIMEOUT_VERIFY_FOCUSABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        is_focusable = _require_adapter_method(adapter, 'is_focusable', widget, name, 'VerifyIsFocusable')
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyIsFocusable] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_FOCUSABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(is_focusable(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyIsFocusable] Element '{name}' should be focusable, but it is not.")
        else:
            raise AssertionError(f"[VerifyIsFocusable] Element '{name}' should NOT be focusable, but it is.")

    @keyword("VerifyIsClickable")
    def verify_clickable(self, name, expected):
        """Verifies whether a widget is clickable or not.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``expected``: ``YES`` or ``NO`` (case‑insensitive).

        Special tokens / control parameters:
        - Not applicable.

        Behavior:
        - Requires adapter method ``is_clickable(locator)``; polls until
          ``${OKW_TIMEOUT_VERIFY_CLICKABLE}`` (default 2s) using ``${OKW_POLL_VERIFY}``.
        """
        widget = resolve_widget(name)
        adapter = context.get_adapter()
        # Strict: adapter must support method
        is_clickable = _require_adapter_method(adapter, 'is_clickable', widget, name, 'VerifyIsClickable')
        expected = str(expected).strip().upper()
        if expected not in ("YES", "NO"):
            raise ValueError(f"[VerifyIsClickable] Expected must be 'YES' or 'NO', got '{expected}'")
        import time
        timeout = _get_time("${OKW_TIMEOUT_VERIFY_CLICKABLE}", 2.0)
        poll = _get_poll()
        end = time.time() + timeout
        last = None
        while time.time() < end:
            last = bool(is_clickable(widget.locator))
            if (expected == "YES" and last) or (expected == "NO" and not last):
                return
            time.sleep(poll)
        if expected == "YES":
            raise AssertionError(f"[VerifyIsClickable] Element '{name}' should be clickable, but it is not.")
        else:
            raise AssertionError(f"[VerifyIsClickable] Element '{name}' should NOT be clickable, but it is.")

    @keyword("ExecuteJS")
    def execute_js(self, script: str):
        """Executes raw JavaScript in the current browser context.

        Arguments:
        - ``script``: JavaScript source to execute. Must be a self‑contained string.

        Why this exists:
        - Power‑escape hatch for scenarios not covered by high‑level keywords or
          adapter APIs (e.g., interacting with tricky widgets, reading transient
          DOM state, invoking browser APIs).
        - Useful for debugging and temporary workarounds while a proper keyword
          is being added.

        Behavior:
        - Supported with web adapters that expose SeleniumLibrary as ``adapter.sl``.
          Internally calls ``SeleniumLibrary.Execute Javascript`` and returns its result.
        - Return value mirrors SeleniumLibrary semantics: primitives and JSON‑serializable
          results are returned; complex DOM objects are typically not serializable.

        Limitations & notes:
        - Works only when the active adapter provides ``execute_javascript`` (web context).
        - Runs in the page context: subject to same‑origin policy and the page's CSP.
        - Prefer dedicated keywords for maintainability; reserve this for exceptions.

        Examples:
        | ${title}= | ExecuteJS | return document.title; |
        | ${len}=   | ExecuteJS | return document.querySelectorAll('input').length; |
        | ExecuteJS | document.querySelector('#email').value = 'user@example.com'; |
        | ExecuteJS | window.localStorage.setItem('feature_flag','on'); |
        """
        adapter = context.get_adapter()
        # Selenium adapter exposes its SeleniumLibrary as 'sl'
        if hasattr(adapter, 'sl') and hasattr(adapter.sl, 'execute_javascript'):
            return adapter.sl.execute_javascript(script)
        a = adapter.__class__.__name__
        raise RuntimeError(f"[ExecuteJS] Not supported by adapter '{a}'")
