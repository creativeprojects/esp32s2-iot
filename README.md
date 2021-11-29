# esp32s2-iot

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