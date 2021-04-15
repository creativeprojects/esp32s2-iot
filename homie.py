
from adafruit_minimqtt.adafruit_minimqtt import MQTT
from socketpool import SocketPool

class Homie:

    def __init__(self, name, broker, port, socketPool: SocketPool):
        self.name = name
        self.retain = True
        # Set up a MiniMQTT Client
        self.mqtt_client = MQTT(
            broker=broker,
            port=port,
            socket_pool=socketPool,
            # ssl_context=ssl.create_default_context(),
        )
    
        # Setup the callback methods above
        self.mqtt_client.on_connect = connected
        self.mqtt_client.on_disconnect = disconnected
        self.mqtt_client.on_message = message

    def publish(self, temperature, humidity, pressure, ambient_light, withDescription=False):
        # Connect the client to the MQTT broker.
        print("Connecting to MQTT broker...")
        self.mqtt_client.connect()
        if withDescription:
            self.mqtt_client.publish("homie/{}/$homie".format(self.name), "4.0.0", self.retain)
            self.mqtt_client.publish("homie/{}/$name".format(self.name), "MQTT Feather-S2 agent", self.retain)
            self.mqtt_client.publish("homie/{}/$nodes".format(self.name), "bme280", self.retain)

            self.mqtt_client.publish("homie/{}/bme280/$name".format(self.name), "BME280 sensor", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/$type".format(self.name), "bme280", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/$properties".format(self.name), "temperature,pressure,humidity", self.retain)

            self.mqtt_client.publish("homie/{}/bme280/temperature/$name".format(self.name), "Temperature", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/temperature/$unit".format(self.name), "°C", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/temperature/$datatype".format(self.name), "float", self.retain)

            self.mqtt_client.publish("homie/{}/bme280/pressure/$name".format(self.name), "Pressure", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/pressure/$unit".format(self.name), "hPa", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/pressure/$datatype".format(self.name), "float", self.retain)

            self.mqtt_client.publish("homie/{}/bme280/humidity/$name".format(self.name), "Humidity", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/humidity/$unit".format(self.name), "%", self.retain)
            self.mqtt_client.publish("homie/{}/bme280/humidity/$datatype".format(self.name), "float", self.retain)

            self.mqtt_client.publish("homie/{}/alspt19/$name".format(self.name), "ALS-PT19 Ambient Light Sensor", self.retain)
            self.mqtt_client.publish("homie/{}/alspt19/$type".format(self.name), "als-pt19", self.retain)
            self.mqtt_client.publish("homie/{}/alspt19/$properties".format(self.name), "light", self.retain)

            self.mqtt_client.publish("homie/{}/alspt19/light/$name".format(self.name), "Light", self.retain)
            self.mqtt_client.publish("homie/{}/alspt19/light/$unit".format(self.name), "%", self.retain)
            self.mqtt_client.publish("homie/{}/alspt19/light/$datatype".format(self.name), "float", self.retain)

        self.state_ready()
        self.mqtt_client.publish("homie/{}/bme280/temperature".format(self.name), temperature, self.retain)
        self.mqtt_client.publish("homie/{}/bme280/humidity".format(self.name), humidity, self.retain)
        self.mqtt_client.publish("homie/{}/bme280/pressure".format(self.name), pressure, self.retain)
        self.mqtt_client.publish("homie/{}/alspt19/light".format(self.name), ambient_light, self.retain)
        self.state_sleeping()
        self.mqtt_client.disconnect()

    def state_ready(self):
        self.mqtt_client.publish("homie/{}/$state".format(self.name), "ready", self.retain)

    def state_sleeping(self):
        self.mqtt_client.publish("homie/{}/$state".format(self.name), "sleeping", self.retain)

    def state_lost(self):
        self.mqtt_client.publish("homie/{}/$state".format(self.name), "lost", self.retain)

def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT broker!")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT broker!")

def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))
