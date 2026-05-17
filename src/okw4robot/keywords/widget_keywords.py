ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'
from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.okw_helpers import (
    should_ignore, is_empty, is_delete,
    get_robot_timeout, get_robot_poll,
    normalize_var_name, resolve_widget,
    verify_with_timeout, verify_yes_no_poll,
)
from okw_contract_utils import MatchMode

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
        | SelectWindow  | LoginDialog |
        | SetValue      | Benutzer    | admin  |
        | SetValue      | Passwort    | geheim |
        | *ClickOn*    | *OK*        |
        """
        w = resolve_widget(name)
        w._with_screenshots("ClickOn", w.okw_click)

    @keyword("DoubleClickOn")
    def double_click_on(self, name: str, value: str | None = None):
        """Double‑click on a widget, optionally on a specific value/entry.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).
        - ``value``: (Optional) Value/entry to find within the widget and
          double‑click on. Used for list‑like widgets (ListView, TreeView, etc.)
          where a specific entry matching this value should be double‑clicked.

        Behavior:
        - Without ``value``: Resolves the widget and triggers ``okw_double_click()``.
          Direct double‑click on the widget itself.
        - With ``value``: Resolves the widget and triggers
          ``okw_double_click_value(value)``. The widget searches for the
          matching entry and double‑clicks it.
        - Write intent: underlying widget/adapter typically performs the same
          pre‑action sync as for clicks (exists → visible → enabled → optional scroll).

        Examples:
        | # Direct double‑click on widget
        | SelectWindow    | FileExplorer |
        | *DoubleClickOn* | *MyFile*     |
        |                 |              |
        | # Double‑click on a specific entry within a list widget
        | SelectWindow    | FileExplorer      |
        | *DoubleClickOn* | *FileList*        | *document.txt* |
        """
        widget = resolve_widget(name)
        if value is None:
            widget._with_screenshots("DoubleClickOn", widget.okw_double_click)
        else:
            widget._with_screenshots("DoubleClickOn", widget.okw_double_click_value, value)

    @keyword("MoveOver")
    def move_over(self, name: str):
        """Move the mouse over a widget (hover).

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Behavior:
        - Resolves the widget by name and triggers its ``okw_move_over()``.
        - Useful for revealing hidden elements that appear on mouse hover
          (tooltips, overlays, dropdown menus).

        Example:
        | SelectWindow  | HoversPage  |
        | *MoveOver*    | *Avatar1*   |
        | VerifyValue   | Username1   | user1 |
        """
        w = resolve_widget(name)
        w._with_screenshots("MoveOver", w.okw_move_over)

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
            w = resolve_widget(name)
            w._with_screenshots("SetValue", w.okw_set_value, "")
            return
        if should_ignore(value):
            print(f"[SetValue] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        w._with_screenshots("SetValue", w.okw_set_value, value)

    @keyword("Delete")
    def delete(self, name):
        """Deletes / clears the content of a widget.

        Arguments:
        - ``name``: Logical widget name from the current window (YAML model).

        Behavior:
        - Resolves the widget and calls ``okw_delete()`` to clear its content.
        - Functionally equivalent to ``TypeKey  name  $DELETE``.

        Examples:
        | SelectWindow | MainFrame |
        | Delete       | txtName   |
        """
        w = resolve_widget(name)
        w._with_screenshots("Delete", w.okw_delete)

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
        if should_ignore(value):
            print(f"[Select] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        w._with_screenshots("Select", w.okw_select, value)

    @keyword("SelectMenu")
    def select_menu(self, name, value=""):
        """Selects a menu item by its logical name.

        Arguments:
        - ``name``: Logical menu-item name from the current window (YAML model).
        - ``value``: Optional target state for checkable menu items.
          Without value the menu item is clicked (toggled).
          With value (``Checked``/``Unchecked``) the state is set idempotently.

        The menu item is identified by its locator (typically the component
        ``name`` attribute). The test code never references the visible menu
        text or the menu path -- only the abstract functional name defined
        in the YAML model.

        This keyword corresponds to the BA keyword
        ``Waehle aus: "MENUE" = "fachlicher Bezeichner"``.

        Examples:
        | SelectWindow | MainFrame             |
        | SelectMenu   | TabellenzeileLoeschen |                # click
        | SelectMenu   | Schnellsuche          |                # click
        | SelectMenu   | Statusleiste          | Checked   |    # idempotent
        | SelectMenu   | Statusleiste          | Unchecked |    # idempotent
        """
        if value and should_ignore(value):
            print(f"[SelectMenu] '{name}' ignored ($IGNORE)")
            return
        w = resolve_widget(name)
        w._with_screenshots("SelectMenu", w.okw_select_menu, value)

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
        # Handle special delete token -- delegiert an Widget
        if is_delete(key):
            w = resolve_widget(name)
            w._with_screenshots("TypeKey($DELETE)", w.okw_delete)
            return
        if should_ignore(key):
            print(f"[TypeKey] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        w._with_screenshots("TypeKey", w.okw_type_key, key)

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
        if should_ignore(expected):
            print(f"[VerifyValue] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_VALUE}", 10.0)
        verify_with_timeout(w.okw_get_value, expected, MatchMode.EXACT, timeout, f"[VerifyValue] '{name}'")
        w._log_current_screenshot("VerifyValue")

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
        if should_ignore(expected):
            print(f"[VerifyValueWCM] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_VALUE}", 10.0)
        verify_with_timeout(w.okw_get_value, expected, MatchMode.WCM, timeout, f"[VerifyValueWCM] '{name}'")
        w._log_current_screenshot("VerifyValueWCM")

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
        if should_ignore(expected):
            print(f"[VerifyValueREGX] '{name}' ignored (blank or $IGNORE)")
            return
        w = resolve_widget(name)
        timeout = get_robot_timeout("${OKW_TIMEOUT_VERIFY_VALUE}", 10.0)
        verify_with_timeout(w.okw_get_value, expected, MatchMode.REGX, timeout, f"[VerifyValueREGX] '{name}'")
        w._log_current_screenshot("VerifyValueREGX")

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
        verify_yes_no_poll(
            lambda: widget.okw_exists(),
            expected,
            "${OKW_TIMEOUT_VERIFY_EXIST}", 2.0,
            f"[VerifyExist] '{name}'",
        )

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
        w = resolve_widget(name)
        w.okw_log_value()
        w._log_current_screenshot("LogValue")

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
        resolve_widget(name).okw_set_focus()

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
        verify_yes_no_poll(
            lambda: widget.okw_has_focus(),
            expected,
            "${OKW_TIMEOUT_VERIFY_FOCUS}", 2.0,
            f"[VerifyHasFocus] '{name}'",
        )

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
        verify_yes_no_poll(
            lambda: widget.okw_is_visible(),
            expected,
            "${OKW_TIMEOUT_VERIFY_VISIBLE}", 2.0,
            f"[VerifyIsVisible] '{name}'",
        )

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
        verify_yes_no_poll(
            lambda: widget.okw_is_enabled(),
            expected,
            "${OKW_TIMEOUT_VERIFY_ENABLED}", 2.0,
            f"[VerifyIsEnabled] '{name}'",
        )

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
        verify_yes_no_poll(
            lambda: widget.okw_is_editable(),
            expected,
            "${OKW_TIMEOUT_VERIFY_EDITABLE}", 2.0,
            f"[VerifyIsEditable] '{name}'",
        )

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
        verify_yes_no_poll(
            lambda: widget.okw_is_focusable(),
            expected,
            "${OKW_TIMEOUT_VERIFY_FOCUSABLE}", 2.0,
            f"[VerifyIsFocusable] '{name}'",
        )

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
        verify_yes_no_poll(
            lambda: widget.okw_is_clickable(),
            expected,
            "${OKW_TIMEOUT_VERIFY_CLICKABLE}", 2.0,
            f"[VerifyIsClickable] '{name}'",
        )

