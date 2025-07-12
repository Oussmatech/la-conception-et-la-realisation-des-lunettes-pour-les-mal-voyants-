#include "esp_camera.h"
#include <WiFi.h>

// CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char* ssid = "ESP32_NET_pi";
const char* password = "12345678";
const char* host_ip = "192.168.4.1"; // IP du serveur (raspberry)

const int port = 5000;

WiFiClient client;
bool connected = false;

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Erreur init caméra : 0x%x\n", err);
    return;
  }
}

void setup() {
  Serial.begin(115200);
  setupCamera();
  sensor_t *s = esp_camera_sensor_get();
  s->set_vflip(s, 1);    // Retourner verticalement
  s->set_hmirror(s, 1);  // Effet miroir
  WiFi.begin(ssid, password);
  Serial.print("Connexion au WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnecté !");
  Serial.print("IP locale : ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Si non connecté, essayer de se connecter au serveur
  if (!connected) {
    Serial.println("Tentative de connexion au serveur...");
    if (client.connect(host_ip, port)) {
      Serial.println("Connecté au serveur !");
      connected = true;
    } else {
      Serial.println("Connexion au serveur échouée.");
      delay(1000);
      return;
    }
  }

  // Capturer une image
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Capture échouée");
    client.stop();
    connected = false;
    return;
  }

  // Vérifier si toujours connecté avant d’envoyer
  if (client.connected()) {
    uint32_t frameSize = fb->len;
    client.write((uint8_t*)&frameSize, sizeof(frameSize)); // Envoyer taille image
    client.write(fb->buf, fb->len);                        // Envoyer image
    Serial.println("Image envoyée !");
  } else {
    Serial.println("Connexion perdue !");
    client.stop();
    connected = false;
  }

  esp_camera_fb_return(fb);
  delay(100); // Attente entre les images
}
