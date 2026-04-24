import time

import smbus


class LCD:
    """HD44780-compatible 16x2 LCD over a PCF8574 backpack."""

    _RS = 0x01
    _EN = 0x04
    _BL = 0x08
    _ROW_OFFSETS = (0x00, 0x40)

    def __init__(self, bus_num: int, addr: int) -> None:
        self._bus = smbus.SMBus(bus_num)
        self._addr = addr
        self._cache: list[str] = [" " * 16, " " * 16]

    def _write_i2c(self, byte: int) -> None:
        self._bus.write_byte(self._addr, byte)

    def _pulse_enable(self, byte: int) -> None:
        """Latch a nibble into the LCD."""
        self._write_i2c(byte | self._EN)
        time.sleep(0.0005)
        self._write_i2c(byte & ~self._EN)
        time.sleep(0.0005)

    def _write_nibble(self, nibble: int, rs: int) -> None:
        """Send one 4-bit value."""
        byte = (nibble << 4) | self._BL | (self._RS if rs else 0)
        self._pulse_enable(byte)

    def _write_byte(self, byte: int, rs: int) -> None:
        """Send one byte in 4-bit mode."""
        self._write_nibble((byte >> 4) & 0x0F, rs)
        self._write_nibble(byte & 0x0F, rs)

    def _command(self, cmd: int) -> None:
        self._write_byte(cmd, rs=0)

    def _data(self, char_code: int) -> None:
        self._write_byte(char_code, rs=1)

    def init(self) -> None:
        """Initialize the LCD in 4-bit mode."""
        time.sleep(0.05)

        for delay in (0.005, 0.001, 0.001):
            self._write_nibble(0x03, rs=0)
            time.sleep(delay)

        self._write_nibble(0x02, rs=0)
        time.sleep(0.001)

        self._command(0x28)
        self._command(0x0C)
        self._command(0x06)
        self._command(0x01)
        time.sleep(0.002)

    def clear(self) -> None:
        self._command(0x01)
        time.sleep(0.002)
        self._cache = [" " * 16, " " * 16]

    def set_cursor(self, col: int, row: int) -> None:
        """Position the cursor at col on row."""
        self._command(0x80 | (self._ROW_OFFSETS[row] + col))

    def write_string(self, text: str) -> None:
        """Write a string at the current cursor position."""
        for char in text:
            self._data(ord(char))

    def show_two_lines(self, line1: str, line2: str) -> None:
        """Write only the characters that changed since the last call."""
        for row, text in enumerate((line1, line2)):
            padded = f"{text:<16}"[:16]
            old = self._cache[row]
            if padded == old:
                continue
            i = 0
            while i < 16:
                if padded[i] == old[i]:
                    i += 1
                    continue
                j = i + 1
                while j < 16 and padded[j] != old[j]:
                    j += 1
                self.set_cursor(i, row)
                self.write_string(padded[i:j])
                i = j
            self._cache[row] = padded
