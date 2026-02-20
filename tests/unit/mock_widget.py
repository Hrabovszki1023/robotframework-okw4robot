"""MockWidget -- Virtuelles Widget fuer Keyword-Unit-Tests.

Implementiert alle ``okw_*`` Methoden mit konfigurierbaren Rueckgabewerten
und Aufruf-Protokollierung. Braucht keinen echten Adapter oder Browser.

Verwendung::

    w = MockWidget()
    w.mock_value = "Hello"
    assert w.okw_get_value() == "Hello"

    w.okw_set_value("World")
    assert w.calls == [("okw_set_value", ("World",))]
"""

from okw4robot.widgets.okw_widget import OkwWidget


class MockWidget(OkwWidget):
    """Virtuelles Widget das alle okw_* Methoden bedient."""

    def __init__(self, **overrides):
        # Kein echter Adapter noetig
        super().__init__(adapter=None, locator=None)

        # Konfigurierbare Rueckgabewerte
        self.mock_value: str = overrides.get("value", "")
        self.mock_text: str = overrides.get("text", "")
        self.mock_tooltip: str = overrides.get("tooltip", "")
        self.mock_label: str = overrides.get("label", "")
        self.mock_placeholder: str = overrides.get("placeholder", "")
        self.mock_attributes: dict = overrides.get("attributes", {})

        self.mock_exists: bool = overrides.get("exists", True)
        self.mock_visible: bool = overrides.get("visible", True)
        self.mock_enabled: bool = overrides.get("enabled", True)
        self.mock_editable: bool = overrides.get("editable", True)
        self.mock_has_focus: bool = overrides.get("has_focus", False)
        self.mock_focusable: bool = overrides.get("focusable", True)
        self.mock_clickable: bool = overrides.get("clickable", True)

        self.mock_list_count: int = overrides.get("list_count", 0)
        self.mock_selected_count: int = overrides.get("selected_count", 0)

        # Tabellen-Daten: Liste von Listen (Zeilen x Spalten)
        self.mock_headers: list[str] = overrides.get("headers", [])
        self.mock_rows: list[list[str]] = overrides.get("rows", [])

        # Aufruf-Protokoll: [(method_name, args), ...]
        self.calls: list[tuple] = []

    def _record(self, method: str, *args):
        self.calls.append((method, args))

    # ------------------------------------------------------------------
    # Interaktion
    # ------------------------------------------------------------------
    def okw_click(self):
        self._record("okw_click")

    def okw_double_click(self):
        self._record("okw_double_click")

    def okw_set_value(self, value: str):
        self._record("okw_set_value", value)
        self.mock_value = value

    def okw_select(self, value: str):
        self._record("okw_select", value)
        self.mock_value = value

    def okw_type_key(self, key: str):
        self._record("okw_type_key", key)

    def okw_delete(self):
        self._record("okw_delete")
        self.mock_value = ""

    # ------------------------------------------------------------------
    # Werte lesen
    # ------------------------------------------------------------------
    def okw_get_value(self) -> str:
        self._record("okw_get_value")
        return self.mock_value

    def okw_get_text(self) -> str:
        self._record("okw_get_text")
        return self.mock_text

    def okw_get_attribute(self, name: str) -> str:
        self._record("okw_get_attribute", name)
        return self.mock_attributes.get(name, "")

    def okw_get_tooltip(self) -> str:
        self._record("okw_get_tooltip")
        return self.mock_tooltip

    def okw_get_label(self) -> str:
        self._record("okw_get_label")
        return self.mock_label

    def okw_get_placeholder(self) -> str:
        self._record("okw_get_placeholder")
        return self.mock_placeholder

    # ------------------------------------------------------------------
    # Zustand
    # ------------------------------------------------------------------
    def okw_exists(self) -> bool:
        self._record("okw_exists")
        return self.mock_exists

    def okw_is_visible(self) -> bool:
        self._record("okw_is_visible")
        return self.mock_visible

    def okw_is_enabled(self) -> bool:
        self._record("okw_is_enabled")
        return self.mock_enabled

    def okw_is_editable(self) -> bool:
        self._record("okw_is_editable")
        return self.mock_editable

    def okw_has_focus(self) -> bool:
        self._record("okw_has_focus")
        return self.mock_has_focus

    def okw_is_focusable(self) -> bool:
        self._record("okw_is_focusable")
        return self.mock_focusable

    def okw_is_clickable(self) -> bool:
        self._record("okw_is_clickable")
        return self.mock_clickable

    def okw_set_focus(self):
        self._record("okw_set_focus")
        self.mock_has_focus = True

    # ------------------------------------------------------------------
    # Listen
    # ------------------------------------------------------------------
    def okw_get_list_count(self) -> int:
        self._record("okw_get_list_count")
        return self.mock_list_count

    def okw_get_selected_count(self) -> int:
        self._record("okw_get_selected_count")
        return self.mock_selected_count

    # ------------------------------------------------------------------
    # Tabelle
    # ------------------------------------------------------------------
    def get_row_texts(self, row: int) -> list[str]:
        self._record("get_row_texts", row)
        if row == 0:
            return list(self.mock_headers)
        if 1 <= row <= len(self.mock_rows):
            return list(self.mock_rows[row - 1])
        return []

    def get_column_texts(self, col: int) -> list[str]:
        self._record("get_column_texts", col)
        out = []
        for r in self.mock_rows:
            if 1 <= col <= len(r):
                out.append(r[col - 1])
            else:
                out.append("")
        return out

    def get_cell_text(self, row: int, col: int) -> str:
        self._record("get_cell_text", row, col)
        if row == 0:
            if 1 <= col <= len(self.mock_headers):
                return self.mock_headers[col - 1]
            return ""
        if 1 <= row <= len(self.mock_rows):
            r = self.mock_rows[row - 1]
            if 1 <= col <= len(r):
                return r[col - 1]
        return ""

    def get_row_count(self) -> int:
        self._record("get_row_count")
        return len(self.mock_rows)

    def get_column_count(self) -> int:
        self._record("get_column_count")
        return len(self.mock_headers) if self.mock_headers else (
            max((len(r) for r in self.mock_rows), default=0)
        )

    def get_header_names(self) -> list[str]:
        self._record("get_header_names")
        return list(self.mock_headers)

    def get_row_key_column_index(self) -> int:
        self._record("get_row_key_column_index")
        return 1
