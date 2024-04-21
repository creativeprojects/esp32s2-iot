#!/bin/sh

from=adafruit-circuitpython-bundle-9.x-mpy-20240417
libraries="adafruit_bme280 adafruit_minimqtt adafruit_dotstar.mpy adafruit_connection_manager.mpy"

mkdir -p lib

for lib in $libraries
do
    echo "Updating $lib"
    rm -rf "lib/$lib"
    cp -a "$HOME/Downloads/$from/lib/$lib" "lib/$lib"
done