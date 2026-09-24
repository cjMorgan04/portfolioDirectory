from machine import Pin, SPI, PWM
import framebuf
import time


# Waveshare Pico-LCD-1.8 pin assignments
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9


def color565(red, green, blue):
    """
    Convert 8-bit RGB values to the byte-swapped RGB565 format
    expected by this Waveshare framebuffer driver.

    Example:
        color565(255, 0, 0) -> red
    """
    value = (
        ((red & 0xF8) << 8)
        | ((green & 0xFC) << 3)
        | (blue >> 3)
    )

    # Swap the two RGB565 bytes.
    return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)


class LCD_1inch8(framebuf.FrameBuffer):
    def __init__(self, brightness=50000):
        self.width = 160
        self.height = 128

        # Control pins
        self.cs = Pin(CS, Pin.OUT, value=1)
        self.dc = Pin(DC, Pin.OUT, value=1)
        self.rst = Pin(RST, Pin.OUT, value=1)

        # LCD uses SPI1
        self.spi = SPI(
            1,
            baudrate=10_000_000,
            polarity=0,
            phase=0,
            sck=Pin(SCK),
            mosi=Pin(MOSI),
            miso=None
        )

        # Backlight control
        self.backlight = PWM(Pin(BL))
        self.backlight.freq(1000)
        self.set_brightness(brightness)

        # Framebuffer
        self.buffer = bytearray(self.width * self.height * 2)

        super().__init__(
            self.buffer,
            self.width,
            self.height,
            framebuf.RGB565
        )

        # Named colors
        self.BLACK = color565(0, 0, 0)
        self.WHITE = color565(255, 255, 255)

        self.RED = color565(255, 0, 0)
        self.GREEN = color565(0, 255, 0)
        self.BLUE = color565(0, 0, 255)

        self.YELLOW = color565(255, 255, 0)
        self.CYAN = color565(0, 255, 255)
        self.MAGENTA = color565(255, 0, 255)

        self.ORANGE = color565(255, 165, 0)
        self.GRAY = color565(128, 128, 128)
        self.DARK_GRAY = color565(40, 40, 40)

        self.init_display()

    def set_brightness(self, brightness):
        """
        Set backlight brightness from 0 to 65535.
        """
        brightness = max(0, min(65535, int(brightness)))
        self.backlight.duty_u16(brightness)

    def write_cmd(self, command):
        """
        Send one command byte to the LCD.
        """
        self.cs.value(1)
        self.dc.value(0)
        self.cs.value(0)

        self.spi.write(bytes([command]))

        self.cs.value(1)

    def write_data(self, data):
        """
        Send one byte or a bytes-like object to the LCD.
        """
        self.cs.value(1)
        self.dc.value(1)
        self.cs.value(0)

        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)

        self.cs.value(1)

    def init_display(self):
        """
        Initialize the ST7735 LCD controller.
        """

        # Hardware reset
        self.rst.value(1)
        time.sleep_ms(10)

        self.rst.value(0)
        time.sleep_ms(10)

        self.rst.value(1)
        time.sleep_ms(120)

        # Memory access control
        self.write_cmd(0x36)
        self.write_data(0x70)

        # 16-bit RGB565 pixel format
        self.write_cmd(0x3A)
        self.write_data(0x05)

        # Frame-rate control
        self.write_cmd(0xB1)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        self.write_cmd(0xB2)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        self.write_cmd(0xB3)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        # Column inversion
        self.write_cmd(0xB4)
        self.write_data(0x07)

        # Power-control sequence
        self.write_cmd(0xC0)
        self.write_data(0xA2)
        self.write_data(0x02)
        self.write_data(0x84)

        self.write_cmd(0xC1)
        self.write_data(0xC5)

        self.write_cmd(0xC2)
        self.write_data(0x0A)
        self.write_data(0x00)

        self.write_cmd(0xC3)
        self.write_data(0x8A)
        self.write_data(0x2A)

        self.write_cmd(0xC4)
        self.write_data(0x8A)
        self.write_data(0xEE)

        # VCOM control
        self.write_cmd(0xC5)
        self.write_data(0x0E)

        # Positive gamma correction
        self.write_cmd(0xE0)
        positive_gamma = (
            0x0F, 0x1A, 0x0F, 0x18,
            0x2F, 0x28, 0x20, 0x22,
            0x1F, 0x1B, 0x23, 0x37,
            0x00, 0x07, 0x02, 0x10
        )

        for value in positive_gamma:
            self.write_data(value)

        # Negative gamma correction
        self.write_cmd(0xE1)
        negative_gamma = (
            0x0F, 0x1B, 0x0F, 0x17,
            0x33, 0x2C, 0x29, 0x2E,
            0x30, 0x30, 0x39, 0x3F,
            0x00, 0x07, 0x03, 0x10
        )

        for value in negative_gamma:
            self.write_data(value)

        # Enable test command
        self.write_cmd(0xF0)
        self.write_data(0x01)

        # Disable RAM power-save mode
        self.write_cmd(0xF6)
        self.write_data(0x00)

        # Exit sleep mode
        self.write_cmd(0x11)
        time.sleep_ms(120)

        # Turn display on
        self.write_cmd(0x29)
        time.sleep_ms(20)

        # Start with a blank screen
        self.fill(self.BLACK)
        self.show()

    def show(self):
        """
        Send the complete framebuffer to the LCD.
        """

        # Column address: 1 through 160
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x00)
        self.write_data(0xA0)

        # Row address: 2 through 129
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x02)
        self.write_data(0x00)
        self.write_data(0x81)

        # Write framebuffer
        self.write_cmd(0x2C)

        self.cs.value(1)
        self.dc.value(1)
        self.cs.value(0)

        self.spi.write(self.buffer)

        self.cs.value(1)