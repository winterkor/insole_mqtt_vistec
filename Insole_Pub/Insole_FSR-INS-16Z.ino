//This code is for connecting Insole with central com in VISTEC-GAIT and sending message in JSON file via MQTT protocol.
#include <WiFi.h>
#include <PubSubClient.h>
#include <cstdint>
#include <ArduinoJson.h>
#include <time.h>

//WiFi name and password
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

//MQTT server and port
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
const int port = 1883;

//Client Setup
WiFiClient espClient;//Creates a client that can connect to to a specified internet IP address and port as defined in client.connect()
PubSubClient client(espClient);//Creates a partially initialised client instance

//Used PIN in ESP32
const int ADC_PIN = 32;
const int S0 = 18;
const int S1 = 5;
const int S2 = 19;
const int S3 = 2;

//Limit message sent
uint32_t message_count = 1;
const uint32_t MESSAGE_LIMIT = 360000;

void setup() {
  Serial.begin(115200);//Initializes serial communication
  setup_wifi();//setup WiFi
  pinMode(ADC_PIN,INPUT);//Set this pin as input
  pinMode(S0,OUTPUT);//Set this pin as output
  pinMode(S1,OUTPUT);
  pinMode(S2,OUTPUT);
  pinMode(S3,OUTPUT);
  client.setServer(mqtt_server, port);
  client.setKeepAlive(60);//Sets the keep alive interval used by the client
  configTime(7*3600, 0, "pool.ntp.org"); //Configures the NTP server
  Serial.println("Waiting for time synchronization...");
  delay(1000);
  Serial.println("Time synchronized!");
}

void setup_wifi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);//Initializes the WiFi library’s network settings and provides the current status.
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) { // 10 seconds timeout if WiFi is not connected
    Serial.print(".");
  }
  //Check WiFi connection status
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed!");
  }
}//Setup WiFi

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}//Reconnect to MQTT server if it isn't

void selectMuxChannel(int channel) {
  // Set the state of control pins based on the channel number
  digitalWrite(S0, channel & 0x01);
  digitalWrite(S1, (channel >> 1) & 0x01);
  digitalWrite(S2, (channel >> 2) & 0x01);
  digitalWrite(S3, (channel >> 3) & 0x01);
}//Function to switch the channel of MUX

void loop() {
  //The time that program starts
  double dt = 10.0 * 1000; // delay time = 10 ms
  unsigned long start = micros();
  printf("%d\n",start);

  if (message_count > MESSAGE_LIMIT) {
    return;
  }//Check if it reach the limited message

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, reconnecting...");
    setup();
  }//Check that WiFi status in loop

  if (!client.connected()) {
    Serial.println("MQTT client not connected, reconnecting...");
    reconnect();
  }//Check MQTT connection in loop
  client.loop();
  
  //Time for publishing
  unsigned long now = micros();
  double pub_time = now/1000000.00;

  //Collect the data from insole sensor
  int values1[16];
  for (int i = 0; i < 16; i++) {
    selectMuxChannel(i);
    delayMicroseconds(200);
    values1[i] = analogRead(ADC_PIN);
    // printf("%d:%d ",i,values1[i]);
  }
  // printf("\n");
  
  //JSON message file creation
  //JSON file will look like this {"count": 1, "ts":1xxxxxxxxx, "data": [4027,0,0,...,27]},...
  char jsonBuffer[512];
  // sprintf(jsonBuffer, "{\"count\": %lu, \"ts\": \"%jd\", \"data\": [", message_count++, (intmax_t)now);
  sprintf(jsonBuffer, "[");
  for (int i = 0; i < 16; i++) {
    char dataBuffer[16];
    sprintf(dataBuffer, "%d", values1[i]);
    strcat(jsonBuffer, dataBuffer);
    if (i < 15) {
      strcat(jsonBuffer, ", ");
    }
  }
  char additionalBuffer[64];
  sprintf(additionalBuffer, ", %.6lf, %lu", pub_time, message_count++);
  strcat(jsonBuffer, additionalBuffer);
  strcat(jsonBuffer, "]");

  //MQTT publishing
  client.publish("data/json", jsonBuffer);
  Serial.println("Message published successfully");
  Serial.println(jsonBuffer);

  //Stable time delay
  unsigned long end = micros();
  double elapsed = (end - start);
  double t = dt - elapsed;
  if (t > 0) {
    delayMicroseconds(t);
  }
}