from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

ledpin = 17

GPIO.setup(ledpin,GPIO.OUT)
hz = 1000
brightness = 50 #0-100
pwm_led1 = GPIO.PWM(ledpin, hz)
pwm_led1.start(brightness)

print('READY')
try:
    while True:
        pwm_led1.start(10)
        time.sleep(0.5)
        GPIO.output(ledpin, GPIO.LOW)
        time.sleep(0.5)
        pwm_led1.start(100)
        time.sleep(0.5)
        GPIO.output(ledpin, GPIO.LOW)
        time.sleep(0.5)
except KeyboardInterrupt:
    print('CTRL + C')
finally:
    GPIO.cleanup()
    print('STOP')
