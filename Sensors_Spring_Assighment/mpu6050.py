import math

import smbus


class MPU6050:
    """Minimal I2C driver for MPU-6050 accelerometer reads."""

    _PWR_MGMT_1 = 0x6B
    _ACCEL_XOUT_H = 0x3B
    _SENSITIVITY = 16384.0

    def __init__(self, bus_num: int = 1, addr: int = 0x68) -> None:
        self._bus = smbus.SMBus(bus_num)
        self._addr = addr
        self._bus.write_byte_data(addr, self._PWR_MGMT_1, 0x00)

    @staticmethod
    def _to_signed(value: int) -> int:
        return value - 0x10000 if value >= 0x8000 else value

    def read_accel(self) -> tuple[float, float, float]:
        """Return (ax, ay, az) in g.

        Reads all six accel registers in one I2C transaction so all three
        axes are sampled at the same instant.
        """
        data = self._bus.read_i2c_block_data(self._addr, self._ACCEL_XOUT_H, 6)
        ax = self._to_signed(data[0] << 8 | data[1]) / self._SENSITIVITY
        ay = self._to_signed(data[2] << 8 | data[3]) / self._SENSITIVITY
        az = self._to_signed(data[4] << 8 | data[5]) / self._SENSITIVITY
        return ax, ay, az

    @staticmethod
    def combined(ax: float, ay: float, az: float) -> float:
        """Return the magnitude of the acceleration vector in g."""
        return math.sqrt(ax * ax + ay * ay + az * az)
