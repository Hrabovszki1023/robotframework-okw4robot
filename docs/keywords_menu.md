# Menu Keywords

Diese Seite dokumentiert das `SelectMenu`-Keyword und das Menu-Widget-Pattern.

---

## SelectMenu

```
SelectMenu    <Name>
SelectMenu    <Name>    <Value>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Name` | ja | Logischer Name des Menu-Eintrags (YAML-Key im aktuellen Fenster) |
| `Value` | nein | Optionaler Zielzustand fuer checkbare Eintraege |

### Verhalten ohne Value (Toggle/Click)

Der Menu-Eintrag wird angeklickt. Bei normalen `JMenuItem` fuehrt das die Aktion aus.
Bei `JCheckBoxMenuItem` wird der Zustand getoggelt.

```robot
SelectMenu    DateiNeu
SelectMenu    AnsichtStatusleiste
```

### Verhalten mit Value (Idempotent)

Nur fuer checkbare Menu-Eintraege (`JCheckBoxMenuItem`).
Setzt den Zustand **idempotent** -- wenn der Zustand bereits stimmt,
passiert nichts.

```robot
SelectMenu    AnsichtStatusleiste    Checked
SelectMenu    AnsichtStatusleiste    Unchecked
```

Gueltige Werte (case-insensitive): `Checked`/`Unchecked`, `True`/`False`, `Yes`/`No`, `1`/`0`

### RadioButtonMenuItem

`JRadioButtonMenuItem` benoetigt **keinen** Value-Parameter.
RadioButtons sind von sich aus idempotent -- ein Klick auf einen
bereits selektierten RadioButton aendert nichts.

```robot
SelectMenu    AnsichtKompakt
SelectMenu    AnsichtErweitert
SelectMenu    AnsichtNormal
```

> **Hinweis:** `VerifyValue` ist fuer `JRadioButtonMenuItem` nicht verfuegbar
> (SwingLibrary `ClassCastException`). Die Auswahl ist ueber `SelectMenu`
> sichergestellt.

### $IGNORE-Token

```robot
SelectMenu    DateiNeu    $IGNORE    # wird uebersprungen
SelectMenu    DateiNeu              # wird ausgefuehrt (leerer Value ist kein $IGNORE)
```

---

## YAML-Locator Pattern fuer Menues

### JMenu (Obermenue)

JMenu ist ein sichtbares Swing-Component und verwendet den normalen `locator`:

```yaml
MenuDatei:
  class: okw_java_remoteswing.widgets.remotesw_menu.RemoteSw_Menu
  locator: { name: "mnuDatei" }
```

### JMenuItem (einfacher Eintrag)

JMenuItems sind **nicht** im Component-Tree sichtbar, wenn das Menue geschlossen ist.
Deshalb verwenden sie `menu_path` statt `locator`:

```yaml
DateiNeu:
  class: okw_java_remoteswing.widgets.remotesw_menuitem.RemoteSw_MenuItem
  menu_path: "Datei|Neu"
```

`menu_path` enthaelt den **sichtbaren Text** der Menue-Hierarchie,
getrennt durch `|` (Pipe). SwingLibrary's `Select From Main Menu`
verwendet diesen Pfad intern.

### JCheckBoxMenuItem

```yaml
AnsichtStatusleiste:
  class: okw_java_remoteswing.widgets.remotesw_checkboxmenuitem.RemoteSw_CheckBoxMenuItem
  menu_path: "Ansicht|Statusleiste"
```

Unterstuetzt zusaetzlich:
- `VerifyValue` -- gibt `Checked` oder `Unchecked` zurueck
- `SetValue` -- setzt idempotent wie `SelectMenu` mit Value

### JRadioButtonMenuItem

```yaml
AnsichtNormal:
  class: okw_java_remoteswing.widgets.remotesw_radiobuttonmenuitem.RemoteSw_RadioButtonMenuItem
  locator: { name: "mnuAnsichtNormal" }
  menu_path: "Ansicht|Normal"
```

> Hat sowohl `locator` (fuer potentielle zukuenftige Erweiterungen)
> als auch `menu_path` (fuer die Auswahl).

---

## Widget-Klassen Uebersicht

| Swing-Klasse | OKW-Widget | SelectMenu | VerifyValue | SetValue |
|---|---|---|---|---|
| `JMenu` | `RemoteSw_Menu` | ja (oeffnet Menue) | nein | nein |
| `JMenuItem` | `RemoteSw_MenuItem` | ja (klickt) | nein | nein |
| `JCheckBoxMenuItem` | `RemoteSw_CheckBoxMenuItem` | ja (toggle/idempotent) | `Checked`/`Unchecked` | `Checked`/`Unchecked` |
| `JRadioButtonMenuItem` | `RemoteSw_RadioButtonMenuItem` | ja (klickt) | nicht moeglich | nein |

---

## Zusaetzliche Keywords fuer Menues

| Keyword | Anwendung | Beispiel |
|---|---|---|
| `VerifyCaption` | Sichtbarer Text des Eintrags | `VerifyCaption  DateiNeu  Neu` |
| `VerifyCaptionWCM` | Wildcard auf sichtbaren Text | `VerifyCaptionWCM  DateiSpeichernUnter  Speichern*` |
| `VerifyListCount` | Anzahl Unter-Eintraege (JMenu) | `VerifyListCount  MenuDatei  6` |
| `VerifyValue` | Zustand CheckBoxMenuItem | `VerifyValue  AnsichtStatusleiste  Checked` |
| `SetValue` | Zustand setzen (CheckBoxMenuItem) | `SetValue  AnsichtStatusleiste  Unchecked` |

---

## Code-Referenzen

- Keyword: `src/okw4robot/keywords/widget_keywords.py` → `SelectMenu`
- Widget-Interface: `src/okw4robot/widgets/okw_widget.py` → `okw_select_menu()`
- RemoteSwing-Widgets: `src/okw_java_remoteswing/widgets/remotesw_menu*.py`
- Adapter: `src/okw_java_remoteswing/adapters/remote_swing_adapter.py`
