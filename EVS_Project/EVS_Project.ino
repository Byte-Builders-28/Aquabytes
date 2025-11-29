#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ---------- WiFi ----------
const char* ssid = "TIG-Works";
const char* password = "03577533";

// ---------- API ----------
const char* apiURL = "https://evs-aquabytes.onrender.com/iot/register";

// ---------- Fixed Values ----------
const char* DEVICE_ID = "ESP32_001";
const char* LOCATION  = "Rooftop Tank 1";
const float DO_VALUE  = 7.2;
  
// ---------- Pins ----------
#define PH_PIN         34
#define TURBIDITY_PIN  35
#define TDS_PIN        32
#define ONE_WIRE_BUS   26

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ---------- Sensor Functions ----------
float readPH() {
  int raw = analogRead(PH_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float ph = 7 + ((2.5 - voltage) * 3.5);   // simple calibration
  return ph;
}

float readTurbidity() {
  int raw = analogRead(TURBIDITY_PIN);
  float voltage = raw * (3.3 / 4095.0);
  return voltage;
}

float readTDS() {
  int raw = analogRead(TDS_PIN);
  float voltage = raw * (3.3 / 4095.0);
  return (voltage * 1000) / 2.3;
}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);
  sensors.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
}

// ---------- Loop ----------
void loop() {

  float ph         = readPH();
  float turbidity = readTurbidity();
  float tds        = readTDS();

  sensors.requestTemperatures();
  float temperature = 20;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(apiURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    json += "\"do\":" + String(DO_VALUE) + ",";
    json += "\"location\":\"" + String(LOCATION) + "\",";
    json += "\"ph\":" + String(ph, 2) + ",";
    json += "\"tds\":" + String(tds, 1) + ",";
    json += "\"temperature\":" + String(temperature, 1) + ",";
    json += "\"turbidity\":" + String(turbidity, 2);
    json += "}";

    int code = http.POST(json);

    Serial.println(json);
    Serial.print("HTTP Code: ");
    Serial.println(code);
    Serial.println(http.getString());

    http.end();
  }

  delay(1000);
}
