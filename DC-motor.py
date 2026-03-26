import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

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

try:
    print("Press button")
    while True:
        speed = 50
        if current_state == 0: #off
            dc_pwm_1.ChangeDutyCycle(0)
            dc_pwm_2.ChangeDutyCycle(0)
        elif current_state == 1: #left
            dc_pwm_1.ChangeDutyCycle(speed)
            dc_pwm_2.ChangeDutyCycle(0)
        elif current_state == 2: #right
            dc_pwm_1.ChangeDutyCycle(0)
            dc_pwm_2.ChangeDutyCycle(speed)

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stop")

finally:
    dc_pwm_1.stop()
    dc_pwm_2.stop()
    GPIO.cleanup()


# time.sleep(3)


# dc_pwm_1. ChangeDutyCycle(0) 
# dc_pwm_2.ChangeDutyCycle(80)
# time.sleep(3)


# dc_pwm_1.ChangeDutyCycle(30)
# dc_pwm_2.ChangeDutyCycle(0) 
# time.sleep(3)

# dc_pwm_1.stop()
# dc_pwm_2.stop()
# del dc_pwm_1
# del dc_pwm_2
# GPIO.cleanup()
