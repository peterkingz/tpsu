chmod +x /home/tekever/tpsu/zenohd
/home/tekever/tpsu/./zenohd &

# start the zenoh-mqtt bridge in the background
chmod +x /home/tekever/tpsu/zenoh-bridge-mqtt
/home/tekever/tpsu/./zenoh-bridge-mqtt &

chmod +x /home/tekever/tpsu/boot-tpsu.sh
/home/tekever/tpsu/boot-tpsu.sh/./boot-tpsu.sh