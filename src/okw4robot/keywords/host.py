from robot.api.deco import keyword
from ..runtime.context import context
from ..utils.yaml_loader import load_yaml_with_fallback
from ..utils.loader import load_class
from ..utils.logging_mixin import LoggingMixin


class HostKeywords(LoggingMixin):

    @keyword("StartHost")
    def start_host(self, name: str):
        self.log_info(f"Starte Host '{name}'...")
        model = load_yaml_with_fallback(name)
        adapter_cls = load_class(model[name]["__self__"]["class"])
        adapter_args = {k: v for k, v in model[name]["__self__"].items() if k != "class"}
        adapter = adapter_cls(**adapter_args)
        context.set_adapter(adapter)
        self.log_info(f"Host '{name}' erfolgreich gestartet.")

    @keyword("SelectHost")
    def select_host(self, name: str):
        current = context.get_adapter().__class__.__name__
        self.log_info(f"Prüfe, ob Host '{name}' aktiv ist...")
        if current.lower() != name.lower():
            self.log_error(f"Host-Kontextfehler: '{name}' ist nicht aktiv (aktuell: '{current}')")
            raise RuntimeError(f"Host '{name}' is not active (currently: '{current}')")
        self.log_info(f"Host '{name}' ist aktiv.")

    @keyword("StopHost")
    def stop_host(self):
        self.log_info("Stoppe aktuellen Host...")
        context.stop_adapter()
        self.log_info("Host wurde gestoppt.")

    
