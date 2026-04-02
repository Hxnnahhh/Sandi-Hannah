from RPi import GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)
buzzer_pin = 4
GPIO.setup(buzzer_pin, GPIO.OUT)
buzzer_pwm = GPIO.PWM(buzzer_pin, 200)
buzzer_pwm.start(50)
sleep(1)
buzzer_pwm.ChangeFrequency(300)
sleep(1)
buzzer_pwm.ChangeFrequency(400)
sleep(1)
buzzer_pwm.ChangeFrequency(500)
sleep(1)
buzzer_pwm.ChangeFrequency(600)
sleep(1)
buzzer_pwm.ChangeFrequency(700)
sleep(1)


buzzer_pwm.ChangeDutyCycle(0)
buzzer_pwm.stop()
GPIO.output(buzzer_pin, 0)
GPIO.cleanup()