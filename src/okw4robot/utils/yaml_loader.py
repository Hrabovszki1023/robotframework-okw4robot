from pathlib import Path
import yaml
from importlib.resources import files

# Treiber-Pakete, die als Fallback fuer Host-/App-YAMLs durchsucht werden.
# Diese werden optional importiert (try/except ImportError).
_DRIVER_PACKAGES = [
    "okw_web_selenium.locators",
    "okw_java_swing.locators",
]


def load_yaml_with_fallback(name: str) -> dict:
    """
    Laedt eine YAML-Datei aus dem Projektverzeichnis oder faellt auf
    Treiber-Pakete zurueck.
    ``name`` ist ein relativer Pfad ohne ".yaml" - z. B. "LoginDialog"

    Suchreihenfolge:
    1. Projektverzeichnis: ./locators/<name>.yaml
    2. Treiber-Pakete: okw_web_selenium.locators, okw_java_swing.locators (falls installiert)
    """
    parts = name.split("/")

    # 1. Projektverzeichnis: ./locators/<name>.yaml
    local_path = Path("locators") / f"{name}.yaml"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # 2. Treiber-Pakete (optional installiert)
    for pkg in _DRIVER_PACKAGES:
        result = _try_load_from_package(pkg, parts)
        if result is not None:
            return result

    raise FileNotFoundError(
        f"App YAML not found: {name}.yaml "
        f"(searched: project ./locators/, "
        f"driver packages: {', '.join(_DRIVER_PACKAGES)})"
    )


def _try_load_from_package(base_pkg: str, parts: list[str]) -> dict | None:
    """Versucht eine YAML-Datei aus einem Paket zu laden. Gibt None zurueck bei Fehler."""
    try:
        if len(parts) == 1:
            res_path = files(base_pkg).joinpath(f"{parts[0]}.yaml")
        else:
            subpkg = ".".join([base_pkg] + parts[:-1])
            res_path = files(subpkg).joinpath(f"{parts[-1]}.yaml")

        if res_path.exists():
            with open(res_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    except (ImportError, ModuleNotFoundError, TypeError):
        # Paket nicht installiert - ueberspringen
        pass
    return None
