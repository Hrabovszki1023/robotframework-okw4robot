*** Settings ***
Library    Process
Library    okw4robot.keywords.host.HostKeywords
Library    okw4robot.keywords.javaswing.ServerWaitKeywords
Library    okw4robot.keywords.javaswing.ObjectExportKeywords

Suite Setup     Starte RPC-Server Und SwingApp
Suite Teardown  Stoppe RPC-Server

*** Variables ***
${PORT}         5678
${JAR_PATH}     C:/tools/SwingSet3.jar
${ZIELDATEI}    objektliste.yaml

*** Test Cases ***
Objektliste Exportieren
    StartHost    JavaRPC
    Warte Bis JavaRPC-Server Bereit Ist
    Exportiere Objektstruktur    ${ZIELDATEI}


*** Keywords ***
Starte RPC-Server Und SwingApp
    [Documentation]    Startet den JavaRPC-Server mit eingebetteter SwingApp
    Start Process    java
    ...            -jar
    ...            ../JavaRPCServer/target/java-rpc-server-1.0-SNAPSHOT-jar-with-dependencies.jar
    ...            ${PORT}
    ...            ${JAR_PATH}
    ...    shell=True
    ...    stdout=NONE
    ...    stderr=NONE
    Sleep    5s

Stoppe RPC-Server
    [Documentation]    Beendet den JavaRPC-Server
    Terminate All Processes

