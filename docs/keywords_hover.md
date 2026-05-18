# Schluesselwort: MoveOver (Hover)

## Zweck

`MoveOver` bewegt den Mauszeiger ueber ein Widget, ohne zu klicken.
Damit werden versteckte Elemente sichtbar gemacht, die erst bei
Mouse-Hover erscheinen — z.B. Tooltips, Overlays, Dropdown-Menues
oder Benutzerinformationen.

---

## Syntax

```
MoveOver    <Name>
```

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| `Name` | ja | Logischer Name des Widgets (YAML-Key im aktuellen Fenster) |

---

## Verhalten

1. Widget wird im aktuellen Fensterkontext aufgeloest.
2. Pre-Condition `_pre_read()` wird geprueft (Element existiert).
3. Der Mauszeiger wird ueber das Element bewegt (`ActionChains.move_to_element()`).
4. Vorher/Nachher-Screenshots werden automatisch im Robot Log geloggt.

**Kein Klick.** `MoveOver` loest nur das `mouseover`/`mouseenter`-Event
aus. Zum Klicken gibt es `ClickOn`.

---

## Typische Anwendungsfaelle

### Hover-Overlays sichtbar machen

Elemente die erst bei Mouse-Hover erscheinen (z.B. Benutzerkarten,
Aktions-Buttons, Kontextinformationen):

```robot
SelectWindow   HoversPage
MoveOver       Avatar1
VerifyValue    Username1    user1
VerifyExist    ProfilLink   YES
```

### Tooltips pruefen

Tooltip-Text wird per `VerifyTooltip` geprueft. `MoveOver` stellt
sicher, dass das Element im Viewport sichtbar und fokussiert ist:

```robot
MoveOver            HelpIcon
VerifyTooltip       HelpIcon    Bitte gueltige E-Mail eingeben
VerifyTooltipWCM    HelpIcon    *E-Mail*
```

### Dropdown-Menues oeffnen

Menues die bei Hover aufklappen (nicht bei Klick):

```robot
MoveOver       NavigationMenu
VerifyExist    SubmenuEinstellungen    YES
ClickOn        SubmenuEinstellungen
```

---

## Zusammenspiel mit SetContext

`MoveOver` funktioniert mit `SetContext` fuer wiederholende
Strukturen. Beispiel: Drei identische Benutzerkarten, die bei
Hover unterschiedliche Informationen zeigen:

```robot
*** Test Cases ***
Hover Zeigt User1 Info
    OnFailNOISE    SetContext    UserCard    user1
    MoveOver       Avatar
    VerifyValueWCM    Benutzername    *user1*

Hover Zeigt User2 Info
    OnFailNOISE    SetContext    UserCard    user2
    MoveOver       Avatar
    VerifyValueWCM    Benutzername    *user2*
```

**YAML (mit `__context__`):**

```yaml
UserCard:
  __context__:
    locator: { xpath: '//div[@class="figure"][.//h5[contains(text(),"{UserName}")]]' }
  Avatar:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { xpath: './/img[@alt="User Avatar"]' }
  Benutzername:
    class: okw_web_selenium.widgets.webse_label.WebSe_Label
    locator: { xpath: './/h5' }
```

---

## 5-Phasen-Modell

`MoveOver` gehoert in der Regel zu **Phase 4 (Testaktion)** — es ist
die Aktion, die den Hover-Zustand herstellt:

```robot
*** Test Cases ***
Hover Overlay Pruefen
    # Phase 1-3: Vorbereitung
    OnFailNOISE    StartApp       MyAppChrome
    OnFailNOISE    SelectWindow   Chrome
    OnFailNOISE    SetValue       URL    ${URL}
    OnFailNOISE    SelectWindow   HoversPage
    OnFailNOISE    SetContext     UserCard    user1
    # Phase 4: Testaktion
    MoveOver       Avatar
    # Phase 5: Verifikation
    VerifyValueWCM    Benutzername    *user1*
    VerifyExist       ProfilLink      YES
```

---

## Pre-Conditions und Sync

| Aspekt | Verhalten |
|---|---|
| Pre-Condition | `_pre_read()` — nur `exists` (kein `visible`/`enabled` noetig) |
| Timeout | Konfigurierbar ueber `${OKW_TIMEOUT_PRECONDITION}` (Standard 5s) |
| Scroll | Kein automatisches Scroll-into-View (read intent) |
| Screenshots | Vorher/Nachher automatisch im Robot Log |

---

## Unterstützte Widgets

`MoveOver` ist in `WebSe_Base` implementiert und wird an alle
Selenium-Web-Widgets vererbt:

| Widget | MoveOver |
|---|---|
| `WebSe_Button` | ja |
| `WebSe_TextField` | ja |
| `WebSe_MultilineField` | ja |
| `WebSe_CheckBox` | ja |
| `WebSe_ComboBox` | ja |
| `WebSe_Label` | ja |
| `WebSe_Link` | ja |
| `WebSe_ListBox` | ja |
| `WebSe_RadioList` | ja |
| `WebSe_Table` | ja |

Fuer andere Treiber (Java Swing, FlaUI) muss `okw_move_over()` in
der jeweiligen Widget-Basis implementiert werden.

---

## Code-Referenzen

- Keyword: `src/okw4robot/keywords/widget_keywords.py` → `MoveOver`
- Widget-Interface: `src/okw4robot/widgets/okw_widget.py` → `okw_move_over()`
- Selenium Widget: `src/okw_web_selenium/widgets/webse_base.py` → `okw_move_over()`
- Selenium Adapter: `src/okw_web_selenium/adapters/selenium_web.py` → `move_over()`
