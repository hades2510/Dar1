from machine import Pin, SPI
from ssd1306 import SSD1306_SPI

from constants import *
from encoder import init as encoder_init, get_pos as encoder_pos
from audio import init as audio_init

# display init
spi = SPI(0, baudrate=80000000, polarity=0, phase=0, sck=Pin(6), mosi=Pin(7), miso=None)

display = SSD1306_SPI(WIDTH, HEIGHT, spi, Pin(0), Pin(1), Pin(3))

# push button init
button = Pin(27, Pin.IN, Pin.PULL_DOWN)

# encoder init
Pin(28, Pin.IN, Pin.PULL_UP)
Pin(29, Pin.IN, Pin.PULL_UP)
encoder_init(2, Pin(28))

#audio init
audio_init(26)

def read_input():            
    is_pressed = button.value()
    
    rot = encoder_pos()
    
    return rot, is_pressed