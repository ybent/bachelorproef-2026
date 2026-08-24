/**
 * @file main.cpp
 * @brief ESP32-C6 Thesis PoC Zigbee Netwerk Traffic Generator 
 */

#ifndef ZIGBEE_MODE_ED
#define ZIGBEE_MODE_ED
#endif

#include <Arduino.h>
#include "Zigbee.h"

#define TEMP_SENSOR_ENDPOINT_NUMBER 1

// 10000 = 10 seconds 
const unsigned long REPORT_INTERVAL_MS = 10000; 

ZigbeeTempSensor zbTempSensor = ZigbeeTempSensor(TEMP_SENSOR_ENDPOINT_NUMBER);

void setup() {
  Serial.begin(115200);
  delay(1000);


  zbTempSensor.setManufacturerAndModel("Espressif", "ESP32-C6-Zigbee-Node");
  Zigbee.addEndpoint(&zbTempSensor);

  if (!Zigbee.begin(ZIGBEE_END_DEVICE, false)) {
    Serial.println("[ERROR] Failed to start Zigbee network connection.");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("[ZIGBEE] Connected / Reconnected to Zigbee network!");
}

void loop() {
  static unsigned long lastUpdate = 0;
  
  // Stuurt telemetry naar de Zigbee netwerk elke 10 seconden
  if (millis() - lastUpdate >= REPORT_INTERVAL_MS) {
    lastUpdate = millis();

    // Random getal tussen 20.0°C en 25.0°C wordt gestuurt
    float simulatedTemp = 20.0 + (random(0, 50) / 10.0);

    // Stuurt de temperatuur naar de Zigbee netwerk
    zbTempSensor.setTemperature(simulatedTemp);

    Serial.printf("[TELEMETRY PUSH] Sent: %.1f °C (Next push in %lu sec)\n", 
                  simulatedTemp, REPORT_INTERVAL_MS / 1000);
  }
}