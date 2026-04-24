ADC_ADDR = 0x48

_CMDS = [0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4]


def read_channel(i2c, channel):
    i2c.write_byte(ADC_ADDR, _CMDS[channel])
    return i2c.read_byte(ADC_ADDR)


def read_x(i2c):
    return read_channel(i2c, 5)


def read_y(i2c):
    return read_channel(i2c, 6)
