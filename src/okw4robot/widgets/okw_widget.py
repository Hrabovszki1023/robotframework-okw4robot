"""OkwWidget -- Zentrale Schnittstelle fuer alle OKW-Widgets.

Treiber-Pakete (okw_web_selenium, okw_java_swing, ...) liefern konkrete
Implementierungen dieser Klasse.  Keywords rufen ausschliesslich ``okw_*``
Methoden auf -- die treiber-spezifische Klasse entscheidet **wie** die
Aktion umgesetzt wird (Delegation statt Steuerung).

Nicht implementierte Methoden werfen ``NotImplementedError``.  Da Python
keine harte Pruefung erzwingt, koennen Projekte beliebige neue Methoden
hinzufuegen, ohne die Framework-Klasse aendern zu muessen.
"""

from okw4robot.utils.logging_mixin import LoggingMixin


class OkwWidget(LoggingMixin):
    """Basisklasse / Interface fuer alle OKW-Widgets."""

    def __init__(self, adapter, locator, **options):
        self.adapter = adapter
        self.locator = locator
        self.options = options or {}

    # ------------------------------------------------------------------
    # Interaktion
    # ------------------------------------------------------------------
    def okw_click(self):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_click()")

    def okw_double_click(self):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_double_click()")

    def okw_set_value(self, value: str):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_set_value()")

    def okw_select(self, value: str):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_select()")

    def okw_type_key(self, key: str):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_type_key()")

    def okw_delete(self):
        """Loescht den Feldinhalt (TypeKey $DELETE Logik)."""
        raise NotImplementedError(f"{self.__class__.__name__}.okw_delete()")

    # ------------------------------------------------------------------
    # Werte lesen
    # ------------------------------------------------------------------
    def okw_get_value(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_value()")

    def okw_get_text(self) -> str:
        """Sichtbarer Text des Elements (Caption)."""
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_text()")

    def okw_get_attribute(self, name: str) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_attribute()")

    def okw_get_tooltip(self) -> str:
        """Tooltip-Text (title / aria-label)."""
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_tooltip()")

    def okw_get_label(self) -> str:
        """Label-Text (aria-labelledby / <label for=> / aria-label / sichtbarer Text)."""
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_label()")

    def okw_get_placeholder(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_placeholder()")

    # ------------------------------------------------------------------
    # Zustand
    # ------------------------------------------------------------------
    def okw_exists(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_exists()")

    def okw_is_visible(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_is_visible()")

    def okw_is_enabled(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_is_enabled()")

    def okw_is_editable(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_is_editable()")

    def okw_has_focus(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_has_focus()")

    def okw_is_focusable(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_is_focusable()")

    def okw_is_clickable(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_is_clickable()")

    def okw_set_focus(self):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_set_focus()")

    # ------------------------------------------------------------------
    # Listen
    # ------------------------------------------------------------------
    def okw_get_list_count(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_list_count()")

    def okw_get_selected_count(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.okw_get_selected_count()")

    # ------------------------------------------------------------------
    # Tabelle
    # ------------------------------------------------------------------
    def get_row_texts(self, row: int) -> list[str]:
        raise NotImplementedError(f"{self.__class__.__name__}.get_row_texts()")

    def get_column_texts(self, col: int) -> list[str]:
        raise NotImplementedError(f"{self.__class__.__name__}.get_column_texts()")

    def get_cell_text(self, row: int, col: int) -> str:
        raise NotImplementedError(f"{self.__class__.__name__}.get_cell_text()")

    def get_row_count(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.get_row_count()")

    def get_column_count(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.get_column_count()")

    def get_header_names(self) -> list[str]:
        raise NotImplementedError(f"{self.__class__.__name__}.get_header_names()")

    def get_row_key_column_index(self) -> int:
        raise NotImplementedError(f"{self.__class__.__name__}.get_row_key_column_index()")

    # ------------------------------------------------------------------
    # Logging / Memorize -- Defaults mit okw_get_value()
    # ------------------------------------------------------------------
    def okw_log_value(self):
        from robot.api import logger
        value = self.okw_get_value()
        logger.info(f"[{self.__class__.__name__}.okw_log_value] {value}")

    def okw_memorize_value(self) -> str:
        return self.okw_get_value()

    def okw_has_value(self):
        """Prueft ob das Widget einen Wert hat (nicht leer)."""
        value = self.okw_get_value()
        return bool(value and value.strip())
