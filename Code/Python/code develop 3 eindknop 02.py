import random
import os
import pygame
import time
import threading
from threading import Thread
import paho.mqtt.client as mqtt
from collections import Counter


MQTT_BROKER_URL = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE = 60

mqtt_connected = threading.Event()

sensor_max = 600

is_muziek_bezig = False

geselecteerde_muziek_index = None

huidig_volume = 1.0
volume_lock = threading.Lock()
volume_thread = None
stop_thread = False
volume_monitor_paused = threading.Event()

muziek_map = os.path.join(os.path.dirname(__file__), "muziek")

#muziek kan gelijk waar op de computer worden gevonden
muziek_dictionary = {
    i: os.path.join(muziek_map, f"Muziek{i+1}.mp3") for i in range(3)
}

#Bericht ontvangen ActiveHarmony/18:1F:3B:BD:9E:7C:/909
#Bericht ontvangen ActiveHarmony/20:88:4E:DA:D4:D4:/886
#Bericht ontvangen ActiveHarmony/74:C7:7A:1B:5A:E0:/975
#Bericht ontvangen ActiveHarmony/1C:31:7B:1B:5A:E0:/8
#Bericht ontvangen ActiveHarmony/4C:F1:77:1B:5A:E0:/946

#arduino_dict = {'18:1F:3B:BD:9E:7C': 'mac1', '20:88:4E:DA:D4:D4': 'mac2', '74:C7:7A:1B:5A:E0': 'mac3', '1C:31:7B:1B:5A:E0': 'mac4', '4C:F1:77:1B:5A:E0': 'mac5'}
arduino_dict = {'20:88:4E:DA:D4:D4': 'mac1', '74:C7:7A:1B:5A:E0': 'mac2', '1C:31:7B:1B:5A:E0': 'mac3', '4C:F1:77:1B:5A:E0': 'mac4'}
# Hou globaal de sensorwaarden bij, per Arduino
# Initialiseer ze allemaal op -1
tegel_sensor_waardes = dict()
for mac in arduino_dict.keys():
    tegel_sensor_waardes[mac] = sensor_max + 1

# Functie die de volgorde van de tegels genereert, afhankelijk van het aantal ingevoerde Arduino's
def genereer_volgorde_tegels():
    #Volgorde = list(arduino_dict.values())  # Maak een lijst van tegels afhankelijk van het aantal Arduino's
    #random.shuffle(Volgorde)  # Willekeurig schudden van de volgorde
    #print(f"Volgorde van tegels: {Volgorde}")
    max_per_mac = 3

    while True: # Herhaal totdat aan alle voorwaarden is voldaan
        Volgorde = []
        while len(Volgorde) < 6:
            getal = random.randint(1, 4)
            mac = f"mac{getal}"
            if len(Volgorde) == 0 or Volgorde[-1] != mac:
                telling = Counter(Volgorde)
                if telling[mac] < max_per_mac:
                    Volgorde.append(mac)
        
        unieke_macs = set(Volgorde)
        if all(f"mac{i}" in unieke_macs for i in range(1, 5)):
            break  # Voorwaarde is voldaan, breek de loop en geef de volgorde terug
    
    print(f"Volgorde van tegels: {Volgorde}")
    return Volgorde
#geen 2x dezelfde tegel na elkaar 

def vraag_muziekfragment():
    global geselecteerd_muziek_index

    print("Kies een muziekfragment:")
    for index, path in muziek_dictionary.items():
        print(f"{index}: {path}")

    while True:
        try:
            keuze = int(input("Geef het nummer van het gewenste muziekfragment: "))
            if keuze in muziek_dictionary:
                geselecteerd_muziek_index = keuze
                print(f"Gekozen muziekfragment: {muziek_dictionary[keuze]}")
                break
            else:
                print("Ongeldige keuze. Kies een geldig nummer.")
        except ValueError:
            print("Ongeldige invoer. Geef een getal in.")

# Functie die het spel afspeelt
def speel_muziek() -> None:
    global is_muziek_bezig
    is_muziek_bezig = True #blokkeer berichtverwerking
    huidig_volume = 1.0
    print(f"Speel {muziek_dictionary[geselecteerd_muziek_index]}")
    start_muziek() #muziek liep in zichzelf vast, nu blijft deze herhalen
    pas_volume_geleidelijk_aan(0.5)

