"""OkwWidget -- Zentrale Schnittstelle fuer alle OKW-Widgets.

Treiber-Pakete (okw_web_selenium, okw_java_remoteswing, ...) liefern konkrete
Implementierungen dieser Klasse.  Keywords rufen ausschliesslich ``okw_*``
Methoden auf -- die treiber-spezifische Klasse entscheidet **wie** die
Aktion umgesetzt wird (Delegation statt Steuerung).

Nicht implementierte Methoden werfen ``NotImplementedError``.  Da Python
keine harte Pruefung erzwingt, koennen Projekte beliebige neue Methoden
hinzufuegen, ohne die Framework-Klasse aendern zu muessen.

Pre-Condition-Kette
--------------------
Vor jeder Aktion prueft das Widget Vorbedingungen per Polling:

- **_pre_write()** (SetValue, ClickOn, TypeKey, Select, ...):
  exists → visible → enabled

- **_pre_read()** (VerifyValue, LogValue, MemorizeValue, ...):
  exists

Die Standard-Kette ist hier in ``OkwWidget`` implementiert.
Treiber- oder Projekt-Klassen koennen sie ueberschreiben oder
erweitern (z.B. ``scroll_into_view`` fuer Selenium).
"""

import time

from okw4robot.utils.logging_mixin import LoggingMixin


def _get_timeout(var_name: str, default: float) -> float:
    """Liest einen Timeout-Wert aus dem Robot-Kontext (falls verfuegbar)."""
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value(var_name, default=default)
        return float(val) if isinstance(val, (int, float)) else BuiltIn().convert_time(str(val))
    except Exception:
        return float(default)


def _get_poll() -> float:
    """Liest ``${OKW_POLL_PRECONDITION}`` aus dem Robot-Kontext."""
    return _get_timeout("${OKW_POLL_PRECONDITION}", 0.1)


class OkwWidget(LoggingMixin):
    """Basisklasse / Interface fuer alle OKW-Widgets."""

    def __init__(self, adapter, locator, **options):
        self.adapter = adapter
        self.locator = locator
        self.options = options or {}

    # ------------------------------------------------------------------
    # Pre-Condition Hooks
    # ------------------------------------------------------------------
    def _pre_write(self):
        """Vorbedingungen fuer schreibende Aktionen.

        Standard-Kette: exists → visible → enabled.
        Jede Stufe pollt bis zum konfigurierten Timeout.

        Ueberschreibbar in Treiber- oder Projekt-Klassen, z.B.::

            def _pre_write(self):
                super()._pre_write()
                self._scroll_into_view()   # Selenium-spezifisch
        """
        timeout = _get_timeout("${OKW_TIMEOUT_PRECONDITION}", 5.0)
        poll = _get_poll()
        cls = self.__class__.__name__

        # 1. exists
        self._wait_for(self.okw_exists, True, timeout, poll,
                       f"[{cls}._pre_write] Element existiert nicht (Timeout {timeout}s).")

        # 2. visible
        self._wait_for(self.okw_is_visible, True, timeout, poll,
                       f"[{cls}._pre_write] Element nicht sichtbar (Timeout {timeout}s).")

        # 3. enabled
        self._wait_for(self.okw_is_enabled, True, timeout, poll,
                       f"[{cls}._pre_write] Element nicht aktiviert (Timeout {timeout}s).")

    def _pre_read(self):
        """Vorbedingungen fuer lesende Aktionen.

        Standard-Kette: exists.

        Ueberschreibbar in Treiber- oder Projekt-Klassen.
        """
        timeout = _get_timeout("${OKW_TIMEOUT_PRECONDITION}", 5.0)
        poll = _get_poll()
        cls = self.__class__.__name__

        # 1. exists
        self._wait_for(self.okw_exists, True, timeout, poll,
                       f"[{cls}._pre_read] Element existiert nicht (Timeout {timeout}s).")

    def _wait_for(self, predicate, expected: bool, timeout: float,
                  poll: float, error_msg: str):
        """Pollt *predicate()* bis es *expected* liefert oder Timeout."""
        end = time.monotonic() + timeout
        while True:
            if bool(predicate()) == expected:
                return
            if time.monotonic() >= end:
                raise RuntimeError(error_msg)
            time.sleep(poll)

    # ------------------------------------------------------------------
    # Interaktion
    # ------------------------------------------------------------------
    def okw_click(self):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_click()")

    def okw_double_click(self):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_double_click()")

    def okw_double_click_value(self, value: str):
        """Doppelklick auf einen bestimmten Eintrag/Wert innerhalb des Widgets.

        Wird fuer Listen-artige Widgets verwendet (ListView, TreeView, etc.),
        bei denen ein Eintrag anhand seines Werts gefunden und per Doppelklick
        aktiviert wird.

        Arguments:
        - ``value``: Der gesuchte Wert/Eintrag im Widget.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.okw_double_click_value()")

    def okw_set_value(self, value: str):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_set_value()")

    def okw_select(self, value: str):
        raise NotImplementedError(f"{self.__class__.__name__}.okw_select()")

    def okw_select_menu(self, value: str = ""):
        """Waehlt einen Menue-Eintrag aus.

        Im Gegensatz zu ``okw_click()`` ist ``okw_select_menu()`` semantisch
        fuer Menue-Eintraege reserviert. Der Locator im YAML-Modell bestimmt
        den konkreten Menue-Eintrag -- der Testcode verwendet nur den
        fachlichen Widget-Namen.

        ``value`` ist optional:
        - Leer/nicht angegeben: Menue-Eintrag wird geklickt (Toggle).
        - ``Checked``/``Unchecked``: Zustand wird idempotent gesetzt
          (nur fuer checkbare Menue-Eintraege).
        """
        raise NotImplementedError(f"{self.__class__.__name__}.okw_select_menu()")

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
    # Fenster-Selektion (Window-as-Widget)
    # ------------------------------------------------------------------
    def okw_select_window(self):
        """Selektiert/fokussiert dieses Widget als Fenster-Kontext.

        Wird von ``SelectWindow`` aufgerufen, wenn das Fenster in der YAML
        eine eigene ``class`` und ``locator`` hat.  Die treiberspezifische
        Implementierung entscheidet, welche Aktion ausgefuehrt wird:

        - Swing/RemoteSwingLibrary: ``Select Window``, ``Select Dialog``
          oder ``Select Context``
        - Selenium/Web: scroll-into-view + Fokus auf den Container
        - Desktop/Mobile: plattformspezifische Fensterfokussierung

        Widgets, die nicht als Fenster dienen, muessen diese Methode nicht
        implementieren (Default: NotImplementedError).
        """
        raise NotImplementedError(f"{self.__class__.__name__}.okw_select_window()")

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
