*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.list_keywords.ListKeywords        WITH NAME    LST
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW

*** Variables ***
${DEMO_FILE}    docs/examples/widgets_demo.html

*** Keywords ***
Setup Widgets Demo
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    ${FILE_URL}=   Evaluate    __import__('pathlib').Path('${DEMO_FILE}').resolve().as_uri()
    KW.SetValue    URL         ${FILE_URL}
    StartApp      web/WidgetsDemo

Teardown Widgets Demo
    StopHost

*** Test Cases ***
List And Selected Counts
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    # Combo options count (native select has 4 options)
    LST.VerifyListCount        Geschlecht       4
    # Radio group counts: Zahlungsmethode has 3; Lieferung has 5
    LST.VerifyListCount        Zahlungsmethode  3
    LST.VerifyListCount        Lieferung        5
    # Selected count: radios are initially 0; after selecting becomes 1
    LST.VerifySelectedCount    Zahlungsmethode  0
    KW.Select                  Zahlungsmethode  paypal
    LST.VerifySelectedCount    Zahlungsmethode  1
    Teardown Widgets Demo

