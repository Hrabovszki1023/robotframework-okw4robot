from ..base.base_widget import BaseWidget


class ComboBox(BaseWidget):
    """Combo with text entry and optional dropdown selection.

    Strategy for SetValue:
    1) Try selecting by label (if it's a native <select>),
    2) If that fails, clear and type the text, then press ENTER.
    """

    def _is_editable(self) -> bool:
        # YAML override: editable: true/false; fallback to adapter.is_editable
        if 'editable' in self.options:
            try:
                return bool(self.options.get('editable'))
            except Exception:
                pass
        try:
            if hasattr(self.adapter, 'is_editable'):
                return bool(self.adapter.is_editable(self.locator))
        except Exception:
            pass
        return False

    def okw_set_value(self, value):
        self._wait_before('write')
        editable = self._is_editable()
        if not editable:
            # Non-editable → must be a selection from list; fail if not present
            try:
                self.adapter.select_by_label(self.locator, value)
                return
            except Exception as e:
                raise AssertionError(f"[ComboBox] Non-editable. Value '{value}' not found in options or selection failed: {e}")
        # Editable → type value and commit; fallback to select if needed
        try:
            self.adapter.clear_text(self.locator)
        except Exception:
            pass
        self.adapter.input_text(self.locator, value)
        try:
            self.adapter.press_keys(self.locator, "ENTER")
        except Exception:
            pass
        # Best-effort verification to ensure the value took effect
        try:
            actual = self.adapter.get_value(self.locator)
            if actual != value:
                # try selecting by label as fallback for type-ahead that didn't commit
                self.adapter.select_by_label(self.locator, value)
        except Exception:
            pass

    def okw_select(self, value):
        # Alias to set value (supports both semantics)
        self._wait_before('write')
        self.okw_set_value(value)

    def okw_type_key(self, key):
        # Forward key presses to the combo/input element
        try:
            self.adapter.press_keys(self.locator, key)
        except Exception:
            # As a fallback, try sending to active element
            self.adapter.press_keys(None, key)

    def okw_verify_value(self, expected):
        actual = None
        # Try value (input) first
        try:
            actual = self.adapter.get_value(self.locator)
        except Exception:
            pass
        # Fallback to selected label (native select)
        if actual is None or actual == "":
            try:
                labels = self.adapter.get_selected_list_labels(self.locator)
                if labels:
                    actual = labels[0]
            except Exception:
                pass
        if actual != expected:
            raise AssertionError(f"[ComboBox] Expected '{expected}', got '{actual}'")

    def okw_log_value(self):
        try:
            val = self.adapter.get_value(self.locator)
        except Exception:
            val = None
        print("LOG:", val)

    def okw_memorize_value(self):
        try:
            return self.adapter.get_value(self.locator)
        except Exception:
            labels = self.adapter.get_selected_list_labels(self.locator)
            return labels[0] if labels else None

    # Placeholder (for combos that are input-based)
    def _get_placeholder(self):
        ph = None
        try:
            ph = self.adapter.get_attribute(self.locator, 'placeholder')
        except Exception:
            ph = None
        return ph if ph is not None else ""

    def okw_verify_placeholder(self, expected):
        actual = self._get_placeholder()
        if actual != expected:
            raise AssertionError("[VerifyPlaceholder] Expected '" + str(expected) + "', got '" + str(actual) + "'")

    def okw_verify_placeholder_wcm(self, expected):
        import re
        value = self._get_placeholder()
        pattern = '^' + re.escape(expected).replace(r'\\*', '.*').replace(r'\\?', '.') + '$'
        if not re.compile(pattern, re.DOTALL).match(value):
            raise AssertionError("[VerifyPlaceholderWCM] Value '" + str(value) + "' does not match pattern '" + str(expected) + "'")

    def okw_verify_placeholder_regex(self, expected):
        import re
        value = self._get_placeholder()
        if not re.search(expected, value or ""):
            raise AssertionError("[VerifyPlaceholderREGX] Value '" + str(value) + "' does not match regex '" + str(expected) + "'")

    # Counts (basic support)
    def okw_get_list_count(self) -> int:
        el = self.adapter.sl.get_webelement(self.adapter._resolve(self.locator))
        tag = (el.tag_name or '').lower()
        if tag == 'select':
            return len(el.find_elements("css selector", "option"))
        raise NotImplementedError("[ComboBox] List count not supported for non-native select. Model a list widget explicitly if needed.")

    def okw_get_selected_count(self) -> int:
        # Native <select>: number of selected options (typically 0/1)
        try:
            labels = self.adapter.get_selected_list_labels(self.locator) or []
            if labels:
                return len(labels)
        except Exception:
            pass
        # Input-based combo: treat non-empty value as one selected/entered value
        try:
            val = self.adapter.get_value(self.locator) or ""
            return 1 if str(val) != "" else 0
        except Exception:
            return 0
