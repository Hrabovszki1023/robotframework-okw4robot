*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.placeholder_keywords.PlaceholderKeywords    WITH NAME    PH
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW
Library    okw4robot.keywords.params.ParamsKeywords                        WITH NAME    PAR

*** Variables ***
${DEMO_FILE}    docs/examples/widgets_demo.html

*** Keywords ***
Setup Widgets Demo
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    ${FILE_URL}=   Evaluate    __import__('pathlib').Path('${DEMO_FILE}').resolve().as_uri()
    PAR.SetOKWParameter    TimeOutVerifyPlaceholder    10
    SetValue       URL         ${FILE_URL}
    StartApp      web/WidgetsDemo

Teardown Widgets Demo
    StopHost

*** Test Cases ***
Verify Placeholders
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    PH.VerifyPlaceholder        Name        Nachname
    PH.VerifyPlaceholderWCM     Vorname     *name*
    PH.VerifyPlaceholderREGX    Anmerkung   ^Mehrzeilige\\s+Eingabe.*
    Teardown Widgets Demo

