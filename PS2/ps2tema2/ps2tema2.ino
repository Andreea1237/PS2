#include <EEPROM.h>

String message = "";
int ledPin = 13;
int tempPin = A0;
int floodButtonPin = 8;

#define MAX_MSGS 10
#define MSG_SIZE 32
int currentIndex = 0;

bool manualLedControl = false;
bool ledState = false;
bool floodReported = false;

void saveMessageToEEPROM(String msg) {
  if (msg.length() > MSG_SIZE - 1) msg = msg.substring(0, MSG_SIZE - 1); 
  int addr = currentIndex * MSG_SIZE;
  for (int i = 0; i < msg.length(); i++) {
    EEPROM.write(addr + i, msg[i]);
  }
  EEPROM.write(addr + msg.length(), '\0');
  currentIndex = (currentIndex + 1) % MAX_MSGS;
}

void printStoredMessages() {
  Serial.println("Mesaje stocate:");
  for (int i = 0; i < MAX_MSGS; i++) {
    int addr = i * MSG_SIZE;
    char buf[MSG_SIZE];
    for (int j = 0; j < MSG_SIZE; j++) {
      buf[j] = EEPROM.read(addr + j);
      if (buf[j] == '\0') break;
    }
    Serial.println(buf);
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  pinMode(floodButtonPin, INPUT_PULLUP);
  digitalWrite(ledPin, LOW);
  printStoredMessages();
}

void loop() {
  // Citim temperatura
  int value = analogRead(tempPin);
  float voltage = value * (5.0 / 1023.0);
  float temperatureC = voltage * 100;
  Serial.print("TEMP:");
  Serial.println(temperatureC);

  // Verificăm comenzi din Serial
  if (Serial.available() > 0) {
    message = Serial.readStringUntil('\n');
    message.trim();

    if (message == "LED_ON") {
      manualLedControl = true;
      ledState = true;
    } else if (message == "LED_OFF") {
      manualLedControl = true;
      ledState = false;
    } else if (message == "LED_AUTO") {
      manualLedControl = false;
    } else {
      saveMessageToEEPROM(message);
    }
  }

  // Citim butonul fizic de inundație
  bool floodButtonPressed = digitalRead(floodButtonPin) == LOW;

  // Debounce pentru buton
  static unsigned long lastDebounceTime = 0;
  unsigned long debounceDelay = 50;

  if (floodButtonPressed && (millis() - lastDebounceTime) > debounceDelay) {
    if (!floodReported) {
      Serial.println("FLOOD_DETECTED");
      floodReported = true;
    }
    lastDebounceTime = millis();
  }

  if (!floodButtonPressed) {
    floodReported = false;
  }

  // CONTROLUL LED-ULUI
  if (manualLedControl) {
    digitalWrite(ledPin, ledState ? HIGH : LOW);
  } else {
    // CONTROL LOCAL CU BUTONUL DE INUNDAȚIE
    if (floodButtonPressed) {
      digitalWrite(ledPin, HIGH);
    } else {
      digitalWrite(ledPin, LOW);
    }
  }

  delay(200);
}
