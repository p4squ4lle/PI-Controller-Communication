# PI-Controller-Communication

## Bewerkstelligung der Kommunikation zwischen Laser Desk und PI controller mittels virtuellem Null-Modem Kabel

Die serielle Verbindung zwischen der Scansoftware (Laserdesk) und dem Python-Programm wird durch einen Null-Modem Emulator bewerkstelligt. 
Die Software, die diese virtuellen COM ports zur Verfügung stellt, heißt com0com. Damit diese auf dem Steuerrechner einwandfrei funktioniert
musste der "secure boot" modus im UEFI (vormals BIOS) ausgeschaltet werden.