def start_volume_monitor(start_time):
    def monitor():
        while pygame.mixer.music.get_busy():
            if not volume_monitor_paused.is_set():
                wacht_tijd = time.time() - start_time
                pas_volume_aan(wacht_tijd)
            time.sleep(1)
    Thread(target=monitor, daemon=True).start()

def pas_volume_geleidelijk_aan(doelvolume, stapgrootte=0.075, interval=0.066):
    global huidig_volume, volume_thread, stop_thread

    def volume_worker():
        global huidig_volume, stop_thread
        while not stop_thread:
            with volume_lock:
                if abs(huidig_volume - doelvolume) < stapgrootte:
                    huidig_volume = doelvolume
                    pygame.mixer.music.set_volume(huidig_volume)
                    break
                if huidig_volume > doelvolume:
                    huidig_volume -= stapgrootte
                else:
                    huidig_volume += stapgrootte
                pygame.mixer.music.set_volume(huidig_volume)
            time.sleep(interval)

    # Stop eventueel lopende thread
    stop_thread = True
    if volume_thread and volume_thread.is_alive():
        volume_thread.join()
    stop_thread = False

    # Start nieuwe thread
    volume_thread = threading.Thread(target=volume_worker)
    volume_thread.start()

def pas_volume_aan(wacht_tijd):
    if wacht_tijd == 0:
        doelvolume = 1.0
        stapgrootte = 1
        interval = 0.05
    else:
        doelvolume = max(0.5, 1.0 - (wacht_tijd / 30))
        stapgrootte = 0.75
        interval = 0.066
    threading.Thread(target=pas_volume_geleidelijk_aan, args=(doelvolume, stapgrootte, interval)).start()
    pas_volume_geleidelijk_aan(doelvolume, stapgrootte, interval)



def connect_mqtt(client, userdata, flags, rc):
    if rc == 0:
        print("Geconnecteerd")
        mqtt_connected.set()  # verbinding is gelukt
        topic = f"ActiveHarmony/+/+"
        client.subscribe(topic)
        print(f"Geabonneerd op topic: {topic}")  # Abonneer je direct na het verbinden
    else:
        print("Verbinden mislukt")

# Callback functie voor ontvangen berichten
def on_message(client, userdata, message):
    global tegel_sensor_waardes
    if message is None:
        return
    #print(f"Ontvangen data van Arduino: {message.topic}")
    #print(f"Bericht ontvangen {message.topic}")
    parts = message.topic.split("/")
    if len(parts)<3:
        print(f"Ongeldig ontvangen: {message.topic}")
        return
    mac = parts[1]
    try:
        sensor_int = int(parts[2])
        tegel_sensor_waardes[mac] = sensor_int # Opslaan in variabele
    except ValueError:
        print(f"Fout bij het omzetten van sensorwaarde naar int: {parts[2]}")
    #print(received_message)

def wacht_op_tegel_veranderd(timeout, min_veranderings_waarde) -> tuple:
    """
    Deze code wacht op tegel verandering
    """
    start_time = time.time()

    while any (sensor_waarde < sensor_max for sensor_waarde in tegel_sensor_waardes.values()):
        print("wacht tot alle tegels losgelaten zijn")
        time.sleep(0.1)

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
                wacht_tijd = time.time() - start_time
                pas_volume_aan (wacht_tijd)
                return mac, tegel_sensor_waardes[mac]
            time.sleep(timeout)

def wacht_op_start_knop():
    #blokkeer verder spelverloop tot de gebruiker 'start typt'
    while True:
        user_input = input("Typ 'start' om het spel te beginnen: ").strip().lower()
        if user_input == "start":
            print("Start bevestigd! Voorbeeld wordt getoond.")
            break
        else:
            print("Ongeldige invoer. Typ exact 'start' om te beginnen.")

def stuur_lichtcommando(topic) -> None:
    #print(f"MQTT-bericht verzonden: {topic}")
    client.publish(topic, "1") 
    print (topic, "1")

def stuur_leds(rood, groen, blauw, leds: list) -> None:
    print(f"Stuur leds {leds}")
    for mac in leds:
        stuur_lichtcommando(f"ActiveHarmony/{mac}/{rood}/{groen}/{blauw}")

