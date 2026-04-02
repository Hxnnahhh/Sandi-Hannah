import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

DS = 22
SHCP = 17
STCP = 27

def setup():
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([DS, SHCP, STCP], GPIO.OUT)
    GPIO.output(SHCP, 0)
    GPIO.output(STCP, 0)

def shiftClockPulse():
    GPIO.output(SHCP, 1)
    GPIO.output(SHCP, 0)

def storageClockPulse():
    GPIO.output(STCP, 1)
    time.sleep(0.001) 
    GPIO.output(STCP, 0)

def write_one_bit(bit):
    GPIO.output(DS, bit)
    shiftClockPulse()

def write_16_bits(value):
    for i in range(16):
        bit = (value >> i) & 1
        write_one_bit(bit)
    
    storageClockPulse()

def clear_all():
    write_16_bits(0)


setup()

try:
    print("Starting")
    while True:
        for i in range(11): 
            data = (1 << i) - 1
            write_16_bits(data)
            time.sleep(0.1)
        time.sleep(0.5)
        clear_all()
        time.sleep(0.5)

except KeyboardInterrupt:
    clear_all()
    GPIO.cleanup()
    print("\nProgramm Stopped")