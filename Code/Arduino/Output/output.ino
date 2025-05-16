void setColor(int redValue, int greenValue,  int blueValue) {
  analogWrite(roodPin, redValue);
  analogWrite(groenPin,  greenValue);
  analogWrite(blauwPin, blueValue);
}

char lichtwaardeStr[10];
sprintf(lichtwaardeStr, "%d", waardeVoorMQQT);

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

Serial.begin(9600);
Serial.print("Verbinden met WiFi... ");
Serial.println("Verbonden!");
Serial.print("IP-adres: ");
Serial.println(WiFi.localIP());

Serial.print("Verbinden met MQTT-broker... ");
Serial.println("Verbonden met MQTT!");

Serial.print("Subscribing to topic: ");
Serial.println(topic);

Serial.print("Lichtwaarde: ");
Serial.println(lichtwaarde);

Serial.println(waardeVoorMQQT);

Serial.println("Received a message: ");
Serial.println(topic);
Serial.println(payload);
Serial.println("zetlicht");
Serial.println(input);
Serial.println(mac);
Serial.println(rood);
Serial.println(groen);
Serial.println(blauw);
Serial.println("kleurwaarde");
Serial.println(rood.toInt());
Serial.println(groen.toInt());
Serial.println(blauw.toInt());
Serial.println("MQTT bericht verzonden!");
Serial.println(topic);
