# esp32s2-iot

Send temperature, humidity, pressure, ambient light, and motion detection to MQTT.
Get feedback from the board LED.

## hardware

* Microcontroller: Unexpectedmaker FeatherS2
* Temperature sensor: BME280 via I2C bus
* Motion sensor: HC-SR501 PIR on pin D13 (11)

## config

`config.py`
```python
config = {
    "name": "esp32s2",
    "wifi_ssid": "MY WIFI",
    "wifi_password": "",
    "mqtt_broker": "mqtt.example.com",
    "mqtt_port": 1883,
    "brightness": 0.1,
    "sleep": 600, # measurement cycle in seconds
    "watchdog_timer": 800, # no response in seconds
}
```