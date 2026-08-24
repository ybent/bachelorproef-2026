/**
 * @file main.cpp
 * @brief ESP32-S3 Thesis PoC MQTT Netwerk Traffic Generator 
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- Configuratie ---
const char* WIFI_SSID     = "Bachelorproef_IoT";  
const char* WIFI_PASSWORD = "Hogent_IoT";         
const char* MQTT_SERVER   = "10.0.40.10";         
const int   MQTT_PORT     = 1883;

// --- MQTT Credentials ---
const char* MQTT_USER     = "iot_user";           
const char* MQTT_PASS     = "HogentIoT";          

WiFiClient espClient;
PubSubClient mqttClient(espClient);

unsigned long sequenceNumber   = 0;
unsigned long lastNormalTx     = 0;

void connectWiFi() {
  Serial.print("[WIFI] Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[WIFI] Connected! IP: " + WiFi.localIP().toString());
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Connecting to broker...");
    String clientId = "ESP32S3-Thesis-" + String(random(0xffff), HEX);
    
    if (mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  connectWiFi();
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setBufferSize(1024);
}

void sendValidTelemetry() {
  sequenceNumber++;
  JsonDocument doc;
  
  doc["seq"]          = sequenceNumber;
  doc["device_id"]    = "ESP32-S3-N16R8";
  doc["uptime_sec"]   = millis() / 1000;
  doc["free_heap"]    = ESP.getFreeHeap();
  doc["free_psram"]   = ESP.getFreePsram();
  doc["wifi_rssi"]    = WiFi.RSSI();
  doc["sim_temp"]     = 20.0 + (random(0, 100) / 10.0);

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  mqttClient.publish("iot/esp32s3/telemetry", jsonBuffer);
  Serial.printf("[TX MQTT #%lu] Published telemetry payload.\n", sequenceNumber);
}

// Zolang we verbonden blijven met de MQTT broker, blijven we telemetry berichten sturen
void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  unsigned long now = millis();

  // Baseline Phase: Stuurt elke 5 seconden een geldig MQTT-telemetriebericht naar de broker
  if (now - lastNormalTx >= 5000) {
    lastNormalTx = now;
    sendValidTelemetry();
  }
}