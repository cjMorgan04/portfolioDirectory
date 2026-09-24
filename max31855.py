class MAX31855:
    """
    MicroPython driver for the MAX31855 thermocouple converter.
    """

    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.cs.value(1)
        self.buffer = bytearray(4)

    def _read_raw(self):
        self.cs.value(0)

        try:
            self.spi.readinto(self.buffer)
        finally:
            self.cs.value(1)

        return int.from_bytes(self.buffer, "big")

    def read(self):
        """
        Return thermocouple temperature in degrees Celsius.
        """

        value = self._read_raw()

        # Check the general fault flag, bit 16.
        if value & (1 << 16):
            if value & 0x01:
                raise RuntimeError("Thermocouple not connected")

            if value & 0x02:
                raise RuntimeError("Thermocouple shorted to ground")

            if value & 0x04:
                raise RuntimeError("Thermocouple shorted to power")

            raise RuntimeError("Unknown MAX31855 fault")

        # Thermocouple temperature is a signed 14-bit value.
        raw_temperature = (value >> 18) & 0x3FFF

        # Convert from signed 14-bit number.
        if raw_temperature & 0x2000:
            raw_temperature -= 0x4000

        # Resolution is 0.25 degrees C per bit.
        return raw_temperature * 0.25

    def read_internal(self):
        """
        Return the MAX31855 internal cold-junction temperature.
        """

        value = self._read_raw()

        raw_internal = (value >> 4) & 0x0FFF

        if raw_internal & 0x0800:
            raw_internal -= 0x1000

        return raw_internal * 0.0625