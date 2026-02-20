# Moduluebersicht fuer OKW4Robot

## `okw4robot/__init__.py`
Initialisiert das OKW4Robot-Paket.

## `okw4robot/keywords/__init__.py`
Initialisiert die Robot Framework Schluesselwortmodule.

## `okw4robot/keywords/app.py`
Stellt App-bezogene Keywords bereit (Start App, Select Window etc.).

## `okw4robot/keywords/host.py`
Stellt Host-bezogene Keywords bereit (Start Host, Stop Host etc.).

## `okw4robot/keywords/widget_keywords.py`
Widget-Interaktions-Keywords (ClickOn, SetValue, VerifyValue etc.).
Delegiert an `okw_*`-Methoden des aufgeloesten Widgets.

## `okw4robot/keywords/attribute_keywords.py`
Attribut-Keywords (VerifyAttribute, LogAttribute etc.).
Delegiert an `okw_get_attribute()`.

## `okw4robot/keywords/caption_keywords.py`
Caption-Keywords (VerifyCaption, LogCaption etc.).
Delegiert an `okw_get_text()`.

## `okw4robot/keywords/label_keywords.py`
Label-Keywords (VerifyLabel, LogLabel etc.).
Delegiert an `okw_get_label()`.

## `okw4robot/keywords/tooltip_keywords.py`
Tooltip-Keywords (VerifyTooltip, LogTooltip etc.).
Delegiert an `okw_get_tooltip()`.

## `okw4robot/keywords/placeholder_keywords.py`
Placeholder-Keywords (VerifyPlaceholder etc.).
Delegiert an `okw_get_placeholder()`.

## `okw4robot/keywords/list_keywords.py`
Listen-Keywords (VerifyListCount, VerifySelectedCount).
Delegiert an `okw_get_list_count()`, `okw_get_selected_count()`.

## `okw4robot/keywords/table_keywords.py`
Tabellen-Keywords (VerifyTableCell, VerifyTableRow etc.).
Delegiert an `get_cell_text()`, `get_row_texts()` etc.

## `okw4robot/runtime/context.py`
Verwaltet den aktuellen Testkontext (Adapter, App, Window).

## `okw4robot/utils/loader.py`
Laedt Python-Klassen aus Strings (z.B. aus YAML-`class`-Eintraegen).

## `okw4robot/utils/logging_mixin.py`
Stellt ein LoggingMixin zur Verfuegung fuer strukturiertes Logging.

## `okw4robot/utils/yaml_loader.py`
Laedt YAML-Dateien mit Fallback-Strategie:
Projektverzeichnis → Treiber-Pakete (okw_web_selenium, okw_java_swing).

## `okw4robot/utils/okw_helpers.py`
Zentrale Helfer: `resolve_widget()`, `verify_with_timeout()`,
`verify_yes_no_poll()`, Token-Pruefungen, Timeout-Zugriff.

## `okw4robot/widgets/okw_widget.py`
`OkwWidget` -- Zentrale Schnittstelle fuer alle OKW-Widgets.
Definiert alle `okw_*`-Methoden mit `NotImplementedError`-Defaults.
Treiber-Pakete erben hiervon (z.B. `WebSe_Base`).

## `okw4robot/widgets/base/base_widget.py`
Legacy `BaseWidget` mit Sync-Helfern. Wird noch von alten
`widgets/common/`-Klassen genutzt. Perspektivisch durch
`OkwWidget` + treiberspezifische Basisklassen ersetzt.
