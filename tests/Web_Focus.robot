*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
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
Focus Switch Between Inputs
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    KW.SetFocus         Name
    KW.VerifyHasFocus   Name        YES
    KW.VerifyHasFocus   Vorname     NO
    KW.SetFocus         Vorname
    KW.VerifyHasFocus   Name        NO
    KW.VerifyHasFocus   Vorname     YES
    Teardown Widgets Demo

Focus Textarea And Button
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    KW.SetFocus         Anmerkung
    KW.VerifyHasFocus   Anmerkung   YES
    KW.SetFocus         OK
    KW.VerifyHasFocus   OK          YES
    KW.VerifyHasFocus   Anmerkung   NO
    Teardown Widgets Demo

Focus Checkbox And ComboBox
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    KW.SetFocus         Verheiratet
    KW.VerifyHasFocus   Verheiratet    YES
    KW.SetFocus         Geschlecht
    KW.VerifyHasFocus   Geschlecht  YES
    KW.VerifyHasFocus   Verheiratet    NO
    Teardown Widgets Demo

