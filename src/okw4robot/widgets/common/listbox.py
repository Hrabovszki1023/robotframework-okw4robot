from ..base.base_widget import BaseWidget


class ListBox(BaseWidget):
    """Multi-select list widget based on HTML <select multiple>.

    SetValue: accepts a single label or a comma-separated list of labels.
    VerifyValue: compares selected labels (order-insensitive) to expected list.
    """

    def _to_list(self, value):
        if isinstance(value, (list, tuple)):
            return [str(v).strip() for v in value]
        # comma-separated string
        return [v.strip() for v in str(value).split(',') if v.strip()]

    def okw_select(self, value):
        self._wait_before('write')
        labels = self._to_list(value)
        if not labels:
            # Empty selection means unselect all
            self.adapter.unselect_all_from_list(self.locator)
            return
        # For multiselect, adapter functions accept list
        self.adapter.select_by_label(self.locator, labels)

    def okw_verify_value(self, expected):
        expected_labels = set(self._to_list(expected))
        actual_labels = set(self.adapter.get_selected_list_labels(self.locator) or [])
        if expected_labels != actual_labels:
            raise AssertionError(f"[ListBox] Expected {sorted(expected_labels)}, got {sorted(actual_labels)}")

    def okw_log_value(self):
        print("LOG:", self.adapter.get_selected_list_labels(self.locator))

    def okw_memorize_value(self):
        return self.adapter.get_selected_list_labels(self.locator)

    # Counts
    def okw_get_list_count(self) -> int:
        el = self.adapter.sl.get_webelement(self.adapter._resolve(self.locator))
        return len(el.find_elements("css selector", "option"))

    def okw_get_selected_count(self) -> int:
        vals = self.adapter.get_selected_list_values(self.locator) or []
        return len(vals)
