import RPi.GPIO as GPIO


class RGBLED:

    def __init__(self, r_pin: int, g_pin: int, b_pin: int, freq: int = 1000) -> None:
        self._pwms = []

        for pin in (r_pin, g_pin, b_pin):
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, freq)
            pwm.start(0)
            self._pwms.append(pwm)

    def set_rgb(self, r: float, g: float, b: float) -> None:
        for pwm, duty in zip(self._pwms, (r, g, b)):
            pwm.ChangeDutyCycle(max(0.0, min(100.0, duty)))

    def off(self) -> None:
        self.set_rgb(0, 0, 0)

    def stop(self) -> None:
        self.off()
        for pwm in self._pwms:
            pwm.stop()
