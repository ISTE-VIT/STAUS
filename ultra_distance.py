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

    

while (True):
    servo.angle = 90
    sleep(2)
    servo.angle = 0
    sleep(2)
    servo.angle = -90
    sleep(2)
    break

    
