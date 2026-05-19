import time

from okw4robot.utils.logging_mixin import LoggingMixin
from okw4robot.utils.loader import load_class


# Reservierte Keys auf Fenster-/Widget-Ebene (keine Kind-Widgets)
_RESERVED_KEYS = frozenset({"class", "locator", "__self__", "__context__"})


def _get_precondition_timeout() -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value("${OKW_TIMEOUT_PRECONDITION}", default=5.0)
        return float(val) if isinstance(val, (int, float)) else BuiltIn().convert_time(str(val))
    except Exception:
        return 5.0


def _get_precondition_poll() -> float:
    try:
        from robot.libraries.BuiltIn import BuiltIn
        val = BuiltIn().get_variable_value("${OKW_POLL_PRECONDITION}", default=0.1)
        return float(val) if isinstance(val, (int, float)) else BuiltIn().convert_time(str(val))
    except Exception:
        return 0.1


class Context(LoggingMixin):
    """Zentraler Laufzeitkontext fuer OKW4Robot.

    Haelt den aktiven Host/Adapter, den aktuellen App-Kontext (Name und Modell)
    sowie das aktuell ausgewaehlte Fenster/Widget. Keywords greifen auf diesen
    Kontext zu, um Operationen gegen die Anwendung gezielt auszufuehren.
    """
    def __init__(self):
        """Initialisiert leeren Kontext (kein Adapter, keine App, kein Fenster)."""
        self._adapter = None
        self._app_model = None
        self._app_name = None
        self._app_config_name = None
        self._app_config_data = None
        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None

    # === HOST / ADAPTER ===
    def set_adapter(self, adapter):
        """
        Setzt den aktiven Adapter (z. B. Selenium).
        Beendet alle bestehenden App- und Fensterkontexte.
        """
        self._adapter = adapter
        self._app_model = None
        self._app_name = None
        self._app_config_name = None
        self._app_config_data = None
        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None

        self.log_info(f"[Context] Adapter '{adapter.__class__.__name__}' wurde gesetzt.")
        print(f"[Context] Adapter '{adapter.__class__.__name__}' wurde gesetzt.")


    def stop_adapter(self):
        """
        Entfernt den aktiven Adapter (z. B. beim Test-TearDown).
        Setzt auch App- und Fensterkontext zurück.
        """
        if self._adapter is None:
            raise RuntimeError("[Context] Kein aktiver Adapter zum Stoppen.")

        adapter_name = self._adapter.__class__.__name__

        self._adapter = None
        self._app_model = None
        self._app_name = None
        self._app_config_name = None
        self._app_config_data = None
        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None

        print(f"[Context] Adapter '{adapter_name}' wurde gestoppt.")

    def get_adapter(self):
        """Gibt den aktiven Adapter zurueck.

        Returns:
        - Adapter-Instanz

        Raises:
        - RuntimeError: Wenn kein Adapter aktiv ist.
        """
        if not self._adapter:
            raise RuntimeError("No host/adapter is active.")
        return self._adapter

    # === APP CONFIG ===
    def set_app_config(self, config_name: str, config_data: dict):
        """Speichert die aktive App-Konfiguration.

        Args:
            config_name: Name der Konfiguration (z.B. 'staging').
            config_data: Konfigurationsdaten als dict aus dem YAML.
        """
        self._app_config_name = config_name
        self._app_config_data = config_data
        print(f"[Context] App-Konfiguration '{config_name}' gesetzt.")

    def get_app_config(self) -> dict | None:
        """Gibt die aktive App-Konfiguration zurueck oder None."""
        return self._app_config_data

    def get_app_config_name(self) -> str | None:
        """Gibt den Namen der aktiven App-Konfiguration zurueck oder None."""
        return self._app_config_name

    # === APP ===
    def set_app(self, name: str, model: dict):
        """
        Setzt den aktuellen App-Kontext.
        Voraussetzung: Ein Host/Adapter muss bereits aktiv sein.
        """
        if self._adapter is None:
            raise RuntimeError(
                f"[Context] Kein Host aktiv – "
                f"du musst vorher 'Start Host' ausführen, bevor du 'Start App {name}' aufrufst."
            )

        self._app_name = name
        self._app_model = model
        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None

        print(f"[Context] Anwendung '{name}' wurde gestartet.")

    def select_app(self, name: str):
        """
        Aktiviert eine Anwendung aus dem geladenen App-Kontext.
        Erwartet, dass zuvor 'Start App' mit dieser Anwendung aufgerufen wurde.
        """
        if self._app_model is None:
            raise RuntimeError(
                f"[Context] Keine App aktiv – du musst vorher 'Start App {name}' ausführen."
            )

        if name != self._app_name:
            raise ValueError(
                f"[Context] App-Kontextfehler: Gewünschte App ist '{name}', "
                f"aber aktuell ist '{self._app_name}' aktiv."
            )

        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None
        print(f"[Context] Anwendung '{name}' wurde ausgewählt.")


    def stop_app(self):
        """
        Beendet die aktuell aktive App (setzt Modell, Name und Fensterkontext zurück).
        """
        if self._app_model is None:
            raise RuntimeError("[Context] Keine App aktiv – kann nichts beenden.")

        print(f"[Context] Anwendung '{self._app_name}' wurde beendet.")

        self._app_model = None
        self._app_name = None
        self._app_config_name = None
        self._app_config_data = None
        self._window = None
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None


    # === WINDOW ===
    def set_window(self, window_name: str):
        """Setzt den Fenster-/Widget-Kontext und selektiert das Fenster.

        1. Validiert, dass App-Modell und Adapter aktiv sind.
        2. Loeest das Fenster als Widget auf (class + locator aus YAML).
        3. Ruft ``okw_select_window()`` auf dem Widget auf -- die
           treiberspezifische Klasse entscheidet, welche Aktion
           ausgefuehrt wird (z.B. SwingLibrary ``Select Window``).
        4. Setzt den Fensterkontext fuer nachfolgende Widget-Zugriffe.
        """
        if not self._app_model:
            raise RuntimeError(
                f"[Context] Kein App- oder Host-Modell geladen – "
                f"du musst vorher 'Start App' ausführen."
            )

        if window_name not in self._app_model:
            modell_name = self._app_name or "<Host-Modell>"
            raise KeyError(
                f"[Context] Fenster oder Host-Element '{window_name}' wurde im Modell "
                f"'{modell_name}' nicht gefunden."
            )

        window_model = self._app_model[window_name]

        # --- Fenster als Widget aufloesen und selektieren ---
        from okw4robot.utils.okw_helpers import _log_resolved_element
        if isinstance(window_model, dict) and "class" in window_model:
            widget_cls = load_class(window_model["class"])
            adapter = self.get_adapter()
            locator = window_model.get("locator")
            _log_resolved_element(window_name, locator)
            extras = {k: v for k, v in window_model.items()
                      if k not in _RESERVED_KEYS and not isinstance(v, dict)}
            window_widget = widget_cls(adapter, locator, **extras)
            self._wait_for_window(window_widget, window_name)
            window_widget.okw_select_window()
            window_widget._log_current_screenshot(f"SelectWindow [{window_name}]")
            self.log_info(
                f"[Context] Fenster '{window_name}' selektiert via "
                f"{widget_cls.__name__}.okw_select_window()."
            )
        elif isinstance(window_model, dict):
            self_cfg = window_model.get("__self__", {})
            if "class" in self_cfg and "locator" in self_cfg:
                widget_cls = load_class(self_cfg["class"])
                adapter = self.get_adapter()
                locator = self_cfg.get("locator")
                _log_resolved_element(window_name, locator)
                window_widget = widget_cls(adapter, locator)
                self._wait_for_window(window_widget, window_name)
                window_widget._log_current_screenshot(
                    f"SelectWindow [{window_name}]"
                )

        self._window = window_name
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None
        modell_name = self._app_name or "<Host-Modell>"
        print(f"[Context] Fenster/Widget '{window_name}' im Modell '{modell_name}' ausgewählt.")


    def get_current_window_model(self):
        """Gibt das Modell des aktuell ausgewaehlten Fensters/Widgets zurueck.

        Returns:
        - Modellobjekt (z.B. dict) des selektierten Fensters/Widgets.

        Raises:
        - RuntimeError: Wenn Adapter, App oder Fenster nicht gesetzt sind.
        """
        if self._adapter is None:
            raise RuntimeError("No adapter available.")
        if self._app_model is None:
            raise RuntimeError("No app active.")
        if self._window is None:
            raise RuntimeError("No window selected.")
        return self._app_model[self._window]

    # === WINDOW PRECONDITION ===
    def _wait_for_window(self, window_widget, window_name: str):
        timeout = _get_precondition_timeout()
        poll = _get_precondition_poll()
        end = time.monotonic() + timeout
        while True:
            try:
                if window_widget.okw_exists():
                    return
            except NotImplementedError:
                return
            except Exception:
                pass
            if time.monotonic() >= end:
                raise RuntimeError(
                    f"[SelectWindow] Fenster '{window_name}' existiert nicht "
                    f"(Timeout {timeout}s)."
                )
            time.sleep(poll)

    # === CONTEXT (Repeating Structures) ===
    def set_context(self, group_name: str, placeholders: dict):
        model = self.get_current_window_model()
        if group_name not in model:
            raise KeyError(
                f"[Context] Context-Gruppe '{group_name}' nicht im Fenster "
                f"'{self._window}' gefunden."
            )
        group = model[group_name]
        if not isinstance(group, dict) or "__context__" not in group:
            raise KeyError(
                f"[Context] Gruppe '{group_name}' hat keinen __context__-Eintrag."
            )
        ctx_def = group["__context__"]
        locator = ctx_def.get("locator")
        if not locator:
            raise ValueError(
                f"[Context] __context__ in '{group_name}' hat keinen Locator."
            )
        self._context_group = group_name
        self._context_placeholders = placeholders
        self._context_locator = locator
        print(f"[Context] SetContext '{group_name}' mit {placeholders}.")

    def clear_context(self):
        self._context_group = None
        self._context_placeholders = {}
        self._context_locator = None

    # === DIAGNOSTICS ===
    def describe(self):
        """Kurzuebersicht des aktuellen Kontextes fuer Diagnose und Logging."""
        return {
            "adapter": type(self._adapter).__name__ if self._adapter else None,
            "app": self._app_name,
            "config": self._app_config_name,
            "window": self._window,
            "context_group": self._context_group,
            "context_placeholders": self._context_placeholders if self._context_group else None,
        }

context = Context()
