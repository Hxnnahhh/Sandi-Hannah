import subprocess
import threading
import time
import RPi.GPIO as GPIO
from ads7830 import ADS7830
from ble_uart import BLEUARTServer
from lcd import LCD
from mpu6050 import MPU6050
from rgb_led import RGBLED

ADC_I2C_BUS = 1
ADC_I2C_ADDR = 0x48
ADC_CH_X = 5    
ADC_CH_Y = 6    

BTN_JOY = 7
BTN_PINS = [20, 16, 21, 26]   

LED_R = 6
LED_G = 5
LED_B = 13

LCD_I2C_BUS = 1
LCD_I2C_ADDR = 0x27

MPU_I2C_BUS = 1
MPU_I2C_ADDR = 0x68

ADC_MAX = 255

_lock = threading.Lock()
_press_count = 0
_current_screen = 0
NUM_SCREENS = 6
_last_nibble = -1



def _joy_button_callback(_channel):
    global _press_count, _current_screen
    with _lock:
        _press_count += 1
        _current_screen = (_current_screen + 1) % NUM_SCREENS
        count = _press_count
    print(f"The joystick has been pressed {count} times!")


def _parse_ip(text: str, iface: str) -> str:
    in_iface = False
    for line in text.splitlines():
        if not line.startswith((" ", "\t")) and iface in line:
            in_iface = True
        if in_iface and "inet " in line and "inet6" not in line:
            return line.split()[1].split("/")[0]
    return "N/A"


def update_screen1(lcd: LCD) -> None:
    output = subprocess.check_output(["ip", "a"], text=True)
    eth0_ip = _parse_ip(output, "eth0")
    wlan0_ip = _parse_ip(output, "wlan0")
    lcd.show_two_lines(f"eth0: {eth0_ip}", f"wlan0:{wlan0_ip}")


def update_screen2(lcd: LCD) -> None:
    global _last_nibble
    nibble = 0
    for index, pin in enumerate(BTN_PINS):
        if GPIO.input(pin) == GPIO.LOW:
            nibble |= 1 << index

    if nibble == _last_nibble:
        return
    _last_nibble = nibble

    lcd.show_two_lines(f"{bin(nibble):<8}{hex(nibble):>8}", f"{nibble:>16}")


def _make_bar(value: int, max_val: int = ADC_MAX, width: int = 16) -> str:
    filled = max(0, min(width, round(value * width / max_val)))
    return chr(255) * filled + " " * (width - filled)


def update_axis_screen(lcd: LCD, label: str, value: int) -> None:
    lcd.show_two_lines(_make_bar(value), f"{label} => {value}"[:16])


def update_screen5(lcd: LCD, mpu: MPU6050) -> None:
    ax, ay, az = mpu.read_accel()
    combined = MPU6050.combined(ax, ay, az)
    line1 = f"X:{ax:5.2f} Y:{ay:5.2f}"
    line2 = f"Z:{az:5.2f} C:{combined:5.2f}"
    lcd.show_two_lines(line1[:16], line2[:16])


def update_screen6(lcd: LCD, ble: BLEUARTServer) -> None:
    msg = ble.get_message()
    if msg is not None:
        lcd.show_two_lines(msg[:16], msg[16:32])


def main() -> None:
    global _last_nibble
    GPIO.setmode(GPIO.BCM)

    adc = ADS7830(ADC_I2C_BUS, ADC_I2C_ADDR)
    lcd = LCD(LCD_I2C_BUS, LCD_I2C_ADDR)
    mpu = MPU6050(MPU_I2C_BUS, MPU_I2C_ADDR)
    led = RGBLED(LED_R, LED_G, LED_B)
    ble = BLEUARTServer("HannahRPi")

    for pin in BTN_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    lcd.init()
    ble.start()

    GPIO.setup(BTN_JOY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        BTN_JOY,
        GPIO.FALLING,
        callback=_joy_button_callback,
        bouncetime=300,
    )

    last_screen = -1

    try:
        while True:
            x_val = adc.read_channel(ADC_CH_X)
            y_val = adc.read_channel(ADC_CH_Y)

            r_pct = x_val / ADC_MAX * 100
            g_pct = y_val / ADC_MAX * 100
            led.set_rgb(r_pct, g_pct, (r_pct + g_pct) / 2)

            with _lock:
                screen = _current_screen

            if screen != last_screen:
                lcd.clear()
                _last_nibble = -1          
                if screen == 0:
                    update_screen1(lcd)    
                elif screen == 5:
                    lcd.show_two_lines("Send a message", "via BLE UART")
                last_screen = screen

            if screen == 1:
                update_screen2(lcd)
            elif screen == 2:
                update_axis_screen(lcd, "VRX", x_val)
            elif screen == 3:
                update_axis_screen(lcd, "VRY", y_val)
            elif screen == 4:
                update_screen5(lcd, mpu)
            elif screen == 5:
                update_screen6(lcd, ble)

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        led.stop()
        lcd.clear()
        ble.stop()
        GPIO.cleanup()
        print("Goodbye.")


if __name__ == "__main__":
    main()
