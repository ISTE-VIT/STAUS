import cv2
import numpy as np
import board
import adafruit_mlx90614
import busio as io
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BOARD)
GPIO_TRIGGER=18
GPIO_ECHO=24
snitizer=11
GPIO.setup(sanitizer, GPIO.OUT)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)
led_pin=17
door =9
GPIO.setup(door,GPIO.OUT)
GPIO.setup(led_pin,GPIO.OUT)


def distance():
    GPIO.output(GPIO_TRIGGER,True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER,False)
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO)==0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO)==1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    Distance = (TimeElapsed*34300)/2
    return Distance

Distance = distance()

temp1 = 0
temp2 = 0
if Distance < 30:
    net = cv2.dnn.readNet('yolov3_training_last.weights', 'yolov3_testing.cfg')

    classes = []
    with open("classes.txt", "r") as f:
        classes = f.read().splitlines()

    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(100, 3))
    start_time=time.time()
    while int(time.time()-start_time)<15:
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
                    temp1=temp1+1
                color = colors[i]
                cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                cv2.putText(img, label + " " + confidence, (x, y+20), font, 2, (255,255,255), 2)
                

    cap.release()
    cv2.destroyAllWindows()

    i2c = io.I2C(board.SCL,board.SDA, frequency=100000)
    mlx=adafruit_mlx90614.MLX90614(i2c)
    obj_temp = mlx.object_temperature
    if obj_temp >=35 and obj_temp<=37:
        temp2=temp2+1

if temp1>0 and temp2==1:
    GPIO.output(led_pin,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(led_pin,GPIO.LOW)
    pwm= GPIO.PWM(sanitizer, 50)  
    pwm.start(0)
    pwm.ChangeDutyCycle(10)
    pwm.sleep(1)
    pwm.ChangeDutyCycle(7.5)
    pwm= GPIO.PWM(9, 50)  
    pwm.start(0)
    pwm.ChangeDutyCycle(5)
    pwm.sleep(1)
    pwm.ChangeDutyCycle(7.5)

    
    
    
    
    
    
    
