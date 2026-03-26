import RPi.GPIO as GPIO
from time import sleep
import smbus 

GPIO.setmode(GPIO.BCM)

servopin = 18
blue_btn = 26 

GPIO.setup(servopin, GPIO.OUT)
GPIO.setup(blue_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

servo_pwm = GPIO.PWM(servopin, 50)
servo_pwm.start(0)


i2c = smbus.SMBus(1)
ADC_addr = 0x48 

def read_adc(channel):
    command = 0x40 | channel
    i2c.write_byte(ADC_addr, command)
    i2c.read_byte(ADC_addr) 
    return i2c.read_byte(ADC_addr)

servo_on = False

def servo_button_changed(channel):
    global servo_on
    if GPIO.input(blue_btn) == 0:
        servo_on = not servo_on
        print(f"Servo motor: {'ON' if servo_on else 'OFF'}")

GPIO.add_event_detect(blue_btn, GPIO.FALLING, callback=servo_button_changed, bouncetime=200)

try:
    print("Use joystick")
    while True:
        if servo_on:
            analog_value_servo = read_adc(0) 
            servo_duty = (analog_value_servo / 255 * 10) + 2.5
            
            servo_pwm.ChangeDutyCycle(servo_duty)
        else:
            servo_pwm.ChangeDutyCycle(0) 
            
        sleep(0.1)

except KeyboardInterrupt:
    print("Cleanup")
finally:
    servo_pwm.stop()
    GPIO.cleanup()