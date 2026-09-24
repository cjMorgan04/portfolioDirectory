from machine import Pin, SPI, PWM
from picoLCD import LCD_1inch8
import max31855
import time

# Setup Thermocouple 
spi = SPI(0, sck=Pin(18), mosi=None, miso=Pin(16), baudrate=5000000)
sensor = max31855.MAX31855(spi, Pin(17, Pin.OUT))

# Power on LCD
pwm = PWM(Pin(13))
pwm.freq(1000)
pwm.duty_u16(32768)
# Setup LCD
lcd = LCD_1inch8()
lcd.fill(lcd.BLACK) # Screen will be black


counter=0
# Read loop
while True:
    tempC = sensor.read_temp_c()
    if tempC is not None and tempC is not False:
        tempF = tempC * 9/5 + 32
    if tempC is False:
        print("Thermocouple disconnected")
    elif tempC is None:
        print("Sensor fault")
    else:
        
        print(f"Temperature: {tempC:.1f}°C  {tempF:.1f}°F")
    lcd.text(f"Temperature: ", 10, 10, lcd.WHITE)
    lcd.text(f"{tempC:.1f}C  {tempF:.1f}F", 10, 20, lcd.RED)
    counter += 1
    lcd.show()
    time.sleep(1)
    lcd.fill(lcd.BLACK)