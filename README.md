# esp32s2-iot

Send temperature, humidity, pressure, ambient light, and motion detection to MQTT (using homie protocol).
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
    "wifi_password": "<my secret password>",
    "mqtt_broker": "mqtt.example.com",
    "mqtt_port": 1883,
    "mqtt_use_tls": False,
    "mqtt_username": None,
    "mqtt_password": None,
    "sleep": 600, # measurement cycle in seconds
    "watchdog_timer": 800, # no response in seconds
    "ca_data": "CA certificate in PEM format",
}
```

## TLS

Version 1.4.0 now supports connection to MQTT brokers using TLS.
You need to provide the CA certificate in PEM format in the `config.py` file.
