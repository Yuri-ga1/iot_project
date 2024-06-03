#include <WiFi.h>
#include <WebServer.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <MQ2Lib.h>

const int buzzerPin = 14;
const int mq2Pin = 34;

const float smokeThreshold = 500;
const float gasThreshold = 500;

MQ2 mq2(mq2Pin);

WebServer server(80);
WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "ESP32_AP";
const char* password = "12345678";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
String macAddress;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);

  mq2.begin();

  WiFi.softAP(ssid, password);

  server.on("/", handleRoot);
  server.on("/save", HTTP_POST, handleSave);
  server.begin();

  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  server.handleClient();

  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      reconnect();
    }
    client.loop();

    float smokeLevel = mq2.readSmoke();
    float gasLevel = mq2.readCO();

    if (isnan(smokeLevel) || isnan(gasLevel)) {
      Serial.println("Error: Sensor reading returned NaN");
      return; 
    }

    Serial.print("smoke: ");
    Serial.println(smokeLevel);
    Serial.print("gas: ");
    Serial.println(gasLevel);

    if (smokeLevel > smokeThreshold || gasLevel > gasThreshold) {
      digitalWrite(buzzerPin, HIGH);
    } else {
      digitalWrite(buzzerPin, LOW);
    }

    sendDataToMQTT(smokeLevel, gasLevel);
  }
  delay(1000);
}

void handleRoot() {
  macAddress = WiFi.macAddress();
  String html = "<!DOCTYPE html><html><head><title>ESP32 Wi-Fi Configuration</title></head><body>";
  html += "<h1>ESP32 Wi-Fi Configuration</h1>";
  html += "<form method='POST' action='/save'>";
  html += "SSID: <input type='text' name='ssid' required><br>";
  html += "Password: <input type='password' name='password' required><br>";
  html += "<input type='submit' value='Save'></form>";
  html += "<p>MAC Address: " + macAddress + "</p>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleSave() {
  if (server.hasArg("ssid") && server.hasArg("password")) {
    String ssid = server.arg("ssid");
    String password = server.arg("password");

    Serial.println("SSID: " + ssid);
    Serial.println("Password: " + password);

    WiFi.begin(ssid.c_str(), password.c_str());
    if (WiFi.waitForConnectResult() == WL_CONNECTED) {
      Serial.println("Reconnected to Wi-Fi");
    } else {
      Serial.println("Failed to connect to Wi-Fi");
    }

    String response = "Data saved:<br>SSID: " + ssid + "<br>Password: " + password;
    response += "<br>MAC Address: " + macAddress;
    server.send(200, "text/html", response);
  } else {
    server.send(400, "text/html", "Invalid Request");
  }
}

void sendDataToMQTT(float smokeLevel, float gasLevel) {
  if (WiFi.status() == WL_CONNECTED) {
    DynamicJsonDocument doc(200);
    doc["smoke_level"] = smokeLevel;
    doc["gas_level"] = gasLevel;
    String jsonStr;
    serializeJson(doc, jsonStr);

    String topic = "detectors/" + macAddress;
    client.publish(topic.c_str(), jsonStr.c_str());
    Serial.println("Data sent to MQTT successfully.");
  } else {
    Serial.println("WiFi not connected");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(macAddress.c_str())) {
      Serial.println("connected");
      client.subscribe("detectors/#");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
