import smbus


class ADS7830:

    _CHANNEL_CMDS = (0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4)

    def __init__(self, bus_num: int = 1, addr: int = 0x48) -> None:
        self._bus = smbus.SMBus(bus_num)
        self._addr = addr

    def read_channel(self, channel: int) -> int:
        assert 0 <= channel <= 7, "Channel must be 0-7"
        self._bus.write_byte(self._addr, self._CHANNEL_CMDS[channel])
        return self._bus.read_byte(self._addr)