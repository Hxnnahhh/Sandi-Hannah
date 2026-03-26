from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BCM)

pins = (19,13,6,5)
btn_left = 20
btn_right = 21

GPIO.setup(pins, GPIO. OUT) 
GPIO.setup(btn_left, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(btn_right, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


steps = (
    (1,0,0,0), # step 1
    (1,1,0,0), # step 2
    (0,1,0,0), # step 3
    (0,1,1,0), 
    (0,0,1,0), 
    (0,0,1,1), 
    (0,0,0,1), 
    (1,0,0,1)  
)

try:
    print("Hold red or blue button")
    while True:
        while GPIO.input(btn_left) == GPIO.LOW:
            print("test")
            for step in steps:
                for i in range(4):
                    GPIO.output(pins[i], step[i])
                    sleep(0.001)
        while GPIO.input(btn_right) == GPIO.LOW:
            for step in reversed(steps):
                for i in range(4):
                    GPIO.output(pins[i], step[i])
                    sleep(0.001)
    sleep(0.1)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()


# try:
#     for n in range(512):
#         for step in steps:
#             for i in range(4):
#                 GPIO.output(pins[i], step[i])

#             sleep(0.001) #Dictates how fast stepper motor will run
# # Turn once in the other direction
#     for n in range(512):
#         for step in steps:
#             for i in range(4):
#                 GPIO.output (pins[3-i], step[i]) # reverse
#             sleep(0.001) #Dictates how fast stepper motor will run

# # Once finished clean everything up
# except KeyboardInterrupt:
#     print ("cleanup")
#     GPIO.cleanup()
