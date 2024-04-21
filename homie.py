
from adafruit_minimqtt.adafruit_minimqtt import MQTT
from socketpool import SocketPool

class Homie:

    def __init__(self, name: str, broker: str, port: int, impl: str, socketPool: SocketPool, ssl_context=None, username: str = None, password: str = None):
        self.name = name
        self.impl = impl
        self.retain = True
        self.qos = 1
        self.is_connected = False
        self.state_topic = "homie/{}/$state".format(self.name)
        # Set up a MiniMQTT Client
        self.mqtt_client = MQTT(
            broker = broker,
            port = port,
            socket_pool = socketPool,
            ssl_context = ssl_context,
            is_ssl = ssl_context is not None,
            username = username,
            password = password,
        )
    
        # Setup the callback methods above
        self.mqtt_client.on_connect = connected
        self.mqtt_client.on_disconnect = disconnected
        self.mqtt_client.on_message = message

    def publishSensors(self, temperature, humidity, pressure, ambient_light, withDescription=False):
        self.connect()
        if withDescription:
            self.mqtt_client.publish("homie/{}/$homie".format(self.name), "4.0.0", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/$name".format(self.name), "MQTT Feather-S2 agent", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/$implementation".format(self.name), self.impl, self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/$nodes".format(self.name), "bme280,alspt19,hcsr501", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/bme280/$name".format(self.name), "BME280 sensor", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/$type".format(self.name), "bme280", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/$properties".format(self.name), "temperature,pressure,humidity", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/bme280/temperature/$name".format(self.name), "Temperature", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/temperature/$unit".format(self.name), "°C", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/temperature/$datatype".format(self.name), "float", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/bme280/pressure/$name".format(self.name), "Pressure", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/pressure/$unit".format(self.name), "hPa", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/pressure/$datatype".format(self.name), "float", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/bme280/humidity/$name".format(self.name), "Humidity", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/humidity/$unit".format(self.name), "%", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/bme280/humidity/$datatype".format(self.name), "float", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/alspt19/$name".format(self.name), "ALS-PT19 Ambient Light Sensor", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/alspt19/$type".format(self.name), "als-pt19", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/alspt19/$properties".format(self.name), "light", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/alspt19/light/$name".format(self.name), "Light", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/alspt19/light/$unit".format(self.name), "%", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/alspt19/light/$datatype".format(self.name), "float", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/hcsr501/$name".format(self.name), "HC-SR501 PIR Motion Sensor", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/hcsr501/$type".format(self.name), "hc-sr501", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/hcsr501/$properties".format(self.name), "motion", self.retain, self.qos)

            self.mqtt_client.publish("homie/{}/hcsr501/motion/$name".format(self.name), "Motion Detection", self.retain, self.qos)
            self.mqtt_client.publish("homie/{}/hcsr501/motion/$datatype".format(self.name), "boolean", self.retain, self.qos)
            
        self.mqtt_client.publish("homie/{}/bme280/temperature".format(self.name), temperature, self.retain, self.qos)
        self.mqtt_client.publish("homie/{}/bme280/humidity".format(self.name), humidity, self.retain, self.qos)
        self.mqtt_client.publish("homie/{}/bme280/pressure".format(self.name), pressure, self.retain, self.qos)
        self.mqtt_client.publish("homie/{}/alspt19/light".format(self.name), ambient_light, self.retain, self.qos)
        self.disconnect()
    
    def publishMotion(self, state):
        self.connect()
        self.mqtt_client.publish("homie/{}/hcsr501/motion".format(self.name), homieBoolean(state), self.retain, self.qos)
        # don't disconnect after motion detection, we need to lower the signal down in a few seconds
        if state == False:
            self.disconnect()

    def connect(self):
        if self.is_connected:
            return True
        print("Connecting to MQTT broker...")
        self.mqtt_client.will_set(self.state_topic, "lost", self.qos, self.retain)
        self.mqtt_client.connect()
        self.state_ready()
        self.is_connected = True
        return True
    
    def disconnect(self):
        if not self.is_connected:
            return
        self.state_sleeping()
        self.mqtt_client.disconnect()
        self.is_connected = False

    def state_ready(self):
        self.mqtt_client.publish(self.state_topic, "ready", self.retain, self.qos)

    def state_sleeping(self):
        self.mqtt_client.publish(self.state_topic, "sleeping", self.retain, self.qos)

def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT broker")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT broker")

def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))

def homieBoolean(state):
    if state == True:
        return "true"
    return "false"
