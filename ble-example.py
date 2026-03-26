import RPi.GPIO as GPIO
from time import sleep
import smbus
import time
import threading
import queue
from ble import bluetooth_uart_server

GPIO.setmode(GPIO.BCM)

pins = (19,13,6,5)
btn_left = 20
btn_right = 21
GPIO.setup(pins, GPIO.OUT) 
GPIO.setup(btn_left, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(btn_right, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

steps = (
    (1,0,0,0), (1,1,0,0), (0,1,0,0), (0,1,1,0), 
    (0,0,1,0), (0,0,1,1), (0,0,0,1), (1,0,0,1)  
)

motoRPin1 = 14
motoRPin2 = 15
btn_toggle = 16
GPIO.setup([motoRPin1, motoRPin2], GPIO.OUT)
GPIO.setup(btn_toggle, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
dc_pwm_1 = GPIO.PWM(motoRPin1,1000) 
dc_pwm_1.start(0)
dc_pwm_2 = GPIO.PWM(motoRPin2,1000) 
dc_pwm_2.start(0)
current_state = 0

def switch_mode(channel):
    global current_state
    current_state = (current_state + 1) % 3
    print(f"New state: {current_state}")

GPIO.add_event_detect(btn_toggle, GPIO.RISING, callback=switch_mode, bouncetime=300)

servopin = 18
blue_btn = 26 
GPIO.setup(servopin, GPIO.OUT)
GPIO.setup(blue_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)