import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2
from ultralytics import YOLO
import time
import numpy as np
import torch
import serial
import serial.tools.list_ports
from pathlib import Path
from serial.tools import list_ports
import sys


<<<<<<< Updated upstream
def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        description = port.description.lower()
        if port.vid == 0x2341:  # Arduino VID
            print(f"✅ Arduino found on: {port.device}")
            return port.device
    return None

def connect_arduino(arduino_port, baudrate):
    try:
        arduino = serial.Serial(arduino_port, baudrate, timeout=1)
        time.sleep(2)
        print(f"✅ Arduino connected on {arduino_port}")
        return arduino
    except Exception as e:
        print(f"❌ Failed to connect to Arduino: {e}")
        return None
    
def send_arduino(arduino, msg, arduino_port, baudrate):
    try:
        arduino.write(msg)
        print(f"📡 Sent to Arduino: {msg.decode().strip()}")
    except serial.SerialException:
        arduino = connect_arduino(arduino_port, baudrate)
    return arduino

# ------------------------ DEVICE (CUDA / ROCm / CPU) ------------------------
=======
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


# DEVICE
>>>>>>> Stashed changes
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using: {device}")

# PATHS
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "Santa_Claus_Weight.pt"
assert MODEL_PATH.exists(), f"❌ Model not found: {MODEL_PATH}"

<<<<<<< Updated upstream
# ------------------------ ARDUINO SETTINGS ------------------------
arduino_port = find_arduino()
baudrate = 9600 # Make sure, that baudrate in arduino script is the same
last_seen_time = time.time()
reset_send = False
SEND_INTERVAL = 0.05  # 50ms = max 20 commands/second, to avoid overwhelming the Arduino
=======
# ARDUINO SETTINGS
arduino_port = find_arduino_port()
baudrate = 115200
last_seen_time = time.time()
SEND_INTERVAL = 0.05  # 20 Hz
>>>>>>> Stashed changes
last_send_time = 0

arduino=connect_arduino(arduino_port, baudrate)
arduino=send_arduino(arduino, b"90,90\n", arduino_port, baudrate) # Send 90, 90 to servos (Full stop)

# MODEL LOADING
print("0. Program started")
t0 = time.time()

model = YOLO(str(MODEL_PATH))
model.to(device)

print(f"1. Model loaded in {time.time() - t0:.2f} sec")

torch.set_num_threads(4)

print("2. Warming up model...")
dummy = np.zeros((640, 640, 3), dtype=np.uint8)
t_warm = time.time()

model(dummy, imgsz=640, device=device, verbose=False)

print(f"3. Warm-up completed in {time.time() - t_warm:.2f} sec")

# CAMERA
print("4. Opening camera")
<<<<<<< Updated upstream
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G')) # Must be set before FPS and resolution
cap.set(cv2.CAP_PROP_FPS, 90) # FPS of the camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) # Resolution X-Axis
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200) # Resolution Y-Axis
=======

cap = find_camera()
>>>>>>> Stashed changes

if not cap.isOpened():
    print("❌ Failed to open webcam")
    exit()

<<<<<<< Updated upstream
actual_fps = cap.get(cv2.CAP_PROP_FPS)
actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Actual settings: {actual_width}x{actual_height} @ {actual_fps}fps")

print("5. Camera opened")
=======
width = cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
height = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
fps = cap.set(cv2.CAP_PROP_FPS, 90)

print(f"5. Camera opened. FPS: {fps}, Width: {width}, Height: {height}")
>>>>>>> Stashed changes
print("Press 'q' to exit")

# PID-Paramenters
Kp = 0.1
Ki = 0.005
Kd = 0.03
error_x=0
error_y=0
alpha=0.2

Dead_Zone=15

# Some Stuff

filtered_x = None
filtered_y = None
Target_Lost=True

# MAIN
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
            device=device,
            verbose=False
        )
        result = results[0]

        if len(result.boxes) > 0:

            frame_center_x = frame_width / 2
            frame_center_y = frame_height / 2

            santa_boxes = []
            other_boxes = []

<<<<<<< Updated upstream
            for box in result.boxes: # Filtering classes
                cls_idx = int(box.cls[0])
                cls_name = model.names[cls_idx]
=======
            for box in result.boxes:
                class_index = int(box.cls[0])
                class_name = model.names[class_index]
