import time

import board
import busio
import config_key
import microcontroller
import socketpool
import wifi
from adafruit_bme280 import advanced as adafruit_bme280
from adafruit_dotstar import DotStar
from microcontroller import watchdog
from watchdog import WatchDogMode
from digitalio import DigitalInOut, Direction, Pull

import feathers2
from homie import Homie

SECOND          = 1e+9
BME280_ADDRESS  = 0x76
SoftwareVersion = "1.4.0"

BME280_SENSOR_ERROR = 4
LIGHT_SENSOR_ERROR  = 5
NETWORK_ERROR       = 6

DEFAULT_BRIGHTNESS = 0.1
DOTSTAR_CLOCK_PIN = board.APA102_SCK
DOTSTAR_DATA_PIN  = board.APA102_MOSI
PIR_MOTION_PIN    = board.D13

# banner
print("\nThat4home feather-s2 agent {}".format(SoftwareVersion))
print("last reboot was: {}".format(microcontroller.cpu.reset_reason))

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = DotStar(DOTSTAR_CLOCK_PIN, DOTSTAR_DATA_PIN, 1, brightness=DEFAULT_BRIGHTNESS, auto_write=True)

# motion detection
detector = DigitalInOut(PIR_MOTION_PIN)
detector.direction = Direction.INPUT
detector.pull = Pull.UP
motionState = False

# Turn on the internal blue LED
feathers2.working(True)

# Get configuration from a config.py file
try:
    from config import config
except ImportError:
    feathers2.fatal_error("missing config.py file", dotstar)

# setting up watchdog
try:
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    watchdog.timeout = config[config_key.WATCHDOG_TIMER]
    watchdog.mode = WatchDogMode.RESET
except Exception as err:
    feathers2.fatal_error("watchdog: {}".format(err), dotstar)

feathers2.init_step(dotstar, 1)
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_ADDRESS)
except Exception as err:
    feathers2.fatal_error("i2c: {}".format(err), dotstar, BME280_SENSOR_ERROR)

feathers2.init_step(dotstar, 2)

try:
    wifi_ssid = config[config_key.WIFI_SSID]
    print("Connecting to %s"%wifi_ssid)
    wifi.radio.connect(wifi_ssid, config[config_key.WIFI_PASSWORD])
    # print("Connected to %s: channel = %d, bssid = %s" % (wifi_ssid, wifi.Network.channel, wifi.Network.bssid))
    print("IP address:", wifi.radio.ipv4_address)
except Exception as err:
    feathers2.fatal_error("wifi: {}".format(err), dotstar, NETWORK_ERROR)

feathers2.init_step(dotstar, 3)

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

ssl_context = None
if config[config_key.MQTT_USE_TLS]:
    try:
        import ssl
    except ImportError as e:
        print("ssl module not found: ", str(e))
    else:
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(cadata=config[config_key.CA_DATA])

homie = Homie(
    name = config[config_key.NAME], 
    broker = config[config_key.MQTT_BROKER], 
    port = config[config_key.MQTT_PORT], 
    impl = SoftwareVersion, 
    socketPool = pool,
    ssl_context = ssl_context,
    username = config[config_key.MQTT_USERNAME] if config_key.MQTT_USERNAME in config else None,
    password = config[config_key.MQTT_PASSWORD] if config_key.MQTT_PASSWORD in config else None,
)

feathers2.init_step(dotstar, 4)

first_time = True
network_error = False
while True:
    if not network_error:
        watchdog.feed()

    # Invert the internal LED state
    feathers2.working(True)
    # clean neoled
    feathers2.dotstar_off(dotstar)

    try:
        temperature = "%0.2f" % bme280.temperature
        humidity = "%0.2f" % bme280.relative_humidity
        pressure = "%0.2f" % bme280.pressure

        print("Temperature: %s C" % temperature)
        print("Humidity: %s %%" % humidity)
        print("Pressure: %s hPa" % pressure)
    except Exception as err:
        feathers2.recoverable_error("bme280: {}".format(err), dotstar, BME280_SENSOR_ERROR)
        # try again in a minute
        time.sleep(60)
        continue

    try:
        ambient_light = "%d" % feathers2.ambient.value

        print("Ambient light: %s" % ambient_light)
    except Exception as err:
        feathers2.recoverable_error("ambient: {}".format(err), dotstar, LIGHT_SENSOR_ERROR)

    try:
        homie.publishSensors(temperature, humidity, pressure, ambient_light, first_time)
        first_time = False
        network_error = False
    except Exception as err:
        feathers2.recoverable_error("mqtt: {}".format(err), dotstar, NETWORK_ERROR)
        network_error = True
        # try again in a minute
        time.sleep(60)
        continue

    feathers2.success(dotstar)

    # write down the time before entering sub-loop
    latest = time.monotonic_ns()

    if config[config_key.MOTION_DETECTION]:
        while motionState or latest + (config[config_key.SLEEP] * SECOND) > time.monotonic_ns():
            if motionState != detector.value:
                motionState = detector.value
                # print("Detection: {} at {}".format(motionState, time.monotonic_ns()))
                feathers2.motion(dotstar, motionState)
                try:
                    homie.publishMotion(motionState)
                    network_error = False
                except Exception as err:
                    feathers2.recoverable_error("mqtt: {}".format(err), dotstar, NETWORK_ERROR)
                    network_error = True
                    # try again in a minute
                    time.sleep(60)
                    continue

                if motionState:
                    # wait for 3 seconds after a detection
                    time.sleep(3)
                else:
                    # signal going down, wait for a minute
                    time.sleep(60)
                continue
            time.sleep(0.3)
    else:
        time.sleep(config[config_key.SLEEP])
