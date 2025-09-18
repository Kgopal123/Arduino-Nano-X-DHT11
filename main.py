import cv2
import numpy as np
import serial
import time
from tensorflow.keras.models import load_model

# Connect to Arduino Nano
ser = serial.Serial('COM3', 115200, timeout=1)  # change COM3 to your port
time.sleep(2)

# Load Teachable Machine model
model = load_model("keras_model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Preprocess frame
    img = cv2.resize(frame, (224, 224))
    img = np.expand_dims(img, axis=0) / 255.0

    # Predict
    prediction = model.predict(img)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence = prediction[0][index]

    cv2.putText(frame, f"{class_name} ({confidence*100:.2f}%)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Send command to Arduino
    if class_name.lower() == "plastic":
        ser.write(b"ON\n")
    else:
        ser.write(b"OFF\n")

    cv2.imshow("EcoSpark", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
