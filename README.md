# lunettes intelligentes pour les personnes aveugles

Ce projet vise a développée Des lunettes intelligentes dédiées aux personnes aveugles, Ces lunettes associent l’intelligence artificielle pour la détection de l’obstacle et la méthode de vision stéréoscopique pour calculer la distance à partir du flux vidéo de deux ESP32-CAM, puis envoyer  au Raspberry via WIFI qui assurer le traitement et ensuite alerter la personne concernée par les obstacles autour de lui et guider dans ses mouvements et le prévenir, via buzzer, Ce qui facilitera son déplacement aussi bien que son quotidien.

## Features
- Capture deux flux video via ESP32-CAM
- envoyer les flux video sur le resaux wifi via une socket TCP au raspberry pour le traitement
- Détection d’obstacles : YOLOv8 (poids yolov8n.pt) pour la classification et localisation.
- Estimation de la profondeur : par la méthode de la stéréovision
- Alerte sonore par rapport a la distance.
- fonctionnement automatique depuis autostart de la raspberry et auto-connexion au hotspot du Raspberry Pi
- cenception d'un model 3D 

## Matériel Requis :
- Raspberry Pi 4 (Raspbian / Ubuntu OS)
- 2 × ESP32-CAM modules
- Buzzer actif (GPIO PIN configurable)
- Câbles (GPIO, alimentation, caméra)
- 2 × Alimentation 5V (esp32cam I(A)>500mA , raspberry I(A) >2A) 

📁 la-conception-et-la-realisation-des-lunettes-pour-les-mal-voyants
 ├── 📂 detection    
      ├── stereo_detection.py
      ├── stereo_image_utils_yolo.py        # procedure de la vision stereoscopique 
      ├── yolov8n.pt        
 ├── 📂 calibration         # calcule des parametres de la relation de triangulation
      ├── stereo_calibration.ipynb
      ├── images 
 ├── 📂 esp_codes  
      ├── 📂 CameraWebServer # verificaion de flux camera et prend des images pour la calibration
      ├── Esp32cam_client.ino # envoyer flux video via socket TCP 
└── 📜 README.md

## 👥 Team Members
- **Oussama Bouftini**
- **Ayman EL Hasnaoui**

## 📌 Future Enhancements


## 📞 Contact
oussamabouftini@gmail.com
