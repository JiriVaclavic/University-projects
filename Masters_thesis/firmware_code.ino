#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <DHT.h>

#define MQTT_MAX_PACKET_SIZE 1024

// WiFi and MQTT details
const char* ssid = "_";
const char* password = "_";
const char* mqtt_server = "_";
const char* access_token = "_";

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// State variables
bool lastHarvestState = false;
bool lastVentilationState = false;

// Pins for L293D modules and other devices
int ENA1 = 13;
int IN1_1 = 12;
int IN1_2 = 14;

int ENA2 = 25;
int IN1_3 = 26;
int IN1_4 = 27;

int ENA3 = 33;
int IN1_5 = 32;
int IN1_6 = 19;

int ENA4 = 23;
int IN1_7 = 22;
int IN1_8 = 21;

#define SERVO_PIN 2
#define FAN_PIN 17  // Additional fan pin

const int frequency = 5000;
const int pwm_channel1 = 2;
const int pwm_channel2 = 3;
const int pwm_channel3 = 4;
const int pwm_channel4 = 5;
const int resolution = 8;

Servo servo1;

// DHT22 settings
#define DHTPIN 15     // Pin on ESP32 to which the DHT22 is connected
#define DHTTYPE DHT22 // DHT22 sensor type
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);  // Serial communication at 115200 baud

  // Initialize DHT sensor
  dht.begin();

  // Connect to WiFi
  connectToWiFi();

  // Set up MQTT server and callback function
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  connectToMQTT();

  // Setup pins for L293D modules
  pinMode(ENA1, OUTPUT);
  pinMode(IN1_1, OUTPUT);
  pinMode(IN1_2, OUTPUT);
  digitalWrite(IN1_1, LOW);
  digitalWrite(IN1_2, LOW);
  Serial.println("L298N 1 setup done");

  // Setup pins for the second L293D module
  pinMode(ENA2, OUTPUT);
  pinMode(IN1_3, OUTPUT);
  pinMode(IN1_4, OUTPUT);
  digitalWrite(IN1_3, LOW);
  digitalWrite(IN1_4, LOW);
  Serial.println("L298N 2 setup done");

  // Setup pins for the third L293D module
  pinMode(ENA3, OUTPUT);
  pinMode(IN1_5, OUTPUT);
  pinMode(IN1_6, OUTPUT);
  digitalWrite(IN1_5, LOW);
  digitalWrite(IN1_6, LOW);
  Serial.println("L298N 3 setup done");

  // Setup pins for the fourth L293D module
  pinMode(ENA4, OUTPUT);
  pinMode(IN1_7, OUTPUT);
  pinMode(IN1_8, OUTPUT);
  digitalWrite(IN1_7, LOW);
  digitalWrite(IN1_8, LOW);
  Serial.println("L298N 4 setup done");

  // Setup PWM channels
  ledcSetup(pwm_channel1, frequency, resolution);
  ledcAttachPin(ENA1, pwm_channel1);
  Serial.println("PWM channel 1 setup done");

  ledcSetup(pwm_channel2, frequency, resolution);
  ledcAttachPin(ENA2, pwm_channel2);
  Serial.println("PWM channel 2 setup done");

  ledcSetup(pwm_channel3, frequency, resolution);
  ledcAttachPin(ENA3, pwm_channel3);
  Serial.println("PWM channel 3 setup done");

  ledcSetup(pwm_channel4, frequency, resolution);
  ledcAttachPin(ENA4, pwm_channel4);
  Serial.println("PWM channel 4 setup done");

  servo1.attach(SERVO_PIN);
  Serial.println("Servo attached");

  // Setup additional fan pin
  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(FAN_PIN, LOW);  // Ensure the fan is off initially
  Serial.println("Additional fan setup done");
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  // Voltage measurement
  int sensorValue = analogRead(35); // Read ADC value from GPIO34
  float voltage = sensorValue * (3.3 / 4095.0); // Convert ADC value to voltage 0-3.3V ? 
  
  // Calculate actual voltage based on voltage divider
  float actualVoltage = voltage * 2; 

  // Read temperature and humidity
  float humidity = readHumidity();
  float temperature = readTemperature();

  // Check if reading failed and skip publishing if so
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    // Publish voltage, temperature, and humidity to MQTT
    publishData(voltage, actualVoltage, temperature, humidity);
  }
  
  delay(1000); // Measure every second
}

// Function to connect to WiFi
void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); 
    Serial.print(".");
  }
  Serial.println("WiFi connected");
}

