*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    String
Library    Dialogs
Library    okw4robot.Web          driver=selenium    seleniumlib_name=SeleniumLibrary
Library    okw4robot.Keywords    backend=web    locators_path=${EXECDIR}/locators/web    section=LoginDialog

Suite Setup     Öffne Loginseite Im Browser
Suite Teardown  BuiltIn.No Operation


*** Keywords ***
Öffne Loginseite Im Browser
    ${path}=        Normalize Path    C:/temp/login.html
    ${path_fwd}=    Replace String    ${path}    \\    /
    ${url}=         Catenate    SEPARATOR=    file:///    ${path_fwd}

    # ChromeOptions-Objekt bauen (robust, ohne String-Parsing):
    ${opts}=    Evaluate    __import__('selenium.webdriver.chrome.options', fromlist=['Options']).Options()
    Call Method    ${opts}    add_argument    --allow-file-access-from-files
    Call Method    ${opts}    add_argument    --disable-web-security
    # optional: Browser nach Test offen lassen
    Call Method    ${opts}    add_experimental_option    detach    ${True}

    Open Browser    ${url}    chrome    options=${opts}
    Maximize Browser Window



*** Test Cases ***
Loge die Objektliste
    Zeige Objektliste
    Liste Abstrakte Elemente

Login OK
    Wähle Fenster     LoginDialog
    Gib Ein           Benutzer     admin
    Gib Ein           Passwort     geheim
    Klicke            OK
    Prüfe Wert Ist    Status       Status: Angemeldet

Login Abbruch
    Wähle Fenster     LoginDialog
    Klicke            Abbruch
    Prüfe Wert Ist    Status       Status: Abgebrochen
