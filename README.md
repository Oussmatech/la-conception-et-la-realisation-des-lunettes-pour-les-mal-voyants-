# la-conception-et-la-realisation-des-lunettes-pour-les-mal-voyants-

Description
Ce projet implémente un système de lunettes intelligentes destiné aux personnes malvoyantes. À l'aide de deux caméras ESP32-CAM montées sur une monture, d'un Raspberry Pi 4 et un buzzer pour le traitement
Système portable autonome et léger à intégrer dans des lunettes
Détection par yolo
Estimation de la distance grâce à la vision stéréoscopique.
Alerte sonore adaptée à la proximité de l’obstacle.
fonctionnement au demmarage du raspberry

le dispositif :
Acquiert des images stéréo en temps réel
Utilise un modèle YOLOv8 pour détecter les obstacles
Calcule la profondeur par stéréovision (disparité)
Émet une alerte sonore via un buzzer dont la fréquence varie en fonction de la distance à l’obstacle

L’objectif est de signaler à la personne malvoyante la présence et la proximité des objets autour d’elle, de manière autonome et portable.

Fonctionnalités :
Capture stéréo : deux flux video via ESP32-CAM
Détection d’obstacles : YOLOv8 (poids yolov8n.pt) pour la classification et localisation
Estimation de distance : méthode pinhole + stéréovision parallèlement calibrées
Alerte sonore : mapping distance → fréquence (8000 Hz à 1000 Hz) pendant 1 s
Connexion Wi‑Fi : auto-connexion au hotspot Raspberry Pi via nmcli


Matériel Requis
Raspberry Pi 4 
2 × ESP32-CAM modules
Buzzer passif (GPIO PIN configurable)
Alimentation 5V stable
