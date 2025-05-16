pinMode(knopPin, INPUT);
int lichtwaarde = digitalRead(knopPin);

void onMqttMessage(int messageSize) {
  Serial.println("Received a message: ");
  String topic = mqttClient.messageTopic();
  Serial.println(topic);
  Serial.print(mqttClient.messageTopic());

  String payloadString = "";
  for (int i = 0; i < messageSize; i++) {
    payloadString += (char)mqttClient.read();
  }
  payload = payloadString;
  Serial.println(payload);
  zetlicht(topic);
}

mqttClient.subscribe(topic);
mqttClient.onMessage(onMqttMessage);

void zetlicht(String input){
  Serial.println("zetlicht");
  Serial.println(input);
  
  String result[5];
  split(input, '/', result, 5);
  
  if (input.startsWith("ActiveHarmony/")) {
    String mac = result[1];
    String rood = result[2];
    String groen = result[3];
    String blauw = result[4];
    Serial.println(mac);
    Serial.println(rood);
    Serial.println(groen);
    Serial.println(blauw);

    setColor(rood.toInt(), groen.toInt(), blauw.toInt());
    delay(2000);
    Serial.println("kleurwaarde");
    Serial.println(rood.toInt());
    Serial.println(groen.toInt());
    Serial.println(blauw.toInt());
  }
}