def stuur_tijdelijk_leds(rood, groen, blauw, leds: list, duur: int) -> None:
    stuur_leds(rood, groen, blauw, leds)
    time.sleep(duur)
    stuur_leds(0, 0, 0, leds)

def knipper_leds(rood, groen, blauw, leds: list, aantal_keer: int, duur: int) -> None:
    for i in range(aantal_keer):
        stuur_tijdelijk_leds(rood, groen, blauw, leds, duur)

def stuur_fout(leds: list):
    knipper_leds(255,0,0,leds,5,1)
    time.sleep (1)

def stuur_tijdelijk_wit(leds: list):
    stuur_tijdelijk_leds(255,255,255, leds, 3)

def stuur_wit(leds: list):
    stuur_leds(255, 255, 255, leds)

def stuur_blauw(leds: list):
    stuur_tijdelijk_leds(0, 0, 255, leds, 1)

def stuur_groen(leds: list):
    stuur_tijdelijk_leds(0,255, 0,leds, 3)

def stop_muziek():
    pygame.mixer.music.stop() #stop de muziek
    global stop_thread
    stop_thread = True  # Stop de thread die het volume aanpast
    if volume_thread and volume_thread.is_alive():
        volume_thread.join()
    stop_thread = False

def start_muziek(herhalen = True):
    global huidig_volume
    print(f"Speel {muziek_dictionary[geselecteerd_muziek_index]}")
    pygame.mixer.music.load(muziek_dictionary[geselecteerd_muziek_index])
    pygame.mixer.music.play(-1 if herhalen else 0)  # Muziek herhaalt zichzelf
    pas_volume_geleidelijk_aan(1.0)  # Zorg dat volume vanaf het begin juist is


def do_reactie (mac, value, referentie, stap, al_correct, wacht_tijd):
    # Controleer of het MAC-adres in de arduino_dict zit
    #if value == 1:
    #    value_knop = 100
    #    value = value_knop
    #elif value == 0:
    #    value_knop = 1000
    #    value = value_knop

    if mac not in arduino_dict:
        print(f"Ongeldig MAC-adres: {mac}")
        return False, False
    
    if value> sensor_max:
        stop_muziek()
        stuur_fout(list(arduino_dict.keys()))
        time.sleep(1)
        wacht_op_alles_uit()
        return False
    
    if sensor_correct(mac, referentie,stap):
        #if mac not in al_correct:
        stuur_groen([mac])
        volume_monitor_paused.set() #pauzeer de daling van geluid
        pas_volume_aan(wacht_tijd)
        pygame.mixer.music.set_volume(1.0)
        time.sleep(2)
        volume_monitor_paused.clear()
       #pas_volume_geleidelijk_aan(0.5)     # Verminder opnieuw geleidelijk
        return True
    else:
        stop_muziek()
        stuur_fout(list(arduino_dict.keys()))
        time.sleep(1)
        #wacht tot er nergens meer op gestaan wordt
        wacht_op_alles_uit()
        return False

def wacht_op_alle_rode_lichten_uit(leds: list):
    """
    Wacht totdat alle rode lichten uit zijn door gebruik te maken van wacht_op_tegel_veranderd().
    """
    sensors_aan = krijg_sensors_die_aanliggen()

    while sensors_aan:
        print(f"Wachten tot alle rode lichten uit zijn. Deze sensoren liggen nog aan: {sensors_aan}")
        stuur_leds(255, 0, 0, sensors_aan)  # Rood licht op sensoren die nog aanliggen

        # Wacht op verandering op een van de tegels
        wacht_op_tegel_veranderd(timeout=0.5, min_veranderings_waarde=30)

        # Check opnieuw of alles uit is
        sensors_aan = krijg_sensors_die_aanliggen()

    print("Alle rode lichten zijn uit.")


def krijg_sensors_die_aanliggen() -> list:
    """
    Verkrijg een lijst van sensoren die aan staan
    """
    sensors_die_aanliggen = []
    for mac, sensor_waarde in tegel_sensor_waardes.items():
        if sensor_waarde < sensor_max:
            sensors_die_aanliggen.append(mac)
    return sensors_die_aanliggen

