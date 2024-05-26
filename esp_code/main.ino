#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <MQUnifiedsensor.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>

const int buzzerPin = 14;
const int mq2Pin = 15;
const int smokeThreshold = 500;
const int gasThreshold = 500;

MQUnifiedsensor MQ2("ESP32", 3.3, 4096, mq2Pin, "MQ-2");

WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);

  MQ2.setRegressionMethod(1); //_PPM =  a*ratio^b
  MQ2.setA(605.18); MQ2.setB(-3.937); // Это параметры для определения концентрации CO
  MQ2.init();

  WiFiManager wifiManager;

  wifiManager.setConfigPortalTimeout(180);

  wifiManager.autoConnect("ESP32_AP", "12345678");

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect and hit timeout");
    ESP.restart();
  }

  sendMACAddress();

  server.on("/", handleRoot);
  server.begin();

  Serial.println("Connected to Wi-Fi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  server.handleClient();

  MQ2.update();

  float smokeLevel = MQ2.readSensor();
  float gasLevel = MQ2.readSensor();

  if (smokeLevel > smokeThreshold || gasLevel > gasThreshold) {
    digitalWrite(buzzerPin, HIGH);
  } else {
    digitalWrite(buzzerPin, LOW);
  }

  sendDataToServer(smokeLevel, gasLevel);
  delay(1000);
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP32 Wi-Fi Configuration</title></head><body>";
  html += "<h1>ESP32 Wi-Fi Configuration</h1>";
  html += "<form method='POST' action='/save'>SSID: <input type='text' name='ssid'><br>Password: <input type='password' name='password'><br><input type='submit' value='Save'></form>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void sendDataToServer(float smokeLevel, float gasLevel) {
  if (WiFi.status() == WL_CONNECTED) {
    DynamicJsonDocument doc(200);
    doc["mac_address"] = WiFi.macAddress();
    doc["smoke_level"] = smokeLevel;
    doc["gas_level"] = gasLevel;
    String jsonStr;
    serializeJson(doc, jsonStr);
    HTTPClient http;

    http.begin("http://<SERVER_IP>:<PORT>/data"); 
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonStr);
    if (httpResponseCode > 0) {
      Serial.print("Data sent to server successfully. Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending data to server. Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void sendMACAddress() {
  if (WiFi.status() == WL_CONNECTED) {
    String macAddress = WiFi.macAddress();
    DynamicJsonDocument doc(100);
    doc["mac_address"] = macAddress;
    String jsonStr;
    serializeJson(doc, jsonStr);
    HTTPClient http;

    http.begin("http://<SERVER_IP>:<PORT>/registration"); 
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonStr);
    if (httpResponseCode > 0) {
      Serial.print("MAC address sent to server successfully. Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error sending MAC address to server. Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}
