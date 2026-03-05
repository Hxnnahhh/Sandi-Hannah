import smbus
from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)
i2c = smbus.SMBus(1)
ADC_addr = 0x48


BLUE_PIN = 13
RED_PIN = 5
GREEN_PIN = 6
BUTTON_PIN = 18 


GPIO.setup([BLUE_PIN, RED_PIN, GREEN_PIN], GPIO.OUT)
pwm_b = GPIO.PWM(BLUE_PIN, 1000)
pwm_r = GPIO.PWM(RED_PIN, 1000)
pwm_g = GPIO.PWM(GREEN_PIN, 1000)


pwm_b.start(100)
pwm_r.start(100)
pwm_g.start(100)


GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
system_active = True

def toggle_system(channel):
    global system_active
    system_active = not system_active
    print("System status: {}".format("ACTIVE" if system_active else "OFF"))

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=300)

print("I hope it works now, spin it")

try:
    while True:
        if system_active:
            i2c.write_byte(ADC_addr, 0b1001_0100) 
            val_b = i2c.read_byte(ADC_addr)
            
            i2c.write_byte(ADC_addr, 0b1101_0100) 
            val_r = i2c.read_byte(ADC_addr)
            
            i2c.write_byte(ADC_addr, 0b1010_0100) 
            val_g = i2c.read_byte(ADC_addr)

            dc_b = 100 - (val_b / 255 * 100)
            dc_r = 100 - (val_r / 255 * 100)
            dc_g = 100 - (val_g / 255 * 100)

            
            pwm_b.ChangeDutyCycle(dc_b)
            pwm_r.ChangeDutyCycle(dc_r)
            pwm_g.ChangeDutyCycle(dc_g)

            
            print("R: {:3} | G: {:3} | B: {:3}".format(val_r, val_g, val_b))
        else:
            
            pwm_b.ChangeDutyCycle(100)
            pwm_r.ChangeDutyCycle(100)
            pwm_g.ChangeDutyCycle(100)

        time.sleep(0.2) 

except KeyboardInterrupt:
    print("stoppppp")
finally:
    i2c.close()
    GPIO.cleanup()