def wacht_op_alles_uit():
    """
    Blijf wachten tot alle sensoren zijn uitgeschakeld
    Ondertussen worden de sensoren die aan staan rood gekleurd
    """
    sensors_aan = krijg_sensors_die_aanliggen()
    while sensors_aan:
        print(f"Wachten tot alles uit is. Deze sensoren liggen nog aan: {sensors_aan}")
        stuur_fout(sensors_aan)
        time.sleep(1)
        sensors_aan = krijg_sensors_die_aanliggen()

def volgorde_licht(referentie):
    print("Wacht totdat alle rode lichten uit zijn...")
    wacht_op_alle_rode_lichten_uit(list(arduino_dict.keys()))  # Wacht totdat de rode lichten uit zijn
    print("Alle rode lichten zijn uit. Volgorde in wit wordt nu getoond.")

    for mac_naam in referentie:
        for mac_adres,naam in arduino_dict.items():
            if naam == mac_naam:
                stuur_tijdelijk_wit([mac_adres])
                time.sleep (2)

def bereken_score(foutteller):
    score = max(0,100 - (foutteller*5))
    return score

def opstart_spel():
    #stuur_leds(0,255,0,['18:1F:3B:BD:9E:7C'])
    wacht_op_alles_uit()
    print("Alle sensoren zijn uit")
    stuur_blauw(list(arduino_dict.keys()))
    time.sleep(1)
    #stuur_leds(0,0,0,list(arduino_dict.keys()))
    print("We kunnen beginnen")

def sensor_correct (mac, referentie, stap) -> bool:
    mac_naam = referentie[stap]
    for amac, naam in arduino_dict.items():
        if naam == mac_naam and amac == mac:
            return True
    return False

def verwerk_einde_spel(al_correct, foutteller):
    print("Je hebt het spel volledig juist gespeeld!")
    score = bereken_score(foutteller)
    print(f"Je score: {score}/100")

    knipper_leds(0, 255, 0, list(al_correct), 5, 1)
    #pygame.mixer.music.stop() #muziek stopt volledig
    #start_muziek(herhalen = False)

    while pygame.mixer.music.get_busy():
        time.sleep (0.5) # Wacht tot muziek volledig is afgespeeld

    print("Muziek afgelopen. Einde van het spel.")

def start_muziek_en_spel_loop(referentie):
    stap = 0
    al_correct = set()
    foutteller = 0
    wacht_tijd = 1
    speel_muziek() #start een muziekstuk bij het begin van het spel
    start_volume_monitor(time.time())

    while stap < len(referentie):
        mac,value = wacht_op_tegel_veranderd(0.5, sensor_max)
        correct = do_reactie(mac, value, referentie, stap, al_correct, wacht_tijd)
        print(f"Stap {stap} correct!")

        if correct:
            stap += 1
            al_correct.add(mac)
            print(f"Reeds correcte tegels: {len(al_correct)}")
        else:
            foutteller += 1
            stap = 0
            al_correct.clear()
            print("Fout! Terug naar stap 0")
            time.sleep (5)
            print(referentie)
            volgorde_licht(referentie)
            stop_muziek()
            start_muziek() 
            start_volume_monitor(time.time())
            pas_volume_aan(0.5)

    verwerk_einde_spel(al_correct, foutteller)
    


def speel_het_spel(referentie):
    opstart_spel() #Alle sensoren worden gereset en lichten geactiveerd
    wacht_op_start_knop() # wacht tot gebruiker 'start' typt komt overeen met start knop op het controle station
    volgorde_licht(referentie) # toon het voorbeeld
    stop_muziek()
    speel_muziek()
    start_muziek_en_spel_loop(referentie)

if __name__ == "__main__":
    # Initialiseer de pygame mixer voor audio
    pygame.mixer.init()

    # Maak een MQTT-client aan en verbind enkele functies
    client = mqtt.Client()
    client.loop_start()
    client.on_connect = connect_mqtt
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE)

    mqtt_connected.wait()  # wacht tot verbinding is gemaakt

    vraag_muziekfragment() #hier roep je aan met welk liedje ze willen spelen

    # Bedenk de puzzel die moet worden opgelost
    referentie = genereer_volgorde_tegels()
    #referentie = ['mac3', 'mac1', 'mac2', 'mac4', 'mac2', 'mac3']

    # Speel het spel tot volledig gespeeld
    volledig_gespeeld = False

    while not volledig_gespeeld:
         volledig_gespeeld = speel_het_spel(referentie)

#herstart de muziek terug wanneer de referentie nogmaals getoont is

