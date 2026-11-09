import os

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
from ultralytics import YOLO
import time
import numpy as np
import torch
import serial
from pathlib import Path
from serial.tools import list_ports
import sys

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "Santa_Claus_Weight.pt"


def find_arduino_port():
    ports = list(list_ports.comports())
    keywords = ("arduino", "ch340", "cp210", "usb serial", "ttyacm", "ttyusb")

    for port in ports:
        text = f"{port.description} {port.manufacturer or ''} {port.device}".lower()
        if any(keyword in text for keyword in keywords):
            return port.device

    if sys.platform.startswith("win"):
        for port in ports:
            if port.device.upper().startswith("COM"):
                return port.device
    else:
        for port in ports:
            if "/ttyACM" in port.device or "/ttyUSB" in port.device:
                return port.device
    return None


def find_camera(max_cameras=10):
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera found: {index}")
                return cap
        cap.release()
    return None


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using: {DEVICE}")

# Arduino settings
ARDUINO_PORT = find_arduino_port()
BAUDRATE = 9600
SEND_INTERVAL = 0.05  # 20 Hz
last_seen_time = time.time()
last_send_time = 0

try:
    arduino = serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print(f"✅ Arduino connected on {ARDUINO_PORT}")
except Exception as e:
    print(f"❌ Failed to connect to Arduino: {e}")
    arduino = None

print("0. Program started")
t0 = time.time()

model = YOLO(str(MODEL_PATH))
model.to(DEVICE)

print(f"1. Model loaded in {time.time() - t0:.2f} sec")

torch.set_num_threads(4)

print("2. Warming up model...")
dummy = np.zeros((640, 640, 3), dtype=np.uint8)
t_warm = time.time()

model(dummy, imgsz=640, device=DEVICE, verbose=False)

print(f"3. Warm-up completed in {time.time() - t_warm:.2f} sec")

print("4. Opening camera")
cap = find_camera()

if cap == None or not cap.isOpened():
    print("❌ Failed to open webcam")
    exit(1)

CAM_WIDTH = cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
CAM_HEIGHT = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
CAM_FPS = cap.set(cv2.CAP_PROP_FPS, 90)

print(f"5. Camera opened. FPS: {CAM_FPS}"
      f"Width: {CAM_WIDTH}, Height: {CAM_HEIGHT}")
print("Press 'q' to exit")

# PID parameters
KP = 0.1
KI = 0.005
KD = 0.03
error_x = 0
error_y = 0
ALPHA = 0.2

DEAD_ZONE = 15

filtered_x = None
filtered_y = None
target_lost = True

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to get frame")
            break

        frame_height, frame_width, _ = frame.shape

        results = model(
            frame,
            imgsz=640,
            conf=0.5,
            device=DEVICE,
            verbose=False
        )
        result = results[0]

        if len(result.boxes) > 0:
            frame_center_x = frame_width / 2
            frame_center_y = frame_height / 2

            santa_boxes = []

            for box in result.boxes:
                class_index = int(box.cls[0])
                class_name = model.names[class_index]

                if class_name == "Santa":
                    santa_boxes.append(box)

            best_box = None
            min_distance = float("inf")

            for box in santa_boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                box_center_x = (x1 + x2) / 2
                box_center_y = (y1 + y2) / 2

                distance = (
                    (box_center_x - frame_center_x) ** 2 +
                    (box_center_y - frame_center_y) ** 2
                    ) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    best_box = box

            for box in santa_boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0].item()
                class_index = int(box.cls[0])
                class_name = model.names[class_index]

                if box is best_box:
                    if target_lost:
                        last_seen_time = time.time()
                        integral_x = 0
                        last_error_x = 0
                        integral_y = 0
                        last_error_y = 0
                        target_lost = False
                    else:
                        last_error_x = error_x
                        last_error_y = error_y

                    color = (0, 0, 255)

                    x_center = ((x1 + x2) / 2).item()
                    y_center = ((y1 + y2) / 2).item()

                    # EMA filtering
                    if filtered_x is None:
                        filtered_x = x_center
                        filtered_y = y_center
                    else:
                        filtered_x = ALPHA * filtered_x + (1 - ALPHA) * x_center
                        filtered_y = ALPHA * filtered_y + (1 - ALPHA) * y_center

                    # PID calculation
                    error_x = frame_center_x - filtered_x
                    error_y = frame_center_y - filtered_y

                    if abs(error_x) < DEAD_ZONE:
                        error_x = 0

                    if abs(error_y) < DEAD_ZONE:
                        error_y = 0

                    current_time = time.time()

                    dt = current_time - last_seen_time if current_time - last_seen_time > 0 else 0.0001
                    last_seen_time = time.time()

                    px = KP * error_x
                    py = KP * error_y

                    integral_x += error_x * dt
                    integral_y += error_y * dt

                    ix = KI * integral_x
                    iy = KI * integral_y

                    dx = KD * (error_x - last_error_x) / dt
                    dy = KD * (error_y - last_error_y) / dt

                    # P + I + D
                    servo_x = 90 + px + ix + dx
                    servo_y = 90 + py + iy + dy

                    # Clamp servo values to [0, 180]
                    servo_x = round(max(0, min(180, servo_x)), 2)
                    servo_y = round(max(0, min(180, servo_y)), 2)

                    if arduino:
                        current_time = time.time()
                        if current_time - last_send_time >= SEND_INTERVAL:
                            msg = f"{servo_x},{servo_y}\n"
                            print(f"Sending to Arduino: {msg.strip()}")
                            arduino.write(msg.encode())
                            last_send_time = current_time

                    label = f"TARGET {conf:.2f}"
                else:
                    color = (0, 255, 0)
                    label = f"Santa {conf:.2f}"

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
            if time.time() - last_seen_time < 0.2:
                print("Santa disappeared, waiting...")

            if arduino and not target_lost:
                print("Santa lost, timeout reached")
                target_lost = True
                arduino.write(b"90,90\n")

        cv2.imshow("YOLO Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if arduino:
                print("EXIT")
                arduino.write(b"90,90\n")
                time.sleep(0.2)
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()