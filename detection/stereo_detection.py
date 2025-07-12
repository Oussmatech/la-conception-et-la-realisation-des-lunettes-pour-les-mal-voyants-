import socket
import struct
import threading
import numpy as np
import cv2
import time
import gc
from ultralytics import YOLO
import torch
import scipy.optimize
from concurrent.futures import ThreadPoolExecutor
import RPi.GPIO as GPIO


BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer = GPIO.PWM(BUZZER_PIN, 1000)

def sound_buzzer(distance_cm):
    d_min = 10.0
    d_max = 100.0
    f_max = 8000.0
    f_min = 1000.0
    d = max(min(distance_cm, d_max), d_min)
    freq = f_max + (f_min - f_max) * ((d - d_min) / (d_max - d_min))
    buzzer.ChangeFrequency(freq)
    buzzer.start(50)  # Duty cycle à 50%
    time.sleep(1)
    buzzer.stop()

# --- Fonctions utilitaires pour YOLOv8 ---
def get_detections(model, imgs_rgb):
    dets = []
    labels = []
    results = model(imgs_rgb, verbose=False)
    for r in results:
        if r.boxes is None or len(r.boxes) == 0:
            dets.append(np.empty((0, 4)))
            labels.append(np.array([]))
        else:
            boxes = r.boxes.xyxy.cpu().numpy()
            lbls = r.boxes.cls.cpu().numpy().astype(int)
            dets.append(boxes)
            labels.append(lbls)
    return dets, labels

# --- Autres fonctions stéréo ---
from stereo_image_utils_yolo import (
    get_cost, annotate_class2,
    get_horiz_dist_corner_tl, get_horiz_dist_corner_br,
    get_dist_to_centre_tl, get_dist_to_centre_br
)

# --- Initialisation du modèle YOLOv8 ---
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = YOLO('yolov8n.pt').to(device)
model.fuse()
names = model.model.names

# --- Paramètres de calibration stéréo ---
fl = 3.0159464965989997
tantheta = 0.5637724038254779

# --- Réseau TCP ---
HOST = '0.0.0.0'
PORT = 5000

frames_dict = {}
lock = threading.Lock()

def receive_frame(conn):
    try:
        conn.settimeout(5.0)
        frame_size_bytes = conn.recv(4)
        if not frame_size_bytes:
            return None
        frame_size = int.from_bytes(frame_size_bytes, byteorder='little')
        frame_data = bytearray()
        while len(frame_data) < frame_size:
            packet = conn.recv(min(4096, frame_size - len(frame_data)))
            if not packet:
                return None
            frame_data.extend(packet)
        img_array = np.frombuffer(frame_data, dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except socket.timeout:
        print("Réception expirée.")
        return None


def handle_stereo_clients(conn_l, addr_l, conn_r, addr_r):
    print(f"[+] Connexions établies : Gauche={addr_l[0]}, Droite={addr_r[0]}")
    last_detection_time = 0

    try:
        while True:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_l = executor.submit(receive_frame, conn_l)
                future_r = executor.submit(receive_frame, conn_r)
                frame_l = future_l.result()
                frame_r = future_r.result()

            if frame_l is None or frame_r is None:
                break

            current_time = time.time()
            if current_time - last_detection_time >= 1:
                last_detection_time = current_time

                imgs_rgb = [
                    cv2.resize(cv2.cvtColor(frame_l, cv2.COLOR_BGR2RGB), (320, 320)),
                    cv2.resize(cv2.cvtColor(frame_r, cv2.COLOR_BGR2RGB), (320, 320))
                ]

                det, lbls = get_detections(model, imgs_rgb)

                if det[0].shape[0] > 0 and det[1].shape[0] > 0:
                    sz1 = 320
                    centre = sz1 / 2

                    cost = get_cost(det, lbls=lbls, sz1=centre)
                    tracks = scipy.optimize.linear_sum_assignment(cost)

                    dists_tl = get_horiz_dist_corner_tl(det)
                    dists_br = get_horiz_dist_corner_br(det)

                    final_dists = []
                    dctl = get_dist_to_centre_tl(det[0], cntr=centre)
                    dcbr = get_dist_to_centre_br(det[0], cntr=centre)

                    for i, j in zip(*tracks):
                        if dctl[i] < dcbr[i]:
                            final_dists.append((dists_tl[i][j], names[lbls[0][i]]))
                        else:
                            final_dists.append((dists_br[i][j], names[lbls[0][i]]))

                    fd = [i for (i, _) in final_dists]
                    dists_away = (8.7 / 2) * sz1 * (1 / tantheta) / np.array(fd) + fl

                    for idx, dist in enumerate(dists_away):
                        class_name = names[lbls[0][tracks[0][idx]]]
                        print(f"{class_name} is {dist:.1f}cm away")
                        # Son du buzzer selon la distance détectée
                        sound_buzzer(dist)
                else:
                    print("No matching detections in both frames.")

                gc.collect()

    except Exception as e:
        print(f"[{addr_l[0]}_{addr_r[0]}] Erreur : {e}")
    finally:
        conn_l.close()
        conn_r.close()
        print(f"[{addr_l[0]}_{addr_r[0]}] Déconnectés")

# --- Démarrage du serveur TCP ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Serveur en écoute sur le port {PORT}...")

try:
    while True:
        print("Attente de la caméra gauche...")
        conn_l, addr_l = server_socket.accept()
        print("Attente de la caméra droite...")
        conn_r, addr_r = server_socket.accept()

        threading.Thread(
            target=handle_stereo_clients,
            args=(conn_l, addr_l, conn_r, addr_r),
            daemon=True
        ).start()

except KeyboardInterrupt:
    print("\nArrêt du serveur.")
finally:
    server_socket.close()
    GPIO.cleanup()