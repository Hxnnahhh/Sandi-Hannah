from RPi import GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
buzzer_pin = 12
GPIO.setup(buzzer_pin, GPIO.OUT)
buzzer_pwm = GPIO.PWM(buzzer_pin, 200)
buzzer_pwm.start(10)
sleep(3)
buzzer_pwm.ChangeDutyCycle(80)
sleep(3)
buzzer_pwm.ChangeFrequency(1000)
sleep(3)
buzzer_pwm.ChangeDutyCycle(0)
buzzer_pwm.stop()
GPIO.output(buzzer_pin, 0) 
GPIO.cleanup()