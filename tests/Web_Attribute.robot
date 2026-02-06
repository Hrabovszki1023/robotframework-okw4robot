*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW
Library    okw4robot.keywords.attribute_keywords.AttributeKeywords    WITH NAME    ATTR
Library    okw4robot.keywords.params.ParamsKeywords             WITH NAME    PAR

*** Variables ***
${DEMO_FILE}    docs/examples/widgets_demo.html

*** Keywords ***
Setup Widgets Demo
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    ${FILE_URL}=   Evaluate    __import__('pathlib').Path('${DEMO_FILE}').resolve().as_uri()
    PAR.SetOKWParameter    TimeOutVerifyAttribute    10
    SetValue       URL         ${FILE_URL}
    StartApp      web/WidgetsDemo

Teardown Widgets Demo
    StopHost

*** Test Cases ***
Verify Placeholder Attributes
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    ATTR.VerifyAttribute       Name        placeholder    Nachname
    ATTR.VerifyAttributeWCM    Vorname     placeholder    *name*
    ATTR.VerifyAttributeREGX   Anmerkung   placeholder    ^Mehrzeilige\\s+Eingabe.*
    Teardown Widgets Demo

Verify And Memorize Data Attributes
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    ATTR.VerifyAttribute       OK          data-testid     btn-ok
    ATTR.MemorizeAttribute     OK          data-testid     OkDataTest
    ATTR.LogAttribute          OK          data-testid
    Teardown Widgets Demo


