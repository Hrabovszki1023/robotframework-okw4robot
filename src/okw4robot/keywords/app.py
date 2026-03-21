from __future__ import annotations

from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.yaml_loader import load_yaml_with_fallback
from ..utils.loader import load_class
from ..utils.logging_mixin import LoggingMixin

class AppKeywords(LoggingMixin):

    @keyword("StartApp")
    def start_app(self, name: str, config: str | None = None):
        """Startet eine Anwendung anhand ihres YAML-Modells.

        Arguments:
        - ``name``: App-Name / YAML-Pfad (z.B. ``web/LoginApp``).
        - ``config``: Optionaler Konfigurationsname. Wird im YAML unter
          ``__configs__.<config>`` aufgeloest und als dict an den
          Adapter uebergeben (``adapter.apply_config(cfg_data)``).

        YAML-Struktur fuer Konfigurationen::

            MeineApp:
              __self__:
                class: okw_web_selenium.adapters.selenium_web.SeleniumWebAdapter
              __configs__:
                staging:
                  base_url: https://staging.example.com
                  timeout: 30
                production:
                  base_url: https://www.example.com
                  timeout: 10
              LoginDialog:
                Username:
                  class: ...
                  locator: id=user_input

        Beispiele:
        | StartApp | web/LoginApp |
        | StartApp | web/LoginApp | staging |
        """
        cfg_msg = f" mit Konfiguration '{config}'" if config else ""
        self.log_info(f"Starte App '{name}'{cfg_msg}...")
        model = load_yaml_with_fallback(name)
        app_name = name.rsplit("/", 1)[-1]

        if app_name not in model:
            self.log_error(f"App name '{app_name}' not found in YAML root.")
            raise KeyError(f"App name '{app_name}' not found in YAML root")

        app_model = model[app_name]

        # --- Host/Adapter automatisch starten, falls __self__ vorhanden ---
        if "__self__" in app_model and context._adapter is None:
            self_config = app_model["__self__"]
            adapter_cls = load_class(self_config["class"])
            adapter_args = {k: v for k, v in self_config.items() if k != "class"}
            adapter = adapter_cls(**adapter_args)
            context.set_adapter(adapter)
            self.log_info(f"Adapter '{adapter.__class__.__name__}' automatisch gestartet.")

        # --- Konfiguration aufloesen und an Adapter uebergeben ---
        if config is not None:
            configs = app_model.get("__configs__", {})
            if config not in configs:
                available = list(configs.keys()) if configs else []
                raise KeyError(
                    f"Konfiguration '{config}' nicht gefunden im App-Modell '{app_name}'. "
                    f"Verfuegbare Konfigurationen: {available}"
                )
            cfg_data = configs[config]
            adapter = context.get_adapter()
            if hasattr(adapter, 'apply_config'):
                adapter.apply_config(cfg_data)
                self.log_info(f"Konfiguration '{config}' an Adapter uebergeben: {cfg_data}")
            else:
                self.log_info(
                    f"Konfiguration '{config}' geladen: {cfg_data} "
                    f"(Adapter hat kein apply_config, wird im Context gespeichert)"
                )
            context.set_app_config(config, cfg_data)

        context.set_app(app_name, app_model)
        self.log_info(f"App '{app_name}' gestartet.")

    @keyword("SelectWindow")
    def select_window(self, name: str):
        self.log_info(f"Wähle Fenster/Widget '{name}'...")
        context.set_window(name)
        self.log_info(f"Fenster/Widget '{name}' aktiviert.")

    @keyword("StopApp")
    def stop_app(self, name: str | None = None):
        """Beendet eine Anwendung.

        Arguments:
        - ``name``: Optionaler abstrakter Bezeichner der App.
          - Mit Name: Beendet genau diese Anwendung. Prueft ob der Name
            mit der aktuell aktiven App uebereinstimmt.
          - Ohne Name: Beendet alle gestarteten Anwendungen
            (aktuell: die eine aktive App im Context).

        Beispiele:
        | StopApp |                    | # Beendet alle aktiven Apps    |
        | StopApp | web/MeineApp |     | # Beendet genau diese App      |
        """
        if context._app_model is None:
            self.log_error("Keine App aktiv – nichts zu stoppen.")
            raise RuntimeError("StopApp failed: No app is currently active.")

        if name is not None:
            # Mit Name: Pruefen ob die angegebene App aktiv ist
            active_name = context._app_name
            # Vergleich: Voller Pfad (web/MeineApp) oder kurzer Name (MeineApp)
            short_name = name.rsplit("/", 1)[-1]
            if active_name != name and active_name != short_name:
                raise RuntimeError(
                    f"StopApp failed: App '{name}' ist nicht aktiv. "
                    f"Aktive App: '{active_name}'"
                )
            self.log_info(f"Beende App '{name}'.")
        else:
            self.log_info(f"Beende alle aktiven Apps (aktiv: '{context._app_name}').")

        context.stop_app()
