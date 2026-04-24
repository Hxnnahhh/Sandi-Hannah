import smbus
from RPi import GPIO
import time
import subprocess
import math

import lcd
import mpu
import joystick
import led
from ble import BleService

GPIO.setmode(GPIO.BCM)
i2c = smbus.SMBus(1)

# pin defs
JOY_BTN = 7
BTN_1 = 20
BTN_2 = 16
BTN_3 = 21
BTN_4 = 26

LED_R = 6
LED_G = 5
LED_B = 13

LCD_ADDR = 0x27

GPIO.setup(JOY_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup([BTN_1, BTN_2, BTN_3, BTN_4], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup([LED_R, LED_G, LED_B], GPIO.OUT)

pwm_r = GPIO.PWM(LED_R, 1000)
pwm_g = GPIO.PWM(LED_G, 1000)
pwm_b = GPIO.PWM(LED_B, 1000)
led.start_led(pwm_r, pwm_g, pwm_b)

clicks = 0

def joy_click(channel):
    global clicks
    clicks += 1
    print(f"Joystick clicked! count: {clicks}, screen: {clicks % 6 + 1}")

GPIO.add_event_detect(JOY_BTN, GPIO.FALLING, callback=joy_click, bouncetime=300)

lcd.LCD_init(i2c, LCD_ADDR)
mpu.mpu_setup(i2c)

ble = BleService()
ble.start()
last_ble_message = None

print("Starting main loop")

try:
    while True:
        screen = clicks % 6 + 1

        x = joystick.read_x(i2c)
        y = joystick.read_y(i2c)
        led.set_color(pwm_r, pwm_g, pwm_b, x, y)

        # screen 1 - ip addresses
        if screen == 1:
            ip_data = subprocess.check_output(["ip", "addr"], text=True)

            eth_ip = "N/A"
            wlan_ip = "N/A"
            curr_iface = ""

            for line in ip_data.splitlines():
                if "eth0" in line and not line.startswith(" "):
                    curr_iface = "eth0"
                elif "wlan0" in line and not line.startswith(" "):
                    curr_iface = "wlan0"
                elif "inet " in line and "inet6" not in line:
                    addr = line.strip().split()[1].split("/")[0]
                    if curr_iface == "eth0":
                        eth_ip = addr
                    elif curr_iface == "wlan0":
                        wlan_ip = addr

            lcd.LCD_write(i2c, LCD_ADDR, f"eth0:{eth_ip}", f"wlan:{wlan_ip}")

        # screen 2 - button binary/hex/decimal
        elif screen == 2:
            b1 = 0 if GPIO.input(BTN_1) == GPIO.LOW else 1  
            b2 = 0 if GPIO.input(BTN_2) == GPIO.LOW else 1
            b3 = 0 if GPIO.input(BTN_3) == GPIO.LOW else 1
            b4 = 0 if GPIO.input(BTN_4) == GPIO.LOW else 1

            number = b1 | b2 << 1 | b3 << 2 | b4 << 3

            line1 = f"{bin(number)} {hex(number)}"
            line2 = " " * (16 - len(str(number))) + str(number)
            lcd.LCD_write(i2c, LCD_ADDR, line1[:16], line2[:16])

        # screen 3 - joystick x bar
        elif screen == 3:
            bar_len = int((x / 255) * 16)
            bar = "=" * bar_len + " " * (16 - bar_len)
            lcd.LCD_write(i2c, LCD_ADDR, bar, f"VRX => {x}")

        # screen 4 - joystick y bar
        elif screen == 4:
            bar_len = int((y / 255) * 16)
            bar = "=" * bar_len + " " * (16 - bar_len)
            lcd.LCD_write(i2c, LCD_ADDR, bar, f"VRY => {y}")

        # screen 5 - accelerometer
        elif screen == 5:
            ax, ay, az = mpu.get_accel(i2c)
            c = mpu.combined(ax, ay, az)
            lcd.LCD_write(i2c, LCD_ADDR, f"X:{ax} Y:{ay}", f"Z:{az} C:{c}")

        # screen 6 - ble messages
        elif screen == 6:
            msg = ble.get_message()
            if msg is not None:
                last_ble_message = msg

            if last_ble_message is not None:
                lcd.LCD_write(
                    i2c,
                    LCD_ADDR,
                    last_ble_message[:16],
                    last_ble_message[16:32],
                )
            else:
                lcd.LCD_write(i2c, LCD_ADDR, "Send a message", "via BLE UART")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping...")
finally:
    pwm_r.stop()
    pwm_g.stop()
    pwm_b.stop()
    ble.stop()
    lcd.LCD_write(i2c, LCD_ADDR, "", "")
    GPIO.cleanup()
    i2c.close()
    print("Done")
