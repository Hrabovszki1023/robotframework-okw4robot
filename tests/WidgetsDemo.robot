*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW
Library    okw4robot.keywords.placeholder_keywords.PlaceholderKeywords    WITH NAME    PH

*** Variables ***
${DEMO_FILE}    docs/examples/widgets_demo.html

*** Keywords ***
Setup Widgets Demo
    [Documentation]    Start Chrome, open demo HTML, load WidgetsDemo locators
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    ${FILE_URL}=   Evaluate    __import__('pathlib').Path('${DEMO_FILE}').resolve().as_uri()
    SetValue       URL         ${FILE_URL}
    StartApp      web/WidgetsDemo

Teardown Widgets Demo
    StopHost

*** Test Cases ***
TextField Set And Verify
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        Mustermann
    SetValue        Vorname     Max
    VerifyValue     Name        Mustermann
    VerifyValue     Vorname     Max
    Teardown Widgets Demo

MultilineField Set And Verify
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Anmerkung   Mehrzeilige Eingabe\nmit zwei Zeilen
    VerifyValue     Anmerkung   Mehrzeilige Eingabe\nmit zwei Zeilen
    Teardown Widgets Demo

CheckBox Checked And Unchecked
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Verheiratet     Checked
    VerifyValue     Verheiratet     Checked
    SetValue        Verheiratet     Unchecked
    VerifyValue     Verheiratet     Unchecked
    Teardown Widgets Demo

RadioList Select And Verify
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    Select          Zahlungsmethode     paypal
    VerifyValue     Zahlungsmethode     paypal
    Teardown Widgets Demo

RadioList (Container) Select And Verify Lieferung
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    Select          Lieferung     DPD
    VerifyValue     Lieferung     DPD
    Teardown Widgets Demo

RadioLists Cycle And Verify (Value/WCM/REGX)
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    
    # Zahlungsmethode (name-basierte Gruppe)
    Select          Zahlungsmethode     paypal
    VerifyValue     Zahlungsmethode     paypal
    VerifyValueWCM  Zahlungsmethode     *pay*
    VerifyValueREGX  Zahlungsmethode     ^pay.*
    Select          Zahlungsmethode     visa
    VerifyValue     Zahlungsmethode     visa
    VerifyValueWCM  Zahlungsmethode     *isa*
    VerifyValueREGX  Zahlungsmethode     ^vis.*
    Select          Zahlungsmethode     sepa
    VerifyValue     Zahlungsmethode     sepa
    VerifyValueWCM  Zahlungsmethode     *epa*
    VerifyValueREGX  Zahlungsmethode     ^sep.*

    # Lieferung (fieldset/container-basierte Gruppe)
    Select          Lieferung     DHL
    VerifyValue     Lieferung     DHL
    VerifyValueWCM  Lieferung     D*
    VerifyValueREGX  Lieferung     ^DHL$
    Select          Lieferung     UPS
    VerifyValue     Lieferung     UPS
    VerifyValueWCM  Lieferung     U*
    VerifyValueREGX  Lieferung     ^UPS$
    Select          Lieferung     DPD
    VerifyValue     Lieferung     DPD
    VerifyValueWCM  Lieferung     D*
    VerifyValueREGX  Lieferung     ^DPD$
    Select          Lieferung     Hermes
    VerifyValue     Lieferung     Hermes
    VerifyValueWCM  Lieferung     Herm*
    VerifyValueREGX  Lieferung     ^Herm.*
    Select          Lieferung     Selbstabholung
    VerifyValue     Lieferung     Selbstabholung
    VerifyValueWCM  Lieferung     Selbst*
    VerifyValueREGX  Lieferung     ^Selbst.*
    Teardown Widgets Demo

ComboBox Set And Verify
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    # Beide Varianten sind möglich: SetValue oder Select
    SetValue        Geschlecht      Männlich
    VerifyValue     Geschlecht      Männlich
    Select          Geschlecht      Weiblich
    VerifyValue     Geschlecht      Weiblich
    Teardown Widgets Demo

OK Aggregates Values In Status
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        Mustermann
    SetValue        Vorname     Max
    SetValue        Anmerkung   Hallo Welt
    SetValue        Verheiratet    Checked
    Select          Zahlungsmethode  sepa
    Select          Geschlecht   Divers
    ClickOn         OK
    # Das Status-Label enthält mehrere Zeilen. Wir prüfen mit Wildcards auf Teilinhalt.
    VerifyValueWCM  Status      *"Name" = "Mustermann"*
    VerifyValueWCM  Status      *"Vorname" = "Max"*
    VerifyValueWCM  Status      *"Verheiratet" = "Checked"*
    Teardown Widgets Demo

VerifyExist On Status
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    VerifyExist     Status    YES
    Teardown Widgets Demo

$IGNORE Behavior: SetValue Does Nothing
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        Before
    SetValue        Name        $IGNORE
    VerifyValue     Name        Before
    Teardown Widgets Demo

$IGNORE Behavior: Select Does Nothing
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Geschlecht   Männlich
    Select          Geschlecht   $IGNORE
    VerifyValue     Geschlecht   Männlich
    Teardown Widgets Demo

$IGNORE Behavior: TypeKey Does Nothing
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        SomeText
    TypeKey         Name        $IGNORE
    VerifyValue     Name        SomeText
    Teardown Widgets Demo

$IGNORE Behavior: VerifyValue Is Skipped
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        SkipCheck
    VerifyValue     Name        $IGNORE
    # If not ignored, above would assert; reaching here means it was skipped.
    Teardown Widgets Demo

$IGNORE Behavior: VerifyValueWCM/REGX Are Skipped
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        Any
    VerifyValueWCM  Name        $IGNORE
    VerifyValueREGX  Name        $IGNORE
    Teardown Widgets Demo

EMPTY And DELETE Semantics
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        ToDelete
    TypeKey         Name        $DELETE
    VerifyValue     Name        ${EMPTY}
    SetValue        Anmerkung   ${EMPTY}
    VerifyValue     Anmerkung   ${EMPTY}
    Teardown Widgets Demo

Placeholders On Inputs
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    VerifyPlaceholder      Name         Nachname
    VerifyPlaceholderWCM   Vorname      *name*
    VerifyPlaceholderREGX  Anmerkung    ^Mehrzeilige\\s+Eingabe.*
    Teardown Widgets Demo

Memorize And Reuse In Multiline
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    SetValue        Name        Alice
    MemorizeValue   Name        Name
    SetValue        Anmerkung   Gemerkter wert : ${Name}
    VerifyValue     Anmerkung   Gemerkter wert : Alice
    Teardown Widgets Demo

