import time
import board
from adafruit_dotstar import DotStar
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
import microcontroller
import supervisor


def blue_led_set(state):
    """Set the internal LED IO13 to this state"""
    led13.value = state

def enable_LDO2(state):
    """Set the power for the second on-board LDO to allow no current draw when not needed."""
    ldo2.value = state
    # A small delay to let the IO change state
    time.sleep(0.035)

def dotstar_off(dotstar: DotStar):
    if dotstar:
        dotstar[0] = (0, 0, 0, 0)

def fatal_error(message, dotstar: DotStar, flashes=10):
    """Prints the error message on the serial line, then flashes a RED light n times, then reloads the microcontroller"""
    blue_led_set(False)
    if message:
        print("fatal error: {}".format(message))
    i = 0
    while i < flashes:
        if dotstar:
            dotstar[0] = (0xfc, 0x03, 0x03, 0.5)
            time.sleep(1.5)
            dotstar[0] = (0, 0, 0, 0)
        time.sleep(1.5)
        i+=1
    supervisor.reload()

def recoverable_error(message, dotstar: DotStar, flashes=3):
    """Prints the error message on the serial line, then flashes a RED light n times, then continues execution"""
    blue_led_set(False)
    if message:
        print("recoverable error: {}".format(message))
    i = 0
    while i < flashes:
        if dotstar:
            dotstar[0] = (0xfc, 0x03, 0x03, 0.5)
            time.sleep(1)
            dotstar[0] = (0, 0, 0, 0)
        time.sleep(1)
        i+=1

def success(dotstar: DotStar, flashes=3):
    """Flashes a GREEN light 3 times"""
    blue_led_set(False)
    i = 0
    while i < flashes:
        if dotstar:
            dotstar[0] = (0x03, 0xfc, 0x0b, 0.5)
            time.sleep(1)
            dotstar[0] = (0, 0, 0, 0)
        time.sleep(1)
        i+=1

def init_step(dotstar: DotStar, step=1):
    """Changes the colour of the LED from stages 1 to 4"""
    if step==1:
        dotstar[0] = (0x03, 0x13, 0xfc, 0.4) # blue
    elif step==2:
        dotstar[0] = (0xd7, 0x03, 0xfc, 0.4) # purple
    elif step==3:
        dotstar[0] = (0xfc, 0xf8, 0x03, 0.4) # yellow
    elif step==4:
        dotstar[0] = (0x20, 0xfc, 0x03, 0.4) # green
    time.sleep(0.1)

def reboot():
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()

# Init Blink LED
led13 = DigitalInOut(board.LED)
led13.direction = Direction.OUTPUT

# Init LDO2 Pin
ldo2 = DigitalInOut(board.LDO2)
ldo2.direction = Direction.OUTPUT

ambient = AnalogIn(board.AMB)
