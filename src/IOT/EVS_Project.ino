
#include <WiFi.h>
#include <HTTPClient.h>

// -------------------- PIN SETUP --------------------
#define PH_PIN         34     // ADC1 required
#define TDS_PIN        35     // ADC1 required
#define TURBIDITY_PIN  32

// -------------------- GLOBAL SETTINGS --------------------
float ph_calibration_offset = 0.0;
const float TDS_VREF = 3.3;
const int TDS_SAMPLES = 30;


const char* ssid = "SSID";
const char* password = "password";

// -------------------- API --------------------
const char* apiURL = "https://evs-aquabytes.onrender.com/iot/register";
const char* DEVICE_ID = "ESP32_001";
const char* LOCATION  = "Rooftop Tank 1";
const float DO_VALUE  = 7.2;

// -------------------- READ pH --------------------
float readPh() {
  long sum = 0;

  for (int i = 0; i < 10; i++) {
    sum += analogRead(PH_PIN);
    delay(20);
  }

  int adcValue = sum / 10;
  float voltage = adcValue * (3.3 / 4095.0);
  float phValue = (3.5 * voltage) + ph_calibration_offset;
  return phValue;
}

// -------------------- READ TDS --------------------
float readTds() {
  int buffer[TDS_SAMPLES];

  for (int i = 0; i < TDS_SAMPLES; i++) {
    buffer[i] = analogRead(TDS_PIN);
    delay(40);
  }

  for (int i = 0; i < TDS_SAMPLES - 1; i++) {
    for (int j = i + 1; j < TDS_SAMPLES; j++) {
      if (buffer[i] > buffer[j]) {
        int temp = buffer[i];
        buffer[i] = buffer[j];
        buffer[j] = temp;
      }
    }
  }

  long avg = 0;
  for (int i = 10; i < 20; i++) {
    avg += buffer[i];
  }
  avg /= 10;

  float voltage = avg * (TDS_VREF / 4095.0);

  float tdsValue = (133.42 * voltage * voltage * voltage
                   - 255.86 * voltage * voltage
                   + 857.39 * voltage) * 0.5;

  return tdsValue;
}

// -------------------- READ TURBIDITY --------------------
float readTurbidity() {
  int raw = analogRead(TURBIDITY_PIN);
  return raw * (3.3 / 4095.0);
}

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
}

// -------------------- LOOP --------------------
void loop() {
  float ph = readPh();
  float tds = readTds();
  float turbidity = readTurbidity();

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
    json += "\"temperature\":24,";
    json += "\"turbidity\":" + String(turbidity, 2);
    json += "}";

    int code = http.POST(json);

    Serial.println(json);
    Serial.print("HTTP Code: ");
    Serial.println(code);
    Serial.println(http.getString());

    http.end();
  }

  delay(1500);
}

