import cv2
import numpy as np
import picamera
import RPi.GPIO as GPIO
import time
from gpiozero import AngularServo
from time import sleep


servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
trig=21
echo=20
GPIO.setmode(GPIO.BCM)

#Runs until there is an object within 25cm
while True:
    print('Distance measurement in progress')
    GPIO.setup(trig,GPIO.OUT)
    GPIO.setup(echo,GPIO.IN)
    GPIO.output(trig,False)
    print('waiting for sensor to settle')
    time.sleep(0.2)
    GPIO.output(trig,True)
    time.sleep(0.00001)
    GPIO.output(trig,False)
    while GPIO.input(echo)==0:
        pulse_start=time.time()
    while GPIO.input(echo)==1:
        pulse_end=time.time()
    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17150
    distance=round(distance,2)
    print("Distance:",distance,'cm')
    time.sleep(2)
    if distance <=25:
        break

temp1=0
if distance<=25:
    
    net = cv2.dnn.readNet('yolov3_training_last.weights', 'yolov3_testing.cfg')

    classes = []
    with open("classes.txt", "r") as f:
        classes = f.read().splitlines()

    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(100, 3))
    start_time=time.time()
    while int(time.time() - start_time) < 15:
        ret, frame=cap.read()
        if ret:
            assert not isinstance(frame,type(None)),'frame not found'
        _, img = cap.read()
        height, width, _ = img.shape

        blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)

                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)

        if len(indexes)>0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = str(round(confidences[i],2))
                if label.lower() == "wearing mask":
                    temp1 = temp1+1
                color = colors[i]
                cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                cv2.putText(img, label + " " + confidence, (x, y+20), font, 2, (255,255,255), 2)

        cv2.imshow('Image', img)
        #key = cv2.waitKey(1)
        #if key==27:
         #   break

    cap.release()
    cv2.destroyAllWindows()


if temp1>0:
    while (True):
        servo.angle = 90
        sleep(2)
        servo.angle = 0
        sleep(2)
        servo.angle = -90
        sleep(2)
        break


    
