"\"#include <Arduino.h>

#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         // https://github.com/tzapu/WiFiManager
#include <ESP8266mDNS.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

int    HTTP_PORT   = 8080;
String HTTP_METHOD = "POST"; // or "GET"
char   HOST_NAME[] = "192.168.1.53"; // hostname of web server:
String PATH_NAME   = "/";

// Set web server port number to 80
WiFiServer server(80);

// Variable to store the HTTP request
String header;

// Auxiliar variables to store the current output state
String output5State = "off";
String output4State = "off";

// Assign output variables to GPIO pins
const int output5 = 5;
const int output4 = 4;
WiFiManager wm;

//Your Domain name with URL path or IP address with path
const char* serverName = "http://192.168.1.53:8080/";
unsigned long lastTime = 0;
// Timer set to 10 minutes (600000)
//unsigned long timerDelay = 600000;
// Set timer to 5 seconds (5000)
unsigned long timerDelay = 1234;

void setup() {
  // put your setup code here, to run once:
  bool res;

  Serial.begin(115200);
  // Initialize the output variables as outputs
  pinMode(output5, OUTPUT);
  pinMode(output4, OUTPUT);
  // Set outputs to LOW
  digitalWrite(output5, LOW);
  digitalWrite(output4, LOW);

  //wm.startConfigPortal();
  //wifiManager.setConfigPortalBlocking(false); 
  // WiFiManager
  // Local intialization. Once its business is done, there is no need to keep it around
  //WiFiManager wifiManager;
  
  // Uncomment and run it once, if you want to erase all the stored information
  //wifiManager.resetSettings();
  
  // set custom ip for portal
  //wifiManager.setAPConfig(IPAddress(10,0,1,1), IPAddress(10,0,1,1), IPAddress(255,255,255,0));

  // fetches ssid and pass from eeprom and tries to connect
  // if it does not connect it starts an access point with the specified name
  // here  "AutoConnectAP"
  // and goes into a blocking loop awaiting configuration
  res = wm.autoConnect("AutoConnectAP");
      if(!res) {
        Serial.println("Failed to connect");
        // ESP.restart();
    } 
    else {
        //if you get here you have connected to the WiFi    
        Serial.println("connected...yeey :)");
    } 
  // or use this for auto generated name ESP + ChipID
  //wifiManager.autoConnect();

  // if you get here you have connected to the WiFi

  server.begin();
  
  if (MDNS.begin("myesp")) {  //Start mDNS
    Serial.println("MDNS started");
  } 
  else Serial.println("schiete");

  MDNS.addService("http", "tcp", 80);
}

void loop() {

 //Send an HTTP POST request every timerDelay
  if ((millis() - lastTime) > timerDelay) {
    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      WiFiClient client;
      HTTPClient http;
      
      // https://randomnerdtutorials.com/esp8266-nodemcu-http-get-post-arduino/
      // Your Domain name with URL path or IP address with path
      http.begin(client, serverName);
  
      // If you need Node-RED/server authentication, insert user and password below
      //http.setAuthorization("REPLACE_WITH_SERVER_USERNAME", "REPLACE_WITH_SERVER_PASSWORD");
  
      // Specify content-type header
      // If you need an HTTP request with a content type: application/json, use the following:
      http.addHeader("Content-Type", "application/json");
      // Data to send with HTTP POST
      //String httpRequestData = "{\"Host\": \"No-Name_E3_3C_13_D3\", \"IP\": \"192.168.1.48\", \"Type\": \"DS1820\", \"Version\": \"1.25\", \"Hardw\": \"NODEMCU\", \"Network\": \"janzneu\", \"MAC\": \"CC:50:E3:3C:13:D3\", \"AP-Name\": \"HOMAnet\", \"Hash\": \"0x627c7e\", \"Size\": \"0x118\", \"uptime\": \"354\"}";

      String httpRequestData =  "{\"name\": \"NODEMCU\", \"Method\": \"update\", \"ip\": \"127.0.1.1\", \"uptime\": \"" + String(millis()) + "\"" + ",\"hello\": \"world !!!\"}";
      // Send HTTP POST request
      int httpResponseCode = http.POST(httpRequestData);
      Serial.println(http.getString());
      //int httpResponseCode = http.POST("{\"api_key\":\"tPmAT5Ab3j7F9\",\"sensor\":\"BME280\",\"value1\":\"24.25\",\"value2\":\"49.54\",\"value3\":\"1005.14\"}");

      // If you need an HTTP request with a content type: text/plain
      //http.addHeader("Content-Type", "text/plain");
      //int httpResponseCode = http.POST("Hello, World!");
     
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
        
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}