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
