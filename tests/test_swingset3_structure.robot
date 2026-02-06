*** Settings ***
Documentation     Exportiert die GUI-Struktur von SwingSet3 über den JavaRPC-Server
Library           Process
Library           OperatingSystem
Library           okw4robot.keywords.host.HostKeywords
Library           okw4robot.keywords.javaswing.ServerWaitKeywords
Library           okw4robot.keywords.javaswing.ObjectExportKeywords

# Suite Setup
# Suite Teardown

*** Variables ***
${OUTPUT_FILE}    ./reports/swing_structure.yaml

*** Test Cases ***
Export SwingSet3 GUI Structure
    [Documentation]    Fragt die Struktur vom Java-Fenster ab und speichert sie in YAML.
    StartHost    JavaRPC
    Wait Until JavaRPC Server Is Ready
    
    


