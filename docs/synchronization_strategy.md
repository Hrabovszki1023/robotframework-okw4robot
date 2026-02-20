# Synchronisations‑/Delay‑Strategie (Web)

Diese Seite beschreibt, wie OKW vor Interaktionen mit Widgets kurz synchronisiert, um flakige Tests zu vermeiden. Die Strategie ist konfigurierbar auf drei Ebenen: global, pro Widget‑Klasse und pro Widget‑Instanz (YAML).

---

## Ziele

- Vor schreibenden Aktionen (Click/SetValue/TypeKey/Select) werden grundlegende Bedingungen geprüft (existiert, sichtbar, enabled, ggf. editierbar, projektweite Busy‑Overlays verschwunden).
- Vor lesenden Aktionen (Verify*/Memorize*/Log*) werden Minimal‑PreChecks angewendet (existiert; optional sichtbar). Verify* warten schon auf den Sollwert und ergänzen damit die inhaltliche Synchronisation.

---

## Intents (Zugriffsarten)

- Write: Click, SetValue, TypeKey, Select
- Read: Verify*, Memorize*, Log*

Die Konfiguration unterscheidet nach Intent (write/read).

---

## Prüf‑Bausteine (Checks)

In dieser Reihenfolge – so weit aktiviert – werden geprüft:

1. exists: Element befindet sich im DOM
2. scroll_into_view: in den Viewport scrollen (zentriert)
3. visible: Element ist sichtbar
4. enabled: Element ist aktiv (nicht disabled/aria‑disabled)
5. editable: Eingabeelement ist editierbar (nicht readonly; ggf. contenteditable)
6. until_not_visible: projekt‑spezifische Selektoren sind nicht sichtbar (z. B. Busy‑Overlay)

Alle Checks werden zusammen durch ein Timeout „zeitgedeckelt“ (Timeout + Polling).

---

## Konfigurationsebenen (Merge‑Reihenfolge)

1. Instanz (Locator‑YAML): höchste Priorität
2. Widget‑Klasse (Code/Projektklasse): mittlere Priorität
3. Global (Robot‑Variablen): Default‑Werte

Vereinigung: Instanz überschreibt Klassenprofil überschreibt Global Defaults.

---

## Globale Defaults (Robot‑Variablen)

Diese Variablen steuern das Standardverhalten:

- `${OKW_SYNC_TIMEOUT_WRITE}`: Timeout (Sekunden oder Robot‑Zeitformat) für Write‑Sync (Default: 10)
- `${OKW_SYNC_TIMEOUT_READ}`: Timeout für Read‑Sync (Default: 5)
- `${OKW_SYNC_POLL}`: Polling‑Intervall (Sekunden, Default: 0.1)
- `${OKW_SYNC_SCROLL_INTO_VIEW}`: YES/NO – beim Intent Write/Click in den Viewport scrollen (Default: YES)
- `${OKW_SYNC_CHECK_EDITABLE}`: YES/NO – bei TextField/MultilineField/ComboBox die Editierbarkeit prüfen (Default: YES)
- `${OKW_BUSY_SELECTORS_WRITE}`: Liste/CSV projektweiter Busy‑Selektoren, die vor Write unsichtbar sein müssen (z. B. `css:.busy-overlay, css:.spinner`)
- `${OKW_BUSY_SELECTORS_READ}`: Busy‑Selektoren für Read (meist leer)

Beispiel (Variables‑Section):

```robotframework
*** Variables ***
${OKW_SYNC_TIMEOUT_WRITE}         10
${OKW_SYNC_TIMEOUT_READ}           5
${OKW_SYNC_POLL}                 0.1
${OKW_SYNC_SCROLL_INTO_VIEW}     YES
${OKW_SYNC_CHECK_EDITABLE}       YES
${OKW_BUSY_SELECTORS_WRITE}      css:.busy-overlay, css:.spinner
${OKW_BUSY_SELECTORS_READ}       
```

---

## Instanz‑Konfiguration (Locator‑YAML)

Pro Widget kann das Verhalten überschrieben/ergänzt werden:

```yaml
Name:
  class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
  locator: { css: '[data-testid="tf-name"]' }
  wait:
    write:
      timeout: 15           # überschreibt global
      poll: 0.2
      exists: true
      visible: true
      enabled: true
      editable: true        # z. B. hart aktivieren/deaktivieren
      scroll_into_view: true
      until_not_visible:
        - css:.global-loader
        - css:.dialog-backdrop
    read:
      exists: true
      visible: false
      timeout: 5
```

- `until_not_visible` ist genau für projekt‑spezifische Synchronisation gedacht (Busy‑Overlays u. ä.).

---

## Implementierungsdetails

- Adapter (Selenium): stellt Helfer bereit
  - `scroll_into_view(locator)` – zentriertes Scrollen per JS
  - `is_enabled(locator)` – Selenium `is_enabled()`
  - `is_editable(locator)` – prüft `readonly`, `contenteditable`, `tag_name`
  - `wait_until_visible`/`wait_until_not_visible` – via SeleniumLibrary
- WebSe_Base:
  - `_get_global_sync(intent)` – liest globale Defaults
  - `_merge_wait(intent)` – merged Instanz‑Overrides (und ggf. Klassenprofil)
  - `_wait_before(intent)` – führt die Checks aus
- Eingehängt vor schreibenden Aktionen in:
  - Button: `okw_click`, `okw_double_click`
  - TextField: `okw_set_value`, `okw_type_key`, `okw_click`
  - ComboBox: `okw_set_value`, `okw_select`
  - CheckBox: `okw_click`, `okw_set_value`
  - RadioList: `okw_select`
  - ListBox: `okw_select`

Lesende Aktionen (Verify*/Memorize*/Log*) nutzen weiterhin die jeweiligen Verify‑Warte‑Mechanismen; ein Minimal‑PreCheck (exists) kann über `wait.read` erzwungen werden.

---

## Beispiele

### Global per Suite setzen

```robotframework
*** Variables ***
${OKW_SYNC_TIMEOUT_WRITE}       12
${OKW_BUSY_SELECTORS_WRITE}     css:.app-busy, css:.loading
```

### Instanz mit projektspezifischem Busy‑Overlay

```yaml
Speichern:
  class: okw_web_selenium.widgets.webse_button.WebSe_Button
  locator: { css: '[data-testid="btn-save"]' }
  wait:
    write:
      until_not_visible:
        - css:.page-overlay
        - css:.toast.loading
```

---

## Hinweise

- Die Sync‑Checks sind bewusst minimalinvasiv und sollen Stabilität erhöhen, ohne Aktionen zu blockieren, wenn es nicht nötig ist.
- „editable“ ist standardmäßig nur für Eingabeelemente (TextField/MultilineField/ComboBox) aktiv.
- Projektweite Busy‑Selektoren können global gesetzt und bei Bedarf instanzweise ergänzt werden.
