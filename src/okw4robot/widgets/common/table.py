from okw4robot.widgets.base.base_widget import BaseWidget


class Table(BaseWidget):
    def _root(self):
        return self.adapter.sl.get_webelement(self.adapter._resolve(self.locator))

    def _header_cells(self):
        tbl = self._root()
        # Prefer thead>tr>th, fallback to first tr th/td
        heads = tbl.find_elements("css selector", "thead tr th")
        if heads:
            return heads
        heads = tbl.find_elements("css selector", "tr th")
        if heads:
            return heads
        # fallback: first row td
        row = tbl.find_elements("css selector", "tr")
        if row:
            return row[0].find_elements("css selector", "td")
        return []

    def _data_rows(self):
        tbl = self._root()
        rows = tbl.find_elements("css selector", "tbody tr")
        if rows:
            return rows
        # fallback: all tr except thead
        return tbl.find_elements("css selector", "tr")

    def _row_cells(self, row_el):
        cells = row_el.find_elements("css selector", "td")
        if cells:
            return cells
        return row_el.find_elements("css selector", "th")

    def get_row_texts(self, row_index: int):
        # row_index: 0 => header; >=1 => data row (1-based)
        if row_index == 0:
            return [c.text or "" for c in self._header_cells()]
        rows = self._data_rows()
        if 1 <= row_index <= len(rows):
            cells = self._row_cells(rows[row_index - 1])
            return [c.text or "" for c in cells]
        return []

    def get_column_texts(self, col_index: int):
        # data rows only
        out = []
        rows = self._data_rows()
        for r in rows:
            cells = self._row_cells(r)
            if 1 <= col_index <= len(cells):
                out.append(cells[col_index - 1].text or "")
            else:
                out.append("")
        # trim trailing empty rows (if fallback matched header)
        return out

    def get_cell_text(self, row_index: int, col_index: int):
        if row_index == 0:
            heads = self._header_cells()
            if 1 <= col_index <= len(heads):
                return heads[col_index - 1].text or ""
            return ""
        rows = self._data_rows()
        if 1 <= row_index <= len(rows):
            cells = self._row_cells(rows[row_index - 1])
            if 1 <= col_index <= len(cells):
                return cells[col_index - 1].text or ""
        return ""

    def get_row_count(self) -> int:
        return len(self._data_rows())

    def get_column_count(self) -> int:
        heads = self._header_cells()
        if heads:
            return len(heads)
        rows = self._data_rows()
        mx = 0
        for r in rows:
            mx = max(mx, len(self._row_cells(r)))
        return mx