// Function to connect to MQTT server
void connectToMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client", access_token, nullptr)) {
      Serial.println("connected");
      if (client.subscribe("v1/devices/me/attributes")) {
        Serial.println("Subscribed to shared attributes");
      } else {
        Serial.println("Failed to subscribe to shared attributes");
      }
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to reconnect to MQTT server
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Reconnecting to MQTT...");
    if (client.connect("ESP32Client", access_token, nullptr)) {
      Serial.println("connected");
      if (client.subscribe("v1/devices/me/attributes")) {
        Serial.println("Resubscribed to shared attributes");
      } else {
        Serial.println("Failed to resubscribe to shared attributes");
      }
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to publish voltage, temperature, and humidity to MQTT
void publishData(float voltage, float actualVoltage, float temperature, float humidity) {
  DynamicJsonDocument doc(1024);
  doc["voltage"] = actualVoltage;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  char jsonBuffer[1024];
  serializeJson(doc, jsonBuffer);
  client.publish("v1/devices/me/telemetry", jsonBuffer);
}

// Function to handle MQTT messages
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Shared attribute received on topic: " + String(topic) + ", payload: " + message);
  
  // Parse the JSON payload to extract method and parameters
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.println("Failed to parse JSON payload");
    return;
  }
  
  // Process attributes
  if (doc.containsKey("harvest")) {
    handleHarvest(doc["harvest"]);
  }
  
  if (doc.containsKey("ventilation")) {
    handleVentilation(doc["ventilation"]);
  }
}

// Function to turn on motors (ventilation)
void ventilationOn() {
  Serial.println("ventilation on");
  ledcWrite(pwm_channel1, 254);
  digitalWrite(IN1_1, HIGH);
  digitalWrite(IN1_2, LOW);

  ledcWrite(pwm_channel2, 254);
  digitalWrite(IN1_3, HIGH);
  digitalWrite(IN1_4, LOW);

  servo1.write(180);
  delay(1100);
  servo1.write(90);

  digitalWrite(FAN_PIN, HIGH);  // Turn on additional fan
}

// Function to turn off motors (ventilation)
void ventilationOff() {
  Serial.println("ventilation off");
  ledcWrite(pwm_channel1, 0);
  digitalWrite(IN1_1, LOW);
  digitalWrite(IN1_2, LOW);

  ledcWrite(pwm_channel2, 0);
  digitalWrite(IN1_3, LOW);
  digitalWrite(IN1_4, LOW);

  servo1.write(0);
  delay(1100);
  servo1.write(90);

  digitalWrite(FAN_PIN, LOW);  // Turn off additional fan
}

// Function to turn on fans and servo (harvest)
void harvestOn() {
  Serial.println("harvest on");
  ledcWrite(pwm_channel3, 254);
  digitalWrite(IN1_5, HIGH);
  digitalWrite(IN1_6, LOW);

  ledcWrite(pwm_channel4, 254);
  digitalWrite(IN1_7, HIGH);
  digitalWrite(IN1_8, LOW);
}

// Function to turn off fans and servo (harvest)
void harvestOff() {
  Serial.println("harvest off");
  ledcWrite(pwm_channel3, 254);
  digitalWrite(IN1_5, LOW);
  digitalWrite(IN1_6, HIGH);

  ledcWrite(pwm_channel4, 254);
  digitalWrite(IN1_7, LOW);
  digitalWrite(IN1_8, HIGH);
}

// Function to handle harvest state
void handleHarvest(bool harvestState) {
  if (harvestState != lastHarvestState) {
    printHarvest(harvestState);
    lastHarvestState = harvestState;
  }
}

// Function to handle ventilation state
void handleVentilation(bool ventilationState) {
  if (ventilationState != lastVentilationState) {
    printVentilation(ventilationState);
    lastVentilationState = ventilationState;
  }
}

// Function to print harvest state
void printHarvest(bool state) {
  if (state) {
    Serial.println("harvestOn");
    harvestOn();
  } else {
    Serial.println("harvestOff");
    harvestOff();
  }
}

// Function to print ventilation state
void printVentilation(bool state) {
  if (state) {
    Serial.println("ventilationOn");
    ventilationOn();
  } else {
    Serial.println("ventilationOff");
    ventilationOff();
  }
}

// Function to read humidity from DHT22 sensor
float readHumidity() {
  return dht.readHumidity();
}

// Function to read temperature from DHT22 sensor
float readTemperature() {
  return dht.readTemperature();
}
