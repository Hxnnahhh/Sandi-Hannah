from RPi import GPIO
from time import sleep

class BuzzerService:
    def __init__(self, pin: int) -> None:
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, 440)
        self._pwm.start(0)

    def play_tone(self, frequency: float, duration: float, duty: float) ->None:
        if frequency <= 0:
            self._pwm.ChangeDutyCycle(0)
            sleep(duration)
            return
        self._pwm.ChangeFrequency(frequency)
        self._pwm.ChangeDutyCycle(duty)
        sleep(duration)
        self._pwm.ChangeDutyCycle(0)

    def stop(self) -> None:
        self._pwm.stop()
        GPIO.output(self.pin, 0)
        GPIO.cleanup()
