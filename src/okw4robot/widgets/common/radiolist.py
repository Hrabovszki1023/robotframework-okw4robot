from ..base.base_widget import BaseWidget


class RadioList(BaseWidget):
    """Group of radio buttons. Requires group name via YAML extras.

    YAML example:
      MyRadios:
        class: okw4robot.widgets.common.radiolist.RadioList
        group: paymentMethod   # radio group/name attribute

    Optional:
      locator: container (e.g. fieldset) or a name selector (e.g. css:[name="paymentMethod"]).
      If locator is a container, selection is performed within it by value.
      If locator targets the name attribute, selection uses name+value.
    """

    def __init__(self, adapter, locator, **options):
        super().__init__(adapter, locator, **options)
        self.group = options.get('group')
        # group is preferred, but not strictly required if locator provides [name="..."]

    def _extract_name_from_locator(self):
        loc = self.locator
        if isinstance(loc, dict) and len(loc) == 1:
            key, sel = list(loc.items())[0]
            if key == 'css' and sel and 'name=' in sel:
                import re
                m = re.search(r'name\s*=\s*"([^"]+)"', sel)
                if m:
                    return m.group(1)
        if isinstance(loc, str) and loc.startswith('css:') and 'name=' in loc:
            import re
            m = re.search(r'name\s*=\s*"([^"]+)"', loc)
            if m:
                return m.group(1)
        return None

    def _container_css(self):
        loc = self.locator
        if isinstance(loc, dict) and len(loc) == 1:
            key, sel = list(loc.items())[0]
            if key == 'css':
                return sel
        if isinstance(loc, str) and loc.startswith('css:'):
            return loc.split(':',1)[1]
        return None

    def okw_select(self, value):
        self._wait_before('write')
        # Strategy 1: locator names the radio group via [name="..."]
        name_from_loc = self._extract_name_from_locator()
        if name_from_loc:
            self.adapter.select_radio(name_from_loc, value)
            return
        # Strategy 2: container locator → select radio by value inside container
        container = self._container_css()
        if container:
            combined = f"css:{container} input[type='radio'][value='{value}']"
            self.adapter.click(combined)
            return
        # Fallback: use provided group (legacy)
        if not self.group:
            raise ValueError("RadioList needs either 'group' or a locator with [name=...] or a container locator")
        self.adapter.select_radio(self.group, value)

    def okw_verify_value(self, expected):
        name_from_loc = self._extract_name_from_locator()
        if name_from_loc:
            self.adapter.radio_button_should_be_set_to(name_from_loc, expected)
            return
        container = self._container_css()
        if container:
            # Read checked value within container
            checked = f"css:{container} input[type='radio']:checked"
            val = self.adapter.get_attribute(checked, 'value')
            if val != expected:
                raise AssertionError(f"[RadioList] Expected '{expected}', got '{val}'")
            return
        if not self.group:
            raise ValueError("RadioList needs either 'group' or a locator with [name=...] or a container locator")
        # Legacy name+value verification
        self.adapter.radio_button_should_be_set_to(self.group, expected)

    # Counts
    def okw_get_list_count(self) -> int:
        name_from_loc = self._extract_name_from_locator()
        if name_from_loc:
            css = f"css:input[type='radio'][name='{name_from_loc}']"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        container = self._container_css()
        if container:
            css = f"css:{container} input[type='radio']"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        if self.group:
            css = f"css:input[type='radio'][name='{self.group}']"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        raise ValueError("RadioList needs either 'group' or a locator with [name=...] or a container locator")

    def okw_get_selected_count(self) -> int:
        name_from_loc = self._extract_name_from_locator()
        if name_from_loc:
            css = f"css:input[type='radio'][name='{name_from_loc}']:checked"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        container = self._container_css()
        if container:
            css = f"css:{container} input[type='radio']:checked"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        if self.group:
            css = f"css:input[type='radio'][name='{self.group}']:checked"
            return len(self.adapter.sl.get_webelements(self.adapter._resolve(css)))
        raise ValueError("RadioList needs either 'group' or a locator with [name=...] or a container locator")


class WebRadioList(RadioList):
    """Alias/Spezialisierung für Web-RadioList.

    Diese Klasse existiert, um explizit die Web-Variante zu benennen (HTML/DOM‑basiert),
    ohne die Logik zu verändern. Sie erbt die zweistufige Auswahlstrategie von
    RadioList (name‑basiert oder Container‑Locator) und ist nicht treiberspezifisch.
    """
    pass

    # Helpers to read current selected value regardless of strategy
    def _current_value(self):
        name_from_loc = self._extract_name_from_locator()
        if name_from_loc:
            css = f"css:input[type='radio'][name='{name_from_loc}']:checked"
            return self.adapter.get_attribute(css, 'value')
        container = self._container_css()
        if container:
            checked = f"css:{container} input[type='radio']:checked"
            return self.adapter.get_attribute(checked, 'value')
        if self.group:
            css = f"css:input[type='radio'][name='{self.group}']:checked"
            return self.adapter.get_attribute(css, 'value')
        return None

    def okw_verify_value_wcm(self, expected):
        import re
        val = self._current_value() or ""
        pattern = '^' + re.escape(expected) + '$'
        pattern = pattern.replace(r'\\*', '.*').replace(r'\*', '.*').replace(r'\\?', '.').replace(r'\?', '.')
        if not re.compile(pattern, re.DOTALL).match(val):
            raise AssertionError(f"[RadioList-WCM] Value '{val}' does not match pattern '{expected}'")

    def okw_verify_value_regex(self, expected):
        import re
        val = self._current_value() or ""
        if not re.search(expected, val):
            raise AssertionError(f"[RadioList-REGX] Value '{val}' does not match regex '{expected}'")
