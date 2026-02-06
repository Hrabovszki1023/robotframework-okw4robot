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
Visible YES And NO
    Setup Widgets Demo
    SelectWindow   WidgetsDemo
    KW.VerifyIsVisible   Name        YES
    KW.ExecuteJS    document.querySelector('[data-testid="tf-vorname"]').style.display='none';
    KW.VerifyIsVisible   Vorname     NO
    Teardown Widgets Demo



