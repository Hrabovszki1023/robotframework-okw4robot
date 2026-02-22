# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-02-22

### Highlights
- Bilingual documentation (EN/DE) as defined in CONTRACT
- Comprehensive timeout/parameter documentation with 5-scope cascade
- Widget inheritance strategy documented

### Features
- `ParamsKeywords` added to `OKW4RobotLibrary` MRO — `SetOKWParameter` keyword now available without separate import
- `context.stop_adapter()` crash fix — adapter name captured before clearing reference

### Docs
- `okw_parameters.md` / `okw_parameters_de.md`: Complete rewrite with 5-scope cascade (Global, Project, Widget, Test case, Execution), practical examples, CLI usage
- `widgets_common.md`: 4-level widget inheritance strategy (driver standard, company, project, individual)
- `CONTRACT.md`: Bilingual documentation convention (EN primary `*.md`, DE `*_de.md`)
- `KEYWORDS.md`: Moved from web-selenium (generic keyword reference)
- `README.md`: English version (PyPI-ready); `README_de.md` for German
- Terminology: "treiberunabhaengig" → "treiberagnostisch" across all docs
- Removed 6 Selenium-specific docs that belong in okw-web-selenium

### Breaking Changes
- None

## [0.3.0] - 2025-12-15

### Highlights
- OKW ecosystem integration: okw4robot as driver-agnostic core, web-selenium and java-swing as driver packages
- Package restructured for `src/` layout and PyPI publishing
- Core cleanup: removed all driver-specific code

### Features
- `OKW4RobotLibrary` as single entry point with all keyword mixins
- Widget delegation model: keywords → `okw_*()` methods on widgets
- `OkwWidget` interface with `NotImplementedError` defaults
- YAML locator search with fallback: project → driver packages
- `context.py`: Central runtime context (adapter, app, window)
- `SetOKWParameter` keyword for runtime timeout configuration
- `super().__init__()` added to `OKW4RobotLibrary`

### Docs
- CONTRACT.md: Public contract (architecture, delegation model, YAML format)
- SPECIFICATION.md: Semantic keyword specification
- Full keyword documentation: attribute, caption, label, placeholder, tooltip, table, list
- Synchronization strategy documented
- OKW parameters and timeout reference

### Breaking Changes
- Individual keyword library imports (`AppKeywords`, `HostKeywords`, etc.) replaced by single `OKW4RobotLibrary` import

## [0.2.0] - 2025-10-19

### Highlights
- Packaging for PyPI: pyproject.toml configured for src/ layout; URLs set; Python >= 3.10.
- Licensing: Community (non-commercial) LICENSE with explicit AS-IS warranty disclaimer and liability limitation; COMMERCIAL_LICENSE.md and docs/license_faq.md added.
- Web widget matrix refreshed and normalized (UTF-8, check marks). Table + List keywords integrated in overview.

### Features
- SetValue: $EMPTY implemented and documented; $IGNORE behavior clarified.
- TypeKey: Documented; supports $DELETE to clear content.
- Select: Documented.
- Verify value family: VerifyValue, VerifyValueWCM, VerifyValueREGX documented.
- Verify exist/log/memorize: VerifyExist, LogValue, MemorizeValue documented; SetFocus + VerifyHasFocus documented.
- Verify "Is*" rename: VerifyVisible/Enabled/Editable/Focusable/Clickable → VerifyIsVisible/IsEnabled/IsEditable/IsFocusable/IsClickable; keyword docs added.
- Tooltip: VerifyTooltip/...WCM/...REGX documented.
- Tables: Header-based selection keywords, regex variants, implementation helpers.
- Lists: VerifyListCount, VerifySelectedCount.

### Breaking Changes
- Keyword renames: VerifyVisible/VerifyEnabled/VerifyEditable/VerifyFocusable/VerifyClickable → VerifyIsVisible/IsEnabled/IsEditable/IsFocusable/IsClickable.

### Compatibility
- Python: >= 3.10

[0.4.0]: https://github.com/Hrabovszki1023/robotframework-okw4robot/releases/tag/v0.4.0
[0.3.0]: https://github.com/Hrabovszki1023/robotframework-okw4robot/releases/tag/v0.3.0
[0.2.0]: https://github.com/Hrabovszki1023/robotframework-okw4robot/releases/tag/v0.2.0
