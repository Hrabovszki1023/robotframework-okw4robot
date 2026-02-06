*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.table_keywords.TableKeywords      WITH NAME    TBL
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW

*** Variables ***
${DEMO_FILE}    docs/examples/table_demo.html

*** Keywords ***
Setup Table Demo
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    ${FILE_URL}=   Evaluate    __import__('pathlib').Path('${DEMO_FILE}').resolve().as_uri()
    KW.SetValue    URL         ${FILE_URL}
    StartApp      web/TableDemo

Teardown Table Demo
    StopHost

*** Test Cases ***
Has Row With Empty Middle Cell
    Setup Table Demo
    SelectWindow   TableDemo
    TBL.VerifyTableHasRow    DemoTable    A21$TAB$EMPTY$TABA23
    Teardown Table Demo


