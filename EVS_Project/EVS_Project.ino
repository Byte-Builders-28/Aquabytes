#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ---------- WiFi Credentials ----------
const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

// ---------- API URL ----------
String apiURL = "https://your-backend-url.com/api/data"; // change this

// ---------- Sensor Pins ----------
#define PH_PIN 34
#define TURBIDITY_PIN 35
#define TDS_PIN 32

#define ONE_WIRE_BUS 4
#define TRIG_PIN 12
#define ECHO_PIN 14

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ---------- Helper: Read Ultrasonic ----------
float getDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2;  
  return distance;
}

// ---------- Helper: Read pH ----------
float readPH() {
  int raw = analogRead(PH_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float ph = 7 + ((2.5 - voltage) * 3.5);   // basic linear formula
  return ph;
}

// ---------- Helper: Read Turbidity ----------
float readTurbidity() {
  int raw = analogRead(TURBIDITY_PIN);
  float voltage = raw * (3.3 / 4095.0);
  return voltage; // you can map to NTU if you have calibration
}

// ---------- Helper: Read TDS ----------
float readTDS() {
  int raw = analogRead(TDS_PIN);
  float voltage = raw * (3.3 / 4095.0);
  float tds = (voltage * 1000) / 2.3;  // rough formula
  return tds;
}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  sensors.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

// ---------- Loop ----------
void loop() {

  // --- READ ALL SENSOR VALUES ----
  float ph = readPH();
  float turbidity = readTurbidity();
  float tds = readTDS();

  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);

  float distance = getDistanceCM();

  Serial.println("---- SENSOR DATA ----");
  Serial.printf("pH: %.2f\n", ph);
  Serial.printf("Turbidity: %.2f V\n", turbidity);
  Serial.printf("TDS: %.2f ppm\n", tds);
  Serial.printf("Temperature: %.2f °C\n", temperature);
  Serial.printf("Distance: %.2f cm\n", distance);
  Serial.println("---------------------");

  // --- SEND DATA TO BACKEND ---
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(apiURL);
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";
    jsonData += "\"ph\":" + String(ph) + ",";
    jsonData += "\"turbidity\":" + String(turbidity) + ",";
    jsonData += "\"tds\":" + String(tds) + ",";
    jsonData += "\"temperature\":" + String(temperature) + ",";
    jsonData += "\"distance\":" + String(distance);
    jsonData += "}";

    int response = http.POST(jsonData);

    Serial.print("Server Response: ");
    Serial.println(response);

    String respData = http.getString();
    Serial.println(respData);

    http.end();
  }

  delay(5000);  // Send data every 5 seconds
}
