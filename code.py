from homie import Homie
import time
import board
import busio
import adafruit_bme280
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import feathers2
import supervisor
from adafruit_dotstar import DotStar

BME280_ADDRESS = 0x76
SoftwareVersion = "1.0.0"

# banner
print("\nThat4home feather-s2 agent {}".format(SoftwareVersion))

# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1, auto_write=True)

# Turn on the internal blue LED
feathers2.led_set(True)

# Get configuration from a config.py file
try:
    from config import config
except ImportError:
    feathers2.fatal_error("missing config.py file", dotstar)

feathers2.init_step(dotstar, 1)
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=BME280_ADDRESS)
except Exception as err:
    feathers2.fatal_error("i2c: {}".format(err), dotstar)

feathers2.init_step(dotstar, 2)

try:
    print("Connecting to %s"%config["wifi_ssid"])
    wifi.radio.connect(config["wifi_ssid"], config["wifi_password"])
    print("Connected to %s!"%config["wifi_ssid"])
    print("IP address:", wifi.radio.ipv4_address)
except Exception as err:
    feathers2.fatal_error("wifi: {}".format(err), dotstar)

feathers2.init_step(dotstar, 3)

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

homie = Homie(config["name"], config["mqtt_broker"], config["mqtt_port"], pool)

feathers2.init_step(dotstar, 4)

first_time = True
while True:
    # Invert the internal LED state
    feathers2.led_set(True)
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
        feathers2.recoverable_error("bme280: {}".format(err), dotstar)
        # try again in a minute
        time.sleep(60)
        continue

    try:
        homie.publish(temperature, humidity, pressure, first_time)
        first_time = False
    except Exception as err:
        feathers2.recoverable_error("mqtt: {}".format(err), dotstar)
        # try again in a minute
        time.sleep(60)
        continue

    # Invert the internal LED state
    feathers2.led_set(False)

    feathers2.success(dotstar)

    time.sleep(config["sleep"])
