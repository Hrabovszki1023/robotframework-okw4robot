from okw4robot.utils.logging_mixin import LoggingMixin


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
        self._window = None

    # === HOST / ADAPTER ===
    def set_adapter(self, adapter):
        """
        Setzt den aktiven Adapter (z. B. Selenium).
        Beendet alle bestehenden App- und Fensterkontexte.
        """
        self._adapter = adapter
        self._app_model = None
        self._app_name = None
        self._window = None

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
        self._window = None

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
        self._window = None


    # === WINDOW ===
    def set_window(self, window_name: str):
        """
        Setzt den Fenster-/Widget-Kontext anhand des window_name.

        Gültig für:
        - Fenster aus App-YAMLs (z.B. LoginDialog)
        - Virtuelle Widgets aus Host-YAMLs (z.B. URL, Maximize Window)
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

        self._window = window_name
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

    # === DIAGNOSTICS ===
    def describe(self):
        """Kurzuebersicht des aktuellen Kontextes fuer Diagnose und Logging."""
        return {
            "adapter": type(self._adapter).__name__ if self._adapter else None,
            "app": self._app_name,
            "window": self._window
        }

context = Context()
