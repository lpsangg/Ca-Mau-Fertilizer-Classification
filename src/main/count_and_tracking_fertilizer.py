import cv2
from sort import *
import math
import numpy as np
from ultralytics import YOLO
import cvzone

cap = cv2.VideoCapture("video_3.mp4")
model = YOLO('model_n.pt')
classnames = []
with open('class.txt', 'r') as f:
    classnames = f.read().splitlines()

tracker = Sort(max_age=20)

line1 = [0, 300, 1200, 300]
line2 = [0, 320, 1200, 320]

count_Urea_Bio_xanh = 0
count_NPK_22_5_6 = 0
count_Urea_hat_duc = 0

detected_objects = set()  # Set to track detected objects

while (cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture('Video_1.mov')
        continue
    frame = cv2.resize(frame, (288, 512))

    detections = np.empty((0, 5))
    results = model(frame, stream=1)

    for info in results:
        boxes = info.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            classindex = box.cls[0]
            conf = math.ceil(conf * 100)
            classindex = int(classindex)
            objectdetect = classnames[classindex]
            if objectdetect == 'Urea_Bio_xanh' or objectdetect == 'NPK_22-5-6' or objectdetect == 'Urea_hat_duc':
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                new_detections = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, new_detections))

    cv2.line(frame, (line1[0], line1[1]), (line1[2], line1[3]), (255, 0, 0), 2)
    cv2.line(frame, (line2[0], line2[1]), (line2[2], line2[3]), (255, 0, 0), 2)
    track_results = tracker.update(detections)

    for results in track_results:
        x1, y1, x2, y2, id = results
        x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2, y1 + h // 2

        if line1[1] <= cy <= line2[1] and line1[3] <= cy <= line2[3]:
            if id not in detected_objects:
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                if objectdetect == 'Urea_Bio_xanh':
                    count_Urea_Bio_xanh += 1
                elif objectdetect == 'NPK_22-5-6':
                    count_NPK_22_5_6 += 1
                elif objectdetect == 'Urea_hat_duc':
                    count_Urea_hat_duc += 1
                detected_objects.add(id)  # Add the ID to the set to mark as detected
        cvzone.putTextRect(frame, f'Urea_Bio_xanh ={count_Urea_Bio_xanh}', [0, 20], thickness=2, scale=1.5, border=1)
        cvzone.putTextRect(frame, f'NPK_22-5-6 ={count_NPK_22_5_6}', [0, 60], thickness=2, scale=1.5, border=1)
        cvzone.putTextRect(frame, f'Urea_hat_duc ={count_Urea_hat_duc}', [0, 100], thickness=2, scale=1.5, border=1)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cvzone.putTextRect(frame, f'{objectdetect} {conf}%', [x1 + 8, y1 - 12], thickness=2, scale=1)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

    cv2.imshow('frame', frame)
    cv2.waitKey(1)
