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
Cell By Headers
    Setup Table Demo
    SelectWindow   TableDemo
    # Row selected by key (WCM on first column), column by exact header name
    TBL.VerifyTableCellValueByHeaders    DemoTable    A2*     Col3    A23
    TBL.VerifyTableCellValueByHeaders    DemoTable    A2*     Col2    $EMPTY
    Teardown Table Demo

Row Content By Header
    Setup Table Demo
    SelectWindow   TableDemo
    # Select unique row via header/value, verify full row pattern
    TBL.VerifyTableRowContentByHeader    DemoTable    Col1    A31    A31$TABA32$TABA33
    Teardown Table Demo

Column Content By Header
    Setup Table Demo
    SelectWindow   TableDemo
    # Select column by exact header name, verify data rows
    TBL.VerifyTableColumnContentByHeader    DemoTable    Col2    A12$LF$EMPTY$LFA32
    Teardown Table Demo

