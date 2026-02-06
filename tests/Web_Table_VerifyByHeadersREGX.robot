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
Cell By Headers With REGX
    Setup Table Demo
    SelectWindow   TableDemo
    # Row selected by key (WCM on first column), column by exact header name, expected via regex
    TBL.VerifyTableCellValueByHeadersREGX    DemoTable    A3*     Col2    ^A3[0-9]$
    # Empty check via $EMPTY in REGX variant
    TBL.VerifyTableCellValueByHeadersREGX    DemoTable    A2*     Col2    $EMPTY
    Teardown Table Demo

Row Content By Header With REGX
    Setup Table Demo
    SelectWindow   TableDemo
    # Select unique row via header/value, verify per-cell regex patterns
    TBL.VerifyTableRowContentByHeaderREGX    DemoTable    Col1    A31    ^A31$$TAB^A3[0-9]$$TAB^A3[0-9]$
    Teardown Table Demo

Column Content By Header With REGX
    Setup Table Demo
    SelectWindow   TableDemo
    # Select column by exact header name, verify each row via regex
    TBL.VerifyTableColumnContentByHeaderREGX    DemoTable    Col3    ^A1[0-9]$$LF^A2[0-9]$$LF^A3[0-9]$
    Teardown Table Demo
