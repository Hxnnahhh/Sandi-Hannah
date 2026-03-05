import smbus
from RPI import GPIO
import time

GPIO.setmode(GPIO.BCM)
I2c = smbus.SMBus(1)


ADC_addr = 0x48

try:
    while True:
        i2c.write_byte(ADC_addr, 0b1001_0100)
        analog_value - i2c.read_byte(ADC_addr)

        print("Channel 2 has a value of:{} and in volt this is: {}".format(analog_value, analog_value / 255 * 3.3))
        time.sleep(1)
except KeyboardInterrupt as e:
    pass
finally:
    i2c.close()
    del i2c
    GPIO.cleanup()
