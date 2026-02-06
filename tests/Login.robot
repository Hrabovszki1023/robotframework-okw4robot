*** Settings ***
Library    SeleniumLibrary
Library    okw4robot.keywords.host.HostKeywords                 WITH NAME    Host
Library    okw4robot.keywords.app.AppKeywords                   WITH NAME    App
Library    okw4robot.keywords.widget_keywords.WidgetKeywords    WITH NAME    KW

# Suite Setup     Setup Login Test
# Suite Teardown  Close All Browsers

*** Variables ***
${LOGIN_HTML}   file:///C:/temp/login.html

*** Keywords ***
Setup Login Test
    StartHost     Chrome
    StartApp      Chrome 
    SelectWindow  Chrome
    SetValue       URL       ${LOGIN_HTML}
    # ClickOn        Maximize Window
    StartApp      web/TestAppOKW4Robot_WEB

*** Test Cases ***
Login OK
    Setup Login Test

    SelectWindow  LoginDialog
    SetValue       Benutzer     admin
    SetValue       Passwort     geheim
    ClickOn        OK
    VerifyValue    Status       Status: Angemeldet

    StopHost

Login Abbruch
    Setup Login Test

    SelectWindow  LoginDialog
    ClickOn        Abbruch
    VerifyValue    Status       Status: Abgebrochen

    StopHost

Widget Existenzprüfung
    Setup Login Test

    SelectWindow  LoginDialog
    VerifyExist    DoesNotExist    NO

    StopHost

Chrome Zu Firefox Umschalten
    StartHost     Chrome
    StartApp      Chrome
    SelectWindow  Chrome
    SetValue       URL    ${LOGIN_HTML}
    StopHost

    StartHost     Firefox
    StartApp      Firefox
    SelectWindow  Firefox
    SetValue       URL    ${LOGIN_HTML}
    StopHost

