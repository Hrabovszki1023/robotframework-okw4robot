from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.yaml_loader import load_yaml_with_fallback
from ..utils.logging_mixin import LoggingMixin

class AppKeywords(LoggingMixin):

    @keyword("StartApp")
    def start_app(self, name: str):
        self.log_info(f"Starte App '{name}'...")
        model = load_yaml_with_fallback(name)
        app_name = name.rsplit("/", 1)[-1]

        if app_name not in model:
            self.log_error(f"App name '{app_name}' not found in YAML root.")
            raise KeyError(f"App name '{app_name}' not found in YAML root")

        app_model = model[app_name]
        context.set_app(app_name, app_model)
        self.log_info(f"App '{app_name}' gestartet.")

    @keyword("SelectWindow")
    def select_window(self, name: str):
        self.log_info(f"Wähle Fenster/Widget '{name}'...")
        context.set_window(name)
        self.log_info(f"Fenster/Widget '{name}' aktiviert.")

    @keyword("StopApp")
    def stop_app(self):
        if context._app_model is None:
            self.log_error("Keine App aktiv – nichts zu stoppen.")
            raise RuntimeError("Stop App failed: No app is currently active.")

        self.log_info(f"Beende App '{context._app_name}'.")
        context.stop_app()

    
