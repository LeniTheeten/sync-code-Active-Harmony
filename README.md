# sync-code-Active-Harmony
Dit is een project waarin een Arduino via MQTT communiceert met een Python-programma om een interactieve game-ervaring te creëren. Het spel combineert sensorgegevens van de Arduino met dynamische reacties in Python.

## Python code 
### MQTT
**MQTT verbinding opzetten**

**MQTT-berichten verzenden**

**MQTT-berichten ontvangen**

**wifi verbinding**
```sh
#IPv4 Address. . . . . . . . . . . : 192.168.0.198
import socket
#netwerkverbinding testen
def check_wifi():
    try:
        #verbinding maken met Google's DNS-server (8.8.8.8), omdat deze altijd online is (op poort 53)
        socket.create_connection(("8.8.8.8",53))
        print("Verbonden met de Wifi")
    #foutmelding wanneer het netwerk offline is
    except OSError:
        print("Er is geen Wifi verbinding gevonden")
    return False
Connectie_Wifi = check_wifi()
```

### muziek afspelen via computer

### sensorwaarden
**sensorwaarden verwerken**

**wachten op sensorwaarde verandering**

**Wachten tot alle sensoren uit zijn**

### LED aansturing

### Tegelreactie afhandeling

### Volgorde generator voor tegels

### Game logica

### Visual feedback

## Arduino code 

## Finale code
### Python

### Arduino
