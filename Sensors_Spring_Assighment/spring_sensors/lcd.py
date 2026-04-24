import time

LCD_WIDTH = 16

_RS = 0x01
_EN = 0x04
_BL = 0x08


def _nibble(i2c, addr, nibble, rs=0):
    b = (nibble << 4) | _BL | (rs * _RS)
    i2c.write_byte(addr, b | _EN)
    time.sleep(0.0005)
    i2c.write_byte(addr, b & ~_EN)
    time.sleep(0.0005)


def _send(i2c, addr, byte, rs=0):
    _nibble(i2c, addr, (byte >> 4) & 0xF, rs)
    _nibble(i2c, addr, byte & 0xF, rs)


def LCD_init(i2c, addr):
    time.sleep(0.05)
    for _ in range(3):
        _nibble(i2c, addr, 0x03)
        time.sleep(0.005)
    _nibble(i2c, addr, 0x02)
    time.sleep(0.001)
    _send(i2c, addr, 0x28)  # 4-bit mode, 2 lines
    _send(i2c, addr, 0x0C)  # display on
    _send(i2c, addr, 0x06)  # entry mode
    _send(i2c, addr, 0x01)  # clear
    time.sleep(0.002)


def LCD_write(i2c, addr, line1, line2):
    _send(i2c, addr, 0x80)
    for c in str(line1).ljust(LCD_WIDTH)[:LCD_WIDTH]:
        _send(i2c, addr, ord(c), rs=1)
    _send(i2c, addr, 0xC0)
    for c in str(line2).ljust(LCD_WIDTH)[:LCD_WIDTH]:
        _send(i2c, addr, ord(c), rs=1)