>>>>>>> Stashed changes

                if class_name == "Santa":
                    santa_boxes.append(box)
                else:
                    other_boxes.append(box)

            best_box = None
            min_distance = float("inf")

            for box in santa_boxes: # Finding the most centered Santa
                x1, y1, x2, y2 = box.xyxy[0]
                box_center_x = (x1 + x2) / 2
                box_center_y = (y1 + y2) / 2

                distance = ((box_center_x - frame_center_x) ** 2 +
                            (box_center_y - frame_center_y) ** 2) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    best_box = box

            for box in santa_boxes: # Draw all Santa-Boxes
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0].item()
<<<<<<< Updated upstream

                if box is best_box: # Aiming at the most centered Santa
                    last_seen_time = time.time()
                    reset_send = False
=======
                class_index = int(box.cls[0])
                class_name = model.names[class_index]

                if box is best_box:
                    if Target_Lost:
                        last_seen_time = time.time()
                        integral_x = 0
                        last_error_x = 0
                        integral_y = 0
                        last_error_y = 0
                        Target_Lost=False
                    else:
                        last_error_x=error_x
                        last_error_y=error_y

>>>>>>> Stashed changes
                    color = (0, 0, 255)

                    x_center = ((x1 + x2) / 2).item()
                    y_center = ((y1 + y2) / 2).item()

                    if filtered_x is None:
                        filtered_x = x_center
                        filtered_y = y_center
                    else:
                        filtered_x = alpha * filtered_x + (1 - alpha) * x_center
                        filtered_y = alpha * filtered_y + (1 - alpha) * y_center

<<<<<<< Updated upstream
                    servo_x = max(50, min(130, servo_x)) # To make sure that
                    servo_y = max(50, min(130, servo_y)) # servos get command 0-180
=======
                    error_x=frame_center_x-filtered_x
                    error_y=frame_center_y-filtered_y

                    # DEAD ZONE
                    if abs(error_x) < Dead_Zone:
                        error_x = 0

                    if abs(error_y) < Dead_Zone:
                        error_y = 0

                    current_time=time.time()

                    dt=current_time-last_seen_time if current_time-last_seen_time>0 else 0.0001
                    last_seen_time = time.time()

                    Px=Kp*error_x
                    Py=Kp*error_y

                    integral_x+=error_x*dt
                    integral_y+=error_y*dt

                    Ix=Ki*integral_x
                    Iy=Ki*integral_y

                    Dx=Kd*(error_x-last_error_x)/dt
                    Dy=Kd*(error_y-last_error_y)/dt

                    servo_x=90+Px+Ix+Dx
                    servo_y=90+Py+Iy+Dy

                    servo_x = round(max(0, min(180, servo_x)), 2)
                    servo_y = round(max(0, min(180, servo_y)), 2)

                    if arduino:
                        current_time = time.time()

                        if current_time - last_send_time >= SEND_INTERVAL:
                            msg = f"{servo_x},{servo_y}\n"
                            print(f"Sending to Arduino: {msg.strip()}")
                            arduino.write(msg.encode())
                            last_send_time = current_time
>>>>>>> Stashed changes

                    if arduino and (time.time() - last_send_time >= SEND_INTERVAL):
                        arduino=send_arduino(arduino, f"{servo_x},{servo_y}\n".encode(), arduino_port, baudrate)
                        last_send_time = time.time()
                    label = f"TARGET {conf:.2f}"

                else:
                    color = (0, 255, 0)
                    label = f"Santa {conf:.2f}"

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
<<<<<<< Updated upstream
            if time.time() - last_seen_time < 0.5: # If santa wasn't found for 0.5 seconds
                print("Santa disappeared, still waiting...")
            elif arduino and not reset_send:
                arduino=send_arduino(arduino, b"90,90\n", arduino_port, baudrate) # Send 90, 90 to servos (Full stop)
                reset_send=True
=======
            if time.time() - last_seen_time < 0.2:
                print("Santa disappeared, waiting...")

            if arduino and not Target_Lost:
                print("Santa lost, timeout reached")
                Target_Lost=True
                arduino.write(b"90,90\n")
>>>>>>> Stashed changes

        cv2.imshow("YOLO Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if arduino:
<<<<<<< Updated upstream
                print("STOP")
                arduino=send_arduino(arduino, b"90,90\n", arduino_port, baudrate) # Send 90, 90 to servos (Full stop)
=======
                print("EXIT")
                arduino.write(b"90,90\n")
                time.sleep(0.2)
>>>>>>> Stashed changes
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()