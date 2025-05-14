s# Sync-code-Active-Harmony
Dit is een project waarin een Arduino via MQTT communiceert met een Python-programma om een interactieve game-ervaring te creëren. Het spel combineert sensorgegevens van de Arduino met dynamische reacties in Python.
## Bedradingsschema

![image](https://github.com/user-attachments/assets/c74f1546-adf7-493d-be09-2f69e09eebeb)

## Opbouw code

![image](https://github.com/user-attachments/assets/2dd6514c-5238-438a-bd58-2b1b113cb6a6)

![image](https://github.com/user-attachments/assets/5406a8c8-d2e3-4931-b803-4dd1392d2d9e)

![image](https://github.com/user-attachments/assets/0045f85e-fc03-4792-a662-4b6f8f9e1e95)

## Python code 
### MQTT
**MQTT verbinding opzetten**

```sh
print("file")
import paho.mqtt.client as mqtt
#mqtt op een bepaalde broker instellen
#later zal de broker de rasberri zelf zijn
BROKER_URL = "mqtt.eclipseprojects.io"
BROKER_PORT = 1883
KEEP_ALIVE = 60

def connect_mqtt(client,userdata,flags,rc):
    if rc == 0:
        print("geconnecteerd")
    else:
        print("Failed")

client = mqtt.Client()
client.on_connect = connect_mqtt
client.connect(BROKER_URL,BROKER_PORT,KEEP_ALIVE)
#client.loop_start()
print("voor")

client.loop_forever()
print("achter")
```

**MQTT-berichten ontvangen**
```sh
import json
#payload omzetten naar iets leesbaar

BROKER_URL = "mqtt.eclipseprojects.io"
BROKER_PORT = 1883
KEEP_ALIVE = 60

# Callback functie voor connectie
def connect_mqtt(client, userdata, flags, rc):
    if rc == 0:
        print("Geconnecteerd")
        client.subscribe("test/74:C7:7A:1B:5A:E0:/waarde")  # Abonneer je direct na het verbinden
    else:
        print("Verbinden mislukt")

# Callback functie voor ontvangen berichten
def on_mqtt_message(client, userdata, message):
   
    global tegel_sensor_waardes
    
    if message is None:
        return
    
    #print(f"Bericht ontvangen {message.topic}")

    parts = message.topic.split("/")
    if len(parts)<3:
        print(f"Ongeldig ontvangen: {message.topic}")
        return
    
    mac = parts[1]
    try:
        sensor_int = int(parts[2])
        tegel_sensor_waardes[mac] = sensor_int  # Sla de sensorwaarde op in de dictionary
    except ValueError:
        print(f"Fout bij het omzetten van sensorwaarde naar int: {parts[2]}")

# MQTT client instellen
client = mqtt.Client()
client.on_connect = connect_mqtt
client.on_message = on_message

# Verbinden met de broker
client.connect(BROKER_URL, BROKER_PORT, KEEP_ALIVE)

# Start de loop om berichten te ontvangen
print("Listening...")
client.loop_forever()  # Dit houdt het script draaiende
```

**MQTT-berichten verzenden**
```sh
import paho.mqtt.client as mqtt
#mqtt op een bepaalde broker instellen
#later zal de broker de rasberri zelf zijn
exit()
BROKER_URL = "mqtt.eclipseprojects.io"
BROKER_PORT = 1883
KEEP_ALIVE = 60

def connect_mqtt(client,userdata,flags,rc):
    if rc == 0:
        print("geconnecteerd")
    else:
        print("Failed")

client = mqtt.Client()
client.on_connect = connect_mqtt
client.connect(BROKER_URL,BROKER_PORT,KEEP_ALIVE)
#client.loop_start()
client.loop_forever()

while True:
    bericht = input("Typ 'on' om de LED aan te zetten of 'off' om ze uit te zetten: ").strip().lower()
    #als de imput upper cases of spaties bevat wordt dit weg gedaan
    if bericht == "on":
        client.publish(TOPIC, "LED ON")
        print("Bericht verzonden: LED ON")

    elif bericht == "off":
        client.publish(TOPIC, "LED OFF")
        print("Bericht verzonden: LED OFF")

    else:
        print("ongeldige invoer")
```

**Wifi verbinding**
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

### Muziek afspelen via computer

```sh
import pygame
pygame.mixer.init()

voorbeeld_volgorde = [1,2,3,4,5,6]

muziek_dictionary = {
    1: "BeatIt1.mp3",
    2: "BeatIt2.mp3",
    3: "BeatIt3.mp3",
    4: "BeatIt4.mp3",
    5: "BeatIt5.mp3",
    6: "BeatIt6.mp3"
}
def speel_muziek(muziek_bestand):
    pygame.mixer.music.load(muziek_bestand)
    pygame.mixer.music.play()

for plaats in voorbeeld_volgorde:
    muziek_bestand = muziek_dictionary [plaats]
    print(f"Speel muziek {muziek_bestand} voor plaats {plaats}")
    speel_muziek(muziek_bestand)

print("alle muziekjes zijn gespeeld")
```

### Sensorwaarden
**Sensorwaarden verwerken**

```sh
def on_mqtt_message(client, userdata, message):
   
    global tegel_sensor_waardes
    
    if message is None:
        return
    
    #print(f"Bericht ontvangen {message.topic}")

    parts = message.topic.split("/")
    if len(parts)<3:
        print(f"Ongeldig ontvangen: {message.topic}")
        return
    
    mac = parts[1]
    try:
        sensor_int = int(parts[2])
        tegel_sensor_waardes[mac] = sensor_int  # Sla de sensorwaarde op in de dictionary
    except ValueError:
        print(f"Fout bij het omzetten van sensorwaarde naar int: {parts[2]}")
```

**wachten op sensorwaarde verandering**

```sh
def wacht_op_tegel_veranderd(timeout, min_veranderings_waarde) -> tuple:
    """
    Deze code wacht op tegel verandering
    """
    vorige_toestand = dict(tegel_sensor_waardes)  # Maak een kopie van de huidige toestand

    while True:
        # Bereken van alle tegels hoe veel ze veranderd zijn
        tegels_met_hun_veranderings_waarde = dict()

        for mac, sensor_waarde in tegel_sensor_waardes.items():
            if mac in vorige_toestand and sensor_waarde != vorige_toestand[mac]:
                verschil = abs(sensor_waarde - vorige_toestand[mac])
                tegels_met_hun_veranderings_waarde[mac] = verschil

        # Vind de tegel en de grootste verandering
        if tegels_met_hun_veranderings_waarde:
            mac = max(tegels_met_hun_veranderings_waarde, key=tegels_met_hun_veranderings_waarde.get)
            waarde = tegels_met_hun_veranderings_waarde[mac]
            if waarde > min_veranderings_waarde:
                print(f"Sensor {mac} heeft een verandering van {waarde}")
                return mac, tegel_sensor_waardes[mac]
            time.sleep(timeout)
```
            
**Wachten tot alle sensoren uit zijn**

```sh
def krijg_sensors_die_aanliggen() -> list:
    """
    Verkrijg een lijst van sensoren die aan staan
    """
    sensors_die_aanliggen = []
    for mac, sensor_waarde in tegel_sensor_waardes.items():
        if sensor_waarde < SENSOR_TRESHOLD:
            sensors_die_aanliggen.append(mac)
    return sensors_die_aanliggen

def wacht_op_alles_uit():
    """
    Blijf wachten tot alle sensoren zijn uitgeschakeld
    Ondertussen worden de sensoren die aan staan rood gekleurd
    """
    sensors_aan = krijg_sensors_die_aanliggen()
    while sensors_aan:
        print(f"Wachten tot alles uit is. Deze sensoren loggen nog aan: {sensors_aan}")
        stuur_tijdelijk_fout(sensors_aan)
        time.sleep(1)
        sensors_aan = krijg_sensors_die_aanliggen()
```

### LED aansturing
# region Alles rond aansturen van LEDs

```sh
def stuur_lichtcommando(topic) -> None:
    #print(f"MQTT-bericht verzonden: {topic}")
    client.publish(topic, "1")

def stuur_leds(rood, groen, blauw, leds: list) -> None:
    #print(f"Stuur R:{rood}, G:{groen}, B: {blauw} naar leds {leds}")
    for mac in leds:
        stuur_lichtcommando(f"ActiveHarmony/{mac}/{rood}/{groen}/{blauw}")

def stuur_tijdelijk_leds(rood, groen, blauw, leds: list, duur: int) -> None:
    stuur_leds(rood, groen, blauw, leds)
    time.sleep(duur)
    stuur_leds(0, 0, 0, leds)

def knipper_leds(rood, groen, blauw, leds: list, aantal_keer: int, duur: int) -> None:
    for i in range(aantal_keer):
        stuur_tijdelijk_leds(rood, groen, blauw, leds, duur)

def stuur_tijdelijk_fout(leds: list):
    stuur_tijdelijk_leds(255, 0, 0, leds, 1)

def stuur_tijdelijk_wit(leds: list):
    stuur_tijdelijk_leds(255, 255, 255, leds, 1)

def stuur_wit(leds: list):
    stuur_leds(255, 255, 255, leds)

def stuur_groen(leds: list):
    stuur_leds(0, 255, 0, leds)
```

### Tegelreactie afhandeling

```sh
def do_reactie (mac, value, referentie, stap, al_correct) -> bool:
    """
    Speelt de reactie af op de tegel die is veranderd
    Geeft True of False terug afhankelijk of het correct was of niet
    """
    # Controleer of het MAC-adres in de arduino_dict zit
    if mac not in arduino_dict:
        print(f"Ongeldig MAC-adres: {mac}")
        return False, False

    # Sensor uit? Foutieve tegel
    if value > SENSOR_TRESHOLD:
        stuur_tijdelijk_fout([mac])
        return False
    
    if is_sensor_correct(mac, referentie,stap):
        # Nieuw correcte tegel op groen zetten
        stuur_groen([mac])
        # Vorige correcte tegels op wit zetten
        stuur_wit(list(al_correct))
        # Speel muziek af
        speel_muziek(stap)
        return True
    else:
        # Foutive tegel 1x op rood laten knipperen
        stuur_tijdelijk_fout([mac])
        # Stuur juiste volgorde licht
        toon_juiste_volgorde(referentie)
        return False

def speel_het_spel(referentie):
    # Speel de juiste volgorde van de tegels af
    toon_juiste_volgorde(referentie)
    
    stap = 0

    al_correct = set()  # Houd bij welke tegels correct zijn gespeeld

    while stap < len(referentie):
        # Wacht tot een van de tegels is veranderd
        mac, value = wacht_op_tegel_veranderd(0.5, SENSOR_TRESHOLD)

        # Reageer op de veranderde tegel
        correct = do_reactie(mac, value, referentie, stap, al_correct)
        print(f"Stap {stap} correct!")
        if correct:
            stap += 1
            al_correct.add(mac)  # Voeg correcte tegel toe aan de set
            print(f"Reeds correcte tegels: {len(al_correct)}")
        else:
            stap = 0
            al_correct.clear()
            print("Fout! Terug naar stap 0")

    print("Je hebt het spel perfect gespeeld")
    knipper_leds(0, 255, 0, list(al_correct), 5, 1)
```

### Volgorde generator voor tegels

```sh
import random

def genereer_volgorde_tegels():
    random_referentie = ""
    for cijfer in range (6):
        random_cijfer = random.randint(1,6)
        random_referentie += str (random_cijfer)
    referentie_lijst = list (random_referentie)
    return (referentie_lijst)
#random volgorde van tegels genereren

def genereer_arduino_dictionary():
    dict_arduino = {}
    for aantal in range (len(referentie)):
        hoeveelste_arduino = "arduino" + str(aantal+1)
        waarde = False
        dict_arduino [hoeveelste_arduino] = waarde
    return (dict_arduino)
#dictionary aantal arduino's

referentie = genereer_volgorde_tegels()
print (referentie)
dictionary = genereer_arduino_dictionary()
print (dictionary)


stapvolgorde = []
gemaakte_fout = False
stap = 0
while gemaakte_fout == False and stap < len(referentie):
    plaats = int(input("op welke tegel zal je staan?: "))
    if referentie[stap] == str(plaats):
        dictionary["arduino" + str(stap+1)] = True
        stapvolgorde.append(str(plaats))
        stap += 1
    else:
        gemaakte_fout = True
        print("je stapt op de verkeerde tegel")
        print(referentie)
```
### Visual feedback

```sh
def verwerk_string(text):
    rood = 255
    groen = 0
    blauw = 0
    
    delen = text.split("/")
    if len(delen) != 3:
        return "ongeldige invoer"
    
    mac_adres = delen[1]
    waarde = int(delen[2])

    if waarde <= 30:
        arduino = f"Arduino: {mac_adres}"
        rgb_kleur = f"{rood},{groen},{blauw}"
        #de bijhorende arduino + mac adres uit de dictionary worden gehaald
        return f"{arduino}/{rgb_kleur}"
    else:
        return False
    
invoer = "tekst/22:34:4A:69/40"
print(verwerk_string(invoer))
```

### Game logica
import os
import random
import time

import paho.mqtt.client as mqtt
import pygame

MQTT_BROKER_URL = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE = 60

SENSOR_TRESHOLD = 600  # Waarde onder (!) deze waarde is sensor aan

received_message = None
is_muziek_bezig = False

# Dictionary met muziekbestanden, gebaseerd op de huidige foldernaam
audio_folder = os.path.join(os.path.dirname(__file__), "audio")
muziek_dictionary = {
    0: os.path.join(audio_folder, "BeatIt1.mp3"),
    1: os.path.join(audio_folder, "BeatIt2.mp3"),
    2: os.path.join(audio_folder, "BeatIt3.mp3"),
    3: os.path.join(audio_folder, "BeatIt4.mp3"),
    4: os.path.join(audio_folder, "BeatIt5.mp3"),
}

# Dictionary met MAC-adressen en bijbehorende namen
arduino_dict = {
    '18:1F:3B:BD:9E:7C': 'mac1', 
    '20:88:4E:DA:D4:D4': 'mac2', 
    '74:C7:7A:1B:5A:E0': 'mac3', 
    '1C:31:7B:1B:5A:E0': 'mac4', 
    '4C:F1:77:1B:5A:E0': 'mac5'
}

# Hou globaal de sensorwaarden bij, per Arduino
# Initialiseer ze allemaal op -1
tegel_sensor_waardes = dict()
for mac in arduino_dict.keys():
    tegel_sensor_waardes[mac] = -1


def genereer_volgorde_tegels() -> list:
    """
    Functie die de volgorde van de tegels genereert, afhankelijk van het aantal ingevoerde Arduino's.
    """
    volgorde = list(arduino_dict.values())  # Maak een lijst van tegels afhankelijk van het aantal Arduino's
    random.shuffle(volgorde)  # Willekeurig schudden van de volgorde
    print(f"Volgorde van tegels: {volgorde}")
    return volgorde


def speel_muziek(muziek_index) -> None:
    """
    Functie die muziek afspeelt op basis van de index in de muziek_dictionary.
    """
    global is_muziek_bezig
    is_muziek_bezig = True #blokkeer berichtverwerking
    print(f"Speel {muziek_dictionary[muziek_index]}")
    pygame.mixer.music.load(muziek_dictionary[muziek_index])
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    is_muziek_bezig = False

def connect_mqtt(client, userdata, flags, rc):
    if rc == 0:
        print("Geconnecteerd")
        topic = f"ActiveHarmony/+/+"
        client.subscribe(topic)  # Abonneer je direct na het verbinden
        print(f"Geabonneerd op topic: {topic}")
    else:
        print("Verbinden mislukt")

# Callback functie voor ontvangen berichten
def on_mqtt_message(client, userdata, message):
    """
    Deze functie wordt aangeroepen wanneer er een bericht wordt ontvangen op een geabonneerd topic.
    Het bericht wordt verwerkt en de sensorwaarde wordt opgeslagen in de tegel_sensor_waardes dictionary.
    Bvb:
    Bericht ontvangen ActiveHarmony/18:1F:3B:BD:9E:7C:/909
    Bericht ontvangen ActiveHarmony/20:88:4E:DA:D4:D4:/886
    Bericht ontvangen ActiveHarmony/74:C7:7A:1B:5A:E0:/975
    Bericht ontvangen ActiveHarmony/1C:31:7B:1B:5A:E0:/8
    Bericht ontvangen ActiveHarmony/4C:F1:77:1B:5A:E0:/946
    """
    global tegel_sensor_waardes
    
    if message is None:
        return
    
    #print(f"Bericht ontvangen {message.topic}")

    parts = message.topic.split("/")
    if len(parts)<3:
        print(f"Ongeldig ontvangen: {message.topic}")
        return
    
    mac = parts[1]
    try:
        sensor_int = int(parts[2])
        tegel_sensor_waardes[mac] = sensor_int  # Sla de sensorwaarde op in de dictionary
    except ValueError:
        print(f"Fout bij het omzetten van sensorwaarde naar int: {parts[2]}")

def wacht_op_tegel_veranderd(timeout, min_veranderings_waarde) -> tuple:
    """
    Deze code wacht op tegel verandering
    """
    vorige_toestand = dict(tegel_sensor_waardes)  # Maak een kopie van de huidige toestand

    while True:
        # Bereken van alle tegels hoe veel ze veranderd zijn
        tegels_met_hun_veranderings_waarde = dict()

        for mac, sensor_waarde in tegel_sensor_waardes.items():
            if mac in vorige_toestand and sensor_waarde != vorige_toestand[mac]:
                verschil = abs(sensor_waarde - vorige_toestand[mac])
                tegels_met_hun_veranderings_waarde[mac] = verschil

        # Vind de tegel en de grootste verandering
        if tegels_met_hun_veranderings_waarde:
            mac = max(tegels_met_hun_veranderings_waarde, key=tegels_met_hun_veranderings_waarde.get)
            waarde = tegels_met_hun_veranderings_waarde[mac]
            if waarde > min_veranderings_waarde:
                print(f"Sensor {mac} heeft een verandering van {waarde}")
                return mac, tegel_sensor_waardes[mac]
            time.sleep(timeout)




# region Alles rond aansturen van LEDs
def stuur_lichtcommando(topic) -> None:
    #print(f"MQTT-bericht verzonden: {topic}")
    client.publish(topic, "1")

def stuur_leds(rood, groen, blauw, leds: list) -> None:
    #print(f"Stuur R:{rood}, G:{groen}, B: {blauw} naar leds {leds}")
    for mac in leds:
        stuur_lichtcommando(f"ActiveHarmony/{mac}/{rood}/{groen}/{blauw}")

def stuur_tijdelijk_leds(rood, groen, blauw, leds: list, duur: int) -> None:
    stuur_leds(rood, groen, blauw, leds)
    time.sleep(duur)
    stuur_leds(0, 0, 0, leds)

def knipper_leds(rood, groen, blauw, leds: list, aantal_keer: int, duur: int) -> None:
    for i in range(aantal_keer):
        stuur_tijdelijk_leds(rood, groen, blauw, leds, duur)

def stuur_tijdelijk_fout(leds: list):
    stuur_tijdelijk_leds(255, 0, 0, leds, 1)

def stuur_tijdelijk_wit(leds: list):
    stuur_tijdelijk_leds(255, 255, 255, leds, 1)

def stuur_wit(leds: list):
    stuur_leds(255, 255, 255, leds)

def stuur_groen(leds: list):
    stuur_leds(0, 255, 0, leds)
# endregion






def krijg_sensors_die_aanliggen() -> list:
    """
    Verkrijg een lijst van sensoren die aan staan
    """
    sensors_die_aanliggen = []
    for mac, sensor_waarde in tegel_sensor_waardes.items():
        if sensor_waarde < SENSOR_TRESHOLD:
            sensors_die_aanliggen.append(mac)
    return sensors_die_aanliggen

def wacht_op_alles_uit():
    """
    Blijf wachten tot alle sensoren zijn uitgeschakeld
    Ondertussen worden de sensoren die aan staan rood gekleurd
    """
    sensors_aan = krijg_sensors_die_aanliggen()
    while sensors_aan:
        print(f"Wachten tot alles uit is. Deze sensoren loggen nog aan: {sensors_aan}")
        stuur_tijdelijk_fout(sensors_aan)
        time.sleep(1)
        sensors_aan = krijg_sensors_die_aanliggen()

def toon_juiste_volgorde(referentie):
    """
    Toon de juiste volgorde van de tegels met wit licht
    """
    for mac_naam in referentie:
        for mac_adres, naam in arduino_dict.items():
            if naam == mac_naam:
                stuur_tijdelijk_wit([mac_adres])

def opstart_spel():
    # Wacht tot alle sensoren zijn uitgeschakeld
    # De sensoren die aanstaan, worden rood gekleurd
    wacht_op_alles_uit()

    print("Alle sensoren zijn uit")

    # Toon dat we klaar zijn om te beginnen
    # door naar alle tegels wit licht te sturen
    stuur_tijdelijk_wit(list(arduino_dict.keys()))
    time.sleep(1)

    print("Wit op alle tegels afgespeeld, we kunnen beginnen")

def is_sensor_correct (mac, referentie, stap) -> bool:
    """
    Checkt of de sensor voor die stap correct is
    """
    mac_naam = referentie[stap]
    for amac, naam in arduino_dict.items():
        if naam == mac_naam and amac == mac:
            return True
    return False

def do_reactie (mac, value, referentie, stap, al_correct) -> bool:
    """
    Speelt de reactie af op de tegel die is veranderd
    Geeft True of False terug afhankelijk of het correct was of niet
    """
    # Controleer of het MAC-adres in de arduino_dict zit
    if mac not in arduino_dict:
        print(f"Ongeldig MAC-adres: {mac}")
        return False, False

    # Sensor uit? Foutieve tegel
    if value > SENSOR_TRESHOLD:
        stuur_tijdelijk_fout([mac])
        return False
    
    if is_sensor_correct(mac, referentie,stap):
        # Nieuw correcte tegel op groen zetten
        stuur_groen([mac])
        # Vorige correcte tegels op wit zetten
        stuur_wit(list(al_correct))
        # Speel muziek af
        speel_muziek(stap)
        return True
    else:
        # Foutive tegel 1x op rood laten knipperen
        stuur_tijdelijk_fout([mac])
        # Stuur juiste volgorde licht
        toon_juiste_volgorde(referentie)
        return False

def speel_het_spel(referentie):
    # Speel de juiste volgorde van de tegels af
    toon_juiste_volgorde(referentie)
    
    stap = 0

    al_correct = set()  # Houd bij welke tegels correct zijn gespeeld

    while stap < len(referentie):
        # Wacht tot een van de tegels is veranderd
        mac, value = wacht_op_tegel_veranderd(0.5, SENSOR_TRESHOLD)

        # Reageer op de veranderde tegel
        correct = do_reactie(mac, value, referentie, stap, al_correct)
        print(f"Stap {stap} correct!")
        if correct:
            stap += 1
            al_correct.add(mac)  # Voeg correcte tegel toe aan de set
            print(f"Reeds correcte tegels: {len(al_correct)}")
        else:
            stap = 0
            al_correct.clear()
            print("Fout! Terug naar stap 0")

    print("Je hebt het spel perfect gespeeld")
    knipper_leds(0, 255, 0, list(al_correct), 5, 1)



if __name__ == "__main__":
    # Initialiseer de pygame mixer voor audio
    pygame.mixer.init()

    # Maak een MQTT-client aan en verbind enkele functies
    client = mqtt.Client()
    client.loop_start()
    client.on_connect = connect_mqtt
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE)

    # Bedenk de puzzel die moet worden opgelost
    referentie = genereer_volgorde_tegels()
    
    # Toon dat we kunnen starten (of wacht tot alle tegels uit zijn)
    opstart_spel()    

    # Speel het spel tot volledig gespeeld
    volledig_gespeeld = False

    while not volledig_gespeeld:
        volledig_gespeeld = speel_het_spel(referentie)



## Arduino code 

### Wifi

```sh
#include <WiFiNINA.h>

WiFiClient wifiClient;

const char* ssid = "A35 van Leni";
const char* password = "HotspotLeni";

void setup() {
  Serial.begin(9600);

  Serial.print("Verbinden met WiFi... ");
  if (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden!");
  Serial.print("IP-adres: ");
  Serial.println(WiFi.localIP());
}
```

### MQTT

```sh
MqttClient mqttClient(wifiClient);

const char* mqtt_server = "mqtt.eclipseprojects.io";
const int mqtt_port = 1883;

String payload;

void setup() {
  Serial.begin(9600);

  Serial.print("Verbinden met MQTT-broker... ");
  if (!mqttClient.connect(mqtt_server, mqtt_port)) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden met MQTT!");

  mqttClient.onMessage(onMqttMessage);
}
```

### MAC-adres

```sh
String getMacAdress(){
  char macStr[18];
  
  byte mac[6];
  WiFi.macAddress(mac);

  //Serial.print("MAC Address: ");
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X" , mac[0],mac[1], mac[2], mac[3],mac[4], mac[5]);
  return String(macStr);
}
```

### Topic

**_Maken_**

```sh
String maakTopic(){
  String mac = getMacAdress();
  String topic = "ActiveHarmony/" + mac + "/+/+/+" ;
  return topic;
}
```

**_Verzenden_**

```sh
void loop() {

  char lichtwaardeStr[10]; 
  sprintf(lichtwaardeStr, "%d", lichtwaarde);

  const char* macStr = getMacAdress().c_str();

  char topic[50] = "ActiveHarmony/" ;
  strcat(topic, macStr) ;
  strcat(topic, "/");
  strcat(topic, lichtwaardeStr); 
  mqttClient.beginMessage(topic);
  mqttClient.print("Hallo vanaf Arduino Nano 33 IoT!");
  mqttClient.endMessage();

  Serial.println("MQTT bericht verzonden!");
  Serial.println(topic);

  delay(100);  // Wacht 5 seconden voordat een nieuw bericht wordt verzonden

  mqttClient.poll();
}
```

**_Subscribing_**

```sh
void setup() {
  Serial.begin(9600);

  Serial.print("Subscribing to topic: ");
  String topic = maakTopic();
  Serial.println(topic);
  mqttClient.subscribe(topic);
}
```

**_Ontvangen_**

```sh
// Callback functie die wordt aangeroepen wanneer een bericht wordt ontvangen
void onMqttMessage(int messageSize) {
  // print out the topic and some message details
  Serial.println("Received a message: ");
  String topic = mqttClient.messageTopic();
  Serial.println(topic);
  Serial.print(mqttClient.messageTopic());

  // read the incoming data and store it into the payload variable
  String payloadString = "";
  for (int i = 0; i < messageSize; i++) {
    payloadString += (char)mqttClient.read();
  }
  payload = payloadString;
  Serial.println(payload);
  zetlicht(topic);
}
```

**_Opsplitsen_**

```sh
void split(String data, char delimiter, String result[], int maxParts) {
    int start = 0;
    int end = 0;
    int index = 0;
    
    while ((end = data.indexOf(delimiter, start)) != -1 && index < maxParts - 1) {
        result[index++] = data.substring(start, end);
        start = end + 1;
    }
    
    result[index] = data.substring(start);
}
```

### LED

```sh
int roodPin= 9;
int groenPin = 11;
int blauwPin = 10;

void setColor(int redValue, int greenValue,  int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin,  greenValue);
  analogWrite(blauwPin, blueValue);
}

void setup() {
  Serial.begin(9600);
  pinMode(roodPin,  OUTPUT);              
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);
}

void zetlicht(String input){
  Serial.println("zetlicht");
  Serial.println(input);
  
  String result[5];
  split(input, '/', result, 5);
  
  if (input.startsWith("ActiveHarmony/")) {
    String mac = result[1];
    String rood = result[2];
    String groen = result[3];
    String blauw = result[4];// MAC-adres is de eerste waarde
    Serial.println(mac);
    Serial.println(rood);
    Serial.println(groen);
    Serial.println(blauw);

  // Vergelijk MAC-adres met macStr
    setColor(rood.toInt(), groen.toInt(), blauw.toInt());
    delay(2000);
    Serial.println("kleurwaarde");
    Serial.println(rood.toInt());
    Serial.println(groen.toInt());
    Serial.println(blauw.toInt());
  }
}
```

### Sensor

```sh
const int sensorPin = A0;

void loop() {  

  int lichtwaarde = analogRead(A0);  // Lees de analoge waarde van de lichtsensor
    Serial.print("Lichtwaarde: ");
    Serial.println(lichtwaarde);  // Toon de waarde in de seriële monitor
    delay(500);
}
```

## Finale code
### Python

**Simulate sensor**

Dit werd ontwikkeld omdat de Arduino Nano 33 IoT's niet altijd allemaal beschikbaar waren. De Simulate Sensor krijgt een kleur als output en geeft vervolgens een waarde van 100 of 1000, waarmee de sensorwaarden van de Arduino's worden gesimuleerd.
De sensor maakt gebruik van dezelfde MQTT-server als de rest van de code, waarop ook de Arduino's verbonden zijn.

```sh
import curses
import json
import sys
import time

import paho.mqtt.client as mqtt

from config import MQTT_BROKER_PORT, MQTT_BROKER_URL, MQTT_KEEP_ALIVE

MAX_MESSAGES_ON_SCREEN = 4
SENSOR_VALUE_ON = 100
SENSOR_VALUE_OFF = 1000

mac_address: str = ""  # We'll fill this with an existing MAC address to simulate a device
received_messages: list = list()  # We'll keep the top N received messages and log to screen
sent_messages: list = list()  # We'll keep the top N sent messages and log to screen
topic_subscriptions: set = set()  # We'll keep track of the topics we're subscribed to
sensor_status: bool = False  # Is the sensor on or off?
led_status: bool = False  # Is the LED on or off?
color: dict = {"red": 0, "green": 0, "blue": 0}  # The color of the LED (background of the screen)

mac_addresses = [
    "18:1F:3B:BD:9E:7C", 
    "20:88:4E:DA:D4:D4", 
    "74:C7:7A:1B:5A:E0", 
    "1C:31:7B:1B:5A:E0", 
    "4C:F1:77:1B:5A:E0"
]

def get_mac_address(index: int) -> str:
    """
    Get an existing mac address from the list, by index
    :param index: The index of the mac address to get
    :return: The mac address as a string
    """
    return mac_addresses[index]


def update_screen(stdscr) -> None:
    """
    Just for simulation purposes
    Use the terminal background color to simulate an RGB LED
    We only support these 8 colors (black if "off"):
    - 255/255/255 = white
    - 255/0/0 = red
    - 0/255/0 = green
    - 0/0/255 = blue
    - 255/255/0 = yellow
    - 255/0/255 = magenta
    - 0/255/255 = cyan
    - 0/0/0 = black

    Also write some extra info like mac address, sensor status and the last N messages
    :param stdscr: The standard screen object from curses
    """
    if led_status:
        if color.get("red", 0) and color.get("green", 0) and color.get("blue", 0):
            led_color = curses.COLOR_WHITE
        elif color.get("red", 0) and color.get("green", 0):
            led_color = curses.COLOR_YELLOW
        elif color.get("red", 0) and color.get("blue", 0):
            led_color = curses.COLOR_MAGENTA
        elif color.get("green", 0) and color.get("blue", 0):
            led_color = curses.COLOR_CYAN
        elif color.get("red", 0):
            led_color = curses.COLOR_RED
        elif color.get("green", 0):
            led_color = curses.COLOR_GREEN
        elif color.get("blue", 0):
            led_color = curses.COLOR_BLUE
        else:
            led_color = curses.COLOR_BLACK
    else:
        led_color = curses.COLOR_BLACK

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, led_color)
    stdscr.bkgd(' ', curses.color_pair(1))

    # Just for simulation purposes, 
    # write the status of the sensor to the screen
    stdscr.clear()  # clear the screen before writing new text

    left = 2


    text = "Sensor = ON" if sensor_status else "Sensor = OFF"
    stdscr.addstr(3, left, text, curses.color_pair(1))

    text = f"MAC Address: {mac_address}"
    stdscr.addstr(5, left, text, curses.color_pair(1))
    
    for i, topic in enumerate(topic_subscriptions):
        top = 6 + i
        stdscr.addstr(top, left, f"Subscribed to: {topic}", curses.color_pair(1))

    stdscr.addstr(8, left, f"Last {MAX_MESSAGES_ON_SCREEN} messages received:", curses.color_pair(1))

    for i, message in enumerate(received_messages):
        top = 9 + i
        stdscr.addstr(top, left, f"{message.topic}", curses.color_pair(1))

    stdscr.addstr(13 + MAX_MESSAGES_ON_SCREEN, left, f"Last {MAX_MESSAGES_ON_SCREEN} messages sent:", curses.color_pair(1))

    for i, topic in enumerate(sent_messages):
        top = 14 + MAX_MESSAGES_ON_SCREEN + i
        stdscr.addstr(top, left, topic, curses.color_pair(1))

    stdscr.refresh()


def publish_sensor_status(mqtt_client) -> None:
    """
    Sends its sensor status to the MQTT broker via a JSON payload
    :param mqtt_client: The MQTT client instance to use for publishing
    """
    # Instead of sending boolean true / false, 
    # we send an integer value in the topic
    sensor_int_value = SENSOR_VALUE_ON if sensor_status else SENSOR_VALUE_OFF
    topic = f"ActiveHarmony/{mac_address}/{sensor_int_value}"
    payload = {
        # We don't use a payload, since everything is in the topics
    }
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

    # Write the last N sent messages on the screen
    if len(sent_messages) >= MAX_MESSAGES_ON_SCREEN:
        sent_messages.pop()
    sent_messages.insert(0, topic)

def announce_device(mqtt_client) -> None:
    """
    Sends an announcement message to the MQTT broker
    :param mqtt_client: The MQTT client instance to use for publishing
    """
    topic = f"ActiveHarmony/{mac_address}/announce"
    payload = {
        # We don't use a payload, since everything is in the topics
    }
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

def on_sensor_message_received(mqtt_client, userdata, message, topic):
    """
    Every time we receive a message that controls the LED, 
    we update the color and status
    """
    global color
    global led_status
    global message_on_screen
    
    # Adapt the global color dict variable with the received color
    # The topic is in the format: ActiveHarmony/{mac_address}/{red}/{green}/{blue}
    topic_parts = topic.split("/")
    color["red"] = int(topic_parts[-3])
    color["green"] = int(topic_parts[-2])
    color["blue"] = int(topic_parts[-1])

    led_status = False if topic.endswith("/0/0/0") else True

    message_on_screen = f"on_sensor_message_received: {topic}"

    stdscr = userdata
    update_screen(stdscr)

def on_mqtt_message(mqtt_client, userdata, message):
    """
    Receives messages from the MQTT broker and prints them to the console
    """
    # While we're simulating, just show the last N messages on screen
    received_messages.insert(0, message)
    if len(received_messages) > MAX_MESSAGES_ON_SCREEN:
        received_messages.pop()
    
    on_sensor_message_received(mqtt_client, userdata, message, message.topic)


if __name__ == "__main__":
    # Read parameter from command line to know which device tp simulate
    # We can run the script with a parameter to simulate different devices
    # e.g. `python simulate_button.py 0` or `python simulate_button.py 1`
    # If no parameter is given, we use the first device
    mac_address_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    mac_address = get_mac_address(mac_address_index)

    client = mqtt.Client()
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE)

    # Listen to incoming messages that control the LED
    client.on_message = on_mqtt_message

    # Subscribe to the topic that controls the LED
    subscription_topic = f"ActiveHarmony/{mac_address}/+/+/+"
    client.subscribe(subscription_topic)
    topic_subscriptions.add(subscription_topic)

    # Start the loop to process received messages
    client.loop_start()

    # Announce the device to the world
    #announce_device(client)

    def main(stdscr):
        global sensor_status  # Tell Python to use the global variable instead of creating a local one 

        curses.curs_set(0)  # Hide the cursor
        stdscr.nodelay(1)  # Make getch() non-blocking
        stdscr.timeout(100)  # Refresh every 100ms

        client.user_data_set(stdscr)  # Make sure we can access the screen bg in the event handler

        update_screen(stdscr)

        while True:
            key = stdscr.getch()
            if key == 27:  # ESC key
                break
            elif key == ord(' '):  # Space bar
                sensor_status = not sensor_status

            # Publish the sensor status when it has changed
            publish_sensor_status(client)

            update_screen(stdscr)

            time.sleep(0.5)
            
    curses.wrapper(main)
```

### Arduino

```sh
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char* ssid = "A35 van Leni";
const char* password = "HotspotLeni";

const char* mqtt_server = "mqtt.eclipseprojects.io";
const int mqtt_port = 1883;
 

// set topics to subscribe to
// const String topic = "ActiveHarmony/+/+/+/+"; // zetlicht/ mac / kleurencode

// declare variable to story the incoming MQTT payload
String payload;

int roodPin= 9;
int groenPin = 11;
int blauwPin = 10;

const int sensorPin = A0; 

String getMacAdress(){
  char macStr[18];
  
  byte mac[6];
  WiFi.macAddress(mac);

  //Serial.print("MAC Address: ");
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X" , mac[0],mac[1], mac[2], mac[3],mac[4], mac[5]);
  return String(macStr);
}

String maakTopic(){
  String mac = getMacAdress();
  String topic = "ActiveHarmony/" + mac + "/+/+/+" ;
  return topic;
}

void setColor(int redValue, int greenValue,  int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin,  greenValue);
  analogWrite(blauwPin, blueValue);
}

void split(String data, char delimiter, String result[], int maxParts) {
    int start = 0;
    int end = 0;
    int index = 0;
    
    while ((end = data.indexOf(delimiter, start)) != -1 && index < maxParts - 1) {
        result[index++] = data.substring(start, end);
        start = end + 1;
    }
    
    result[index] = data.substring(start); // Add the last part
}

// Callback functie die wordt aangeroepen wanneer een bericht wordt ontvangen
void onMqttMessage(int messageSize) {
  // print out the topic and some message details
  Serial.println("Received a message: ");
  String topic = mqttClient.messageTopic();
  Serial.println(topic);
  Serial.print(mqttClient.messageTopic());

  // read the incoming data and store it into the payload variable
  String payloadString = "";
  for (int i = 0; i < messageSize; i++) {
    payloadString += (char)mqttClient.read();
  }
  payload = payloadString;
  Serial.println(payload);
  zetlicht(topic);
}

void setup() {
  Serial.begin(9600);
  pinMode(roodPin,  OUTPUT);              
  pinMode(groenPin, OUTPUT);
  pinMode(blauwPin, OUTPUT);

  // Verbinden met WiFi
  Serial.print("Verbinden met WiFi... ");
  if (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden!");
  Serial.print("IP-adres: ");
  Serial.println(WiFi.localIP());

  // Verbinden met MQTT-server
  Serial.print("Verbinden met MQTT-broker... ");
  if (!mqttClient.connect(mqtt_server, mqtt_port)) {
    Serial.println("Mislukt!");
    while (true);
  }
  Serial.println("Verbonden met MQTT!");

  // subscribe to the topic
  Serial.print("Subscribing to topic: ");
  String topic = maakTopic();
  Serial.println(topic);
  mqttClient.subscribe(topic);

  // set the message receive callback function:
  // Trigger the 'onMqttMessage' function when mqttClient.poll() (in the loop function) detects a message
  mqttClient.onMessage(onMqttMessage);
}

void zetlicht(String input){
  Serial.println("zetlicht");
  Serial.println(input);
  
  String result[5];
  split(input, '/', result, 5);
  
  if (input.startsWith("ActiveHarmony/")) {
    String mac = result[1];
    String rood = result[2];
    String groen = result[3];
    String blauw = result[4];// MAC-adres is de eerste waarde
    Serial.println(mac);
    Serial.println(rood);
    Serial.println(groen);
    Serial.println(blauw);

  // Vergelijk MAC-adres met macStr
    setColor(rood.toInt(), groen.toInt(), blauw.toInt());
    delay(2000);
    Serial.println("kleurwaarde");
    Serial.println(rood.toInt());
    Serial.println(groen.toInt());
    Serial.println(blauw.toInt());
  }
}

void loop() {  

  int lichtwaarde = analogRead(A0);  // Lees de analoge waarde van de lichtsensor
    Serial.print("Lichtwaarde: ");
    Serial.println(lichtwaarde);  // Toon de waarde in de seriële monitor
    delay(500);

  char lichtwaardeStr[10]; // Buffer voor de lichtwaarde als string
  sprintf(lichtwaardeStr, "%d", lichtwaarde); // Zet int om naar string

  // Mac adresss als char*
  const char* macStr = getMacAdress().c_str();

  // Stuur een testbericht naar MQTT
  char topic[50] = "ActiveHarmony/" ;
  strcat(topic, macStr) ;
  strcat(topic, "/");
  strcat(topic, lichtwaardeStr); 
  mqttClient.beginMessage(topic);
  mqttClient.print("Hallo vanaf Arduino Nano 33 IoT!");
  mqttClient.endMessage();

  Serial.println("MQTT bericht verzonden!");
  Serial.println(topic);

  delay(100);  // Wacht 5 seconden voordat een nieuw bericht wordt verzonden

  mqttClient.poll();
}
```
