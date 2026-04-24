import time
import math

MPU_ADDR = 0x68


def mpu_setup(i2c):
    i2c.write_byte_data(MPU_ADDR, 0x6B, 0x00)
    time.sleep(0.1)
    print("MPU ready")


def _to_signed(val):
    if val >= 32768:
        return val - 65536
    return val


def get_accel(i2c):
    data = i2c.read_i2c_block_data(MPU_ADDR, 0x3B, 6)
    ax = _to_signed(data[0] << 8 | data[1]) / 16384.0
    ay = _to_signed(data[2] << 8 | data[3]) / 16384.0
    az = _to_signed(data[4] << 8 | data[5]) / 16384.0
    return round(ax, 2), round(ay, 2), round(az, 2)


def combined(ax, ay, az):
    return round(math.sqrt(ax**2 + ay**2 + az**2), 2)
