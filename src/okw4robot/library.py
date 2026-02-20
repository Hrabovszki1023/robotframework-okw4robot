"""OKW4Robot – Robot Framework keyword library for GUI test automation.

Driver-agnostic, contract-first widget interaction for web and desktop UIs.
"""
from __future__ import annotations

from robot.api.deco import library

from .keywords.app import AppKeywords
from .keywords.host import HostKeywords
from .keywords.widget_keywords import WidgetKeywords
from .keywords.attribute_keywords import AttributeKeywords
from .keywords.caption_keywords import CaptionKeywords
from .keywords.label_keywords import LabelKeywords
from .keywords.list_keywords import ListKeywords
from .keywords.placeholder_keywords import PlaceholderKeywords
from .keywords.tooltip_keywords import TooltipKeywords
from .keywords.table_keywords import TableKeywords
from .keywords.params import ParamsKeywords


@library(scope="GLOBAL")
class OKW4RobotLibrary(
    HostKeywords,
    AppKeywords,
    WidgetKeywords,
    AttributeKeywords,
    CaptionKeywords,
    LabelKeywords,
    ListKeywords,
    PlaceholderKeywords,
    TooltipKeywords,
    TableKeywords,
    ParamsKeywords,
):
    """Driver-agnostic Robot Framework library for GUI test automation.

    = Overview =

    ``OKW4RobotLibrary`` provides session-less, context-based keyword access to
    GUI widgets defined in YAML locator files. It follows the OKW contract-first
    design: interaction keywords (``SetValue``, ``ClickOn``, …) write to the
    widget state; verification keywords (``VerifyValue``, ``VerifyExist``, …)
    read from it.

    = Drei-Phasen-Modell =

    Alle Keywords dieser Bibliothek arbeiten nach dem OKW-Drei-Phasen-Prinzip:

    | *Phase*      | *Keywords*                                                         | *Aufgabe*                              |
    | Vorbereiten  | ``SetValue``, ``Select``, ``TypeKey``, ``ClickOn``                 | Widget-Zustand setzen / Aktion auslösen |
    | Ausführen    | ``ClickOn``, ``DoubleClickOn``                                     | Aktion am Widget ausführen              |
    | Prüfen       | ``VerifyValue``, ``VerifyExist``, ``VerifyCaption``, …             | Widget-Zustand verifizieren             |

    Beispiel – vollständiger Login-Test:

    | # Vorbereiten
    | StartHost        web
    | StartApp         web/LoginApp
    | SelectWindow     LoginDialog
    | SetValue         Username    admin
    | SetValue         Password    secret
    | # Ausführen
    | ClickOn          OK
    | # Prüfen
    | SelectWindow     Dashboard
    | VerifyExist      WelcomeBanner    YES

    = Adapter-Modell =

    Die Bibliothek ist adapter-agnostisch. Der aktive Adapter (z.B. Selenium,
    JavaRPC) wird über ``StartHost`` gesetzt und im zentralen ``Context``
    gehalten. Alle Keywords greifen über den Context auf den Adapter zu.

    | *Ebene*    | *Beschreibung*                          | *Beispiel*            |
    | Abstrakt   | Logischer Widget-Name im Testfall       | ``Username``          |
    | Konkret    | Locator in der YAML-Datei               | ``id=user_input``     |

    = Locator-Modell =

    Widgets werden in YAML-Dateien beschrieben. Der Pfad wird beim Aufruf von
    ``StartApp`` aufgelöst. Die Datei enthält für jedes Fenster eine Map von
    logischen Namen zu Widget-Definitionen:

    | # locators/LoginApp.yaml
    | LoginApp:
    |   LoginDialog:
    |     Username:
    |       class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
    |       locator: id=user_input
    |     Password:
    |       class: okw_web_selenium.widgets.webse_textfield.WebSe_TextField
    |       locator: id=password_input
    |     OK:
    |       class: okw_web_selenium.widgets.webse_button.WebSe_Button
    |       locator: id=login_btn

    = OKW Tokens =

    | *Token*    | *Verhalten*                                                          |
    | ``$IGNORE``| Keyword wird übersprungen (PASS). Keine Aktion, keine Prüfung.       |
    | ``$EMPTY`` | Bei SetValue: leerer String wird explizit gesetzt (nie ignoriert).    |
    | ``$DELETE``| Bei TypeKey: Feldinhalt löschen (CTRL+A + DELETE oder clear_text).   |

    In Robot-Syntax: ``${IGNORE}`` expandiert zu ``$IGNORE``.

    Der globale Schalter ``${OKW_IGNORE_EMPTY}=YES`` lässt leere Strings
    bei ``SetValue``/``Select``/``TypeKey``/``Verify*`` wie ``$IGNORE`` wirken –
    nützlich für partielle Datenmasken. ``$EMPTY`` ist IMMER wirksam.

    = Timeout- und Polling-Variablen =

    Alle Verify-Keywords nutzen konfigurierbares Timeout-Polling:

    | *Variable*                      | *Standard* | *Verwendet von*                          |
    | ``${OKW_TIMEOUT_VERIFY_VALUE}`` | 10s        | VerifyValue, VerifyValueWCM, VerifyValueREGX |
    | ``${OKW_TIMEOUT_VERIFY_EXIST}`` | 2s         | VerifyExist                              |
    | ``${OKW_TIMEOUT_VERIFY_VISIBLE}`` | 2s       | VerifyIsVisible                          |
    | ``${OKW_TIMEOUT_VERIFY_ENABLED}`` | 2s       | VerifyIsEnabled                          |
    | ``${OKW_TIMEOUT_VERIFY_FOCUS}`` | 2s         | VerifyHasFocus                           |
    | ``${OKW_TIMEOUT_VERIFY_CAPTION}`` | 10s      | VerifyCaption, VerifyCaptionWCM/REGX     |
    | ``${OKW_TIMEOUT_VERIFY_LABEL}`` | 10s        | VerifyLabel, VerifyLabelWCM/REGX         |
    | ``${OKW_TIMEOUT_VERIFY_TOOLTIP}`` | 10s      | VerifyTooltip, VerifyTooltipWCM/REGX     |
    | ``${OKW_TIMEOUT_VERIFY_ATTRIBUTE}`` | 10s    | VerifyAttribute, VerifyAttributeWCM/REGX |
    | ``${OKW_TIMEOUT_VERIFY_PLACEHOLDER}`` | 10s  | VerifyPlaceholder, VerifyPlaceholderWCM/REGX |
    | ``${OKW_TIMEOUT_VERIFY_LIST}``  | 2s         | VerifyListCount, VerifySelectedCount     |
    | ``${OKW_POLL_VERIFY}``          | 0.1s       | Alle Verify-Keywords (Poll-Intervall)    |

    = Import =

    | Library    okw4robot.library.OKW4RobotLibrary

    = Treiber-Pakete =

    Diese Bibliothek ist der generische Kern. Fuer die Anbindung an konkrete
    GUI-Technologien werden Treiber-Pakete benoetigt:

    | *Treiber*                       | *Paket*                                  | *Installation*                                  |
    | Selenium (Chrome, Firefox, ...) | ``robotframework-okw-web-selenium``      | ``pip install robotframework-okw-web-selenium``  |
    | Java Swing (JavaRPC)            | ``robotframework-okw-java-swing``        | ``pip install robotframework-okw-java-swing``    |

    = Abhängigkeiten =

    - ``robotframework >= 6.0``
    - ``PyYAML >= 6.0``
    - ``okw-contract-utils >= 0.2.0``
    """

    ROBOT_LIBRARY_DOC_FORMAT = 'ROBOT'
    ROBOT_LIBRARY_VERSION = '0.4.0'

    def __init__(self):
        """Initialisiert die OKW4RobotLibrary.

        Alle Adapter-, App- und Fensterkontexte starten leer.
        ``StartHost`` muss vor allen Widget-Keywords aufgerufen werden.
        """
        # All keyword mixins are stateless; state lives in the global Context singleton.
        super().__init__()
