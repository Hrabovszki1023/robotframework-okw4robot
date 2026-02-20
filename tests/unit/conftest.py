"""Pytest-Konfig fuer okw4robot Keyword-Unit-Tests.

Stellt Fixtures bereit die:
- Robot Framework BuiltIn patchen (kein laufender RF-Server noetig)
- resolve_widget() patchen, um MockWidgets zu liefern
"""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from .mock_widget import MockWidget


# ---- Robot Framework BuiltIn Mock ----------------------------------------

class FakeBuiltIn:
    """Minimaler Mock fuer robot.libraries.BuiltIn.BuiltIn."""

    _variables = {}

    def get_variable_value(self, name, default=None):
        return self._variables.get(name, default)

    def set_test_variable(self, name, value):
        self._variables[name] = value

    def convert_time(self, value):
        return float(value)


@pytest.fixture(autouse=True)
def _patch_robot():
    """Patcht robot.api und robot.libraries.BuiltIn fuer headless Tests."""
    fake_bi = FakeBuiltIn()
    fake_bi._variables = {
        "${OKW_TIMEOUT_VERIFY_VALUE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_ATTRIBUTE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_CAPTION}": 0.1,
        "${OKW_TIMEOUT_VERIFY_LABEL}": 0.1,
        "${OKW_TIMEOUT_VERIFY_TOOLTIP}": 0.1,
        "${OKW_TIMEOUT_VERIFY_PLACEHOLDER}": 0.1,
        "${OKW_TIMEOUT_VERIFY_EXIST}": 0.1,
        "${OKW_TIMEOUT_VERIFY_HASFOCUS}": 0.1,
        "${OKW_TIMEOUT_VERIFY_VISIBLE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_ENABLED}": 0.1,
        "${OKW_TIMEOUT_VERIFY_EDITABLE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_FOCUSABLE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_CLICKABLE}": 0.1,
        "${OKW_TIMEOUT_VERIFY_LIST_COUNT}": 0.1,
        "${OKW_TIMEOUT_VERIFY_SELECTED_COUNT}": 0.1,
        "${OKW_POLL_VERIFY}": 0.01,
        "${OKW_IGNORE_EMPTY}": "NO",
    }

    # Fake robot.api.logger
    fake_logger = MagicMock()

    # Fake robot.api.deco.keyword = identity decorator
    def fake_keyword(name=None, tags=None, types=None):
        def decorator(func):
            return func
        if callable(name):
            return name
        return decorator

    # Erstelle fake robot Module
    robot_mod = types.ModuleType("robot")
    robot_api = types.ModuleType("robot.api")
    robot_deco = types.ModuleType("robot.api.deco")
    robot_libs = types.ModuleType("robot.libraries")
    robot_bi_mod = types.ModuleType("robot.libraries.BuiltIn")

    robot_api.logger = fake_logger
    robot_api.deco = robot_deco
    robot_deco.keyword = fake_keyword

    class BuiltInFactory:
        """Gibt immer dieselbe FakeBuiltIn-Instanz zurueck."""
        def __new__(cls):
            return fake_bi

    robot_bi_mod.BuiltIn = BuiltInFactory

    robot_mod.api = robot_api
    robot_mod.libraries = robot_libs
    robot_libs.BuiltIn = robot_bi_mod

    # Module registrieren
    saved = {}
    for mod_name, mod in [
        ("robot", robot_mod),
        ("robot.api", robot_api),
        ("robot.api.deco", robot_deco),
        ("robot.libraries", robot_libs),
        ("robot.libraries.BuiltIn", robot_bi_mod),
    ]:
        saved[mod_name] = sys.modules.get(mod_name)
        sys.modules[mod_name] = mod

    yield fake_bi

    # Aufraemen
    for mod_name, orig in saved.items():
        if orig is None:
            sys.modules.pop(mod_name, None)
        else:
            sys.modules[mod_name] = orig


# ---- Widget-Registry fuer Tests -----------------------------------------

_widget_registry: dict[str, MockWidget] = {}


def register_widget(name: str, widget: MockWidget):
    """Registriert ein MockWidget unter einem logischen Namen."""
    _widget_registry[name] = widget


def clear_widgets():
    """Leert die Widget-Registry."""
    _widget_registry.clear()


def _mock_resolve_widget(name: str) -> MockWidget:
    if name not in _widget_registry:
        raise KeyError(f"Widget '{name}' not found (test registry)")
    return _widget_registry[name]


@pytest.fixture(autouse=True)
def _patch_resolve_widget():
    """Patcht resolve_widget in allen Keyword-Modulen."""
    clear_widgets()
    modules_to_patch = [
        "okw4robot.keywords.widget_keywords",
        "okw4robot.keywords.attribute_keywords",
        "okw4robot.keywords.caption_keywords",
        "okw4robot.keywords.label_keywords",
        "okw4robot.keywords.tooltip_keywords",
        "okw4robot.keywords.placeholder_keywords",
        "okw4robot.keywords.list_keywords",
        "okw4robot.keywords.table_keywords",
    ]
    patches = []
    for mod_path in modules_to_patch:
        target = f"{mod_path}.resolve_widget"
        try:
            p = patch(target, side_effect=_mock_resolve_widget)
            p.start()
            patches.append(p)
        except (AttributeError, ModuleNotFoundError):
            pass

    yield

    for p in patches:
        p.stop()
    clear_widgets()
