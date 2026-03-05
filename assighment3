from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

pins = [16,20,21,26]
ledpin = 17
states = [False]*4
prevstates = [True]*4
GPIO.setup(ledpin,GPIO.OUT)
for pin in (pins):
    GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
value = 0
GPIO.output(ledpin, GPIO.HIGH)  
def blinking(hz):
    if hz == 0:
        pass
    else:
        time.sleep(1/(hz*2))
        GPIO.output(ledpin, GPIO.LOW)

        time.sleep(1/(hz*2))
        GPIO.output(ledpin, GPIO.HIGH)   

print('READY')
try:
    while True:
        for pin in (pins):
            pressed = not GPIO.input(pin)
            # print(pin , pressed)
            states[pins.index(pin)] = pressed
        
        if states != prevstates:
            value = 0
            for pin in (pins):
                if states[pins.index(pin)] == True:
                    value += 2**pins.index(pin)
            
            pins_output='Pins: '
            for i in range(len(pins)):
        
                pins_output+= str(int(states[i*-1-1])) + ' '
            print(pins_output)
            print(f"Decimal Value: {value}\n ")
        blinking(value)
        prevstates = states.copy()
        time.sleep(0.01)
except KeyboardInterrupt:
    print('CTRL + C')
finally:
    GPIO.cleanup()
    print('STOP')
