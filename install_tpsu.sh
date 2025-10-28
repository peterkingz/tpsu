#!/bin/bash

# get root
su

# install python3 
opkg update
opkg install python3

# install pip
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
pip install --upgrade pip

#opkg -e /etc/opkg/openwrt/distfeeds.conf update
#opkg -e /etc/opkg/openwrt/distfeeds.conf install nano

# install python packages
pip install pyserial==3.5 pymodbus==3.11.3 
#pip install --no-build-isolation --only-binary=:all: eclipse-zenoh==1.6.2

# prepare the tpsu folder structure
cd /home
mkdir tekever
cd tekever
mkdir tpsu

# where to get this repo without being public????
wget https://github.com/tekever/tpsu/archive/refs/heads/master.zip
tar -xf master.zip -C /home/tekever/tpsu

# make executable the loader
chmod +x /home/tekever/boot-tpsu.sh

#create a service to launch and monitor each 5s the script above
cat << 'EOF' > /etc/init.d/tpsu
#!/bin/sh /etc/rc.common
# Description: Boot TPSU

START=99
STOP=10

TPSU_SCRIPT="/home/tekever/tpsu/boot-tpsu.sh"
MONITOR_PID_FILE="/var/run/tpsu_monitor.pid"

start() {
    # Avoid multiple monitors
    if [ -f "$MONITOR_PID_FILE" ] && kill -0 $(cat "$MONITOR_PID_FILE") 2>/dev/null; then
        echo "TPSU monitor already running."
        return
    fi

    echo "Starting TPSU monitor..."
    monitor_loop &
    echo $! > "$MONITOR_PID_FILE"
}

monitor_loop() {
    # Run the script if not running
    if ! pgrep -f "$TPSU_SCRIPT" > /dev/null; then
        echo "TPSU not running, starting..."
        $TPSU_SCRIPT &
    fi
    # Relaunch this function after 1 second
    sleep 5
    monitor_loop
}

stop() {
    echo "Stopping TPSU monitor..."
    if [ -f "$MONITOR_PID_FILE" ]; then
        kill $(cat "$MONITOR_PID_FILE") 2>/dev/null
        rm -f "$MONITOR_PID_FILE"
    fi
    pkill -f "$TPSU_SCRIPT"
}

status() {
    if [ -f "$MONITOR_PID_FILE" ] && kill -0 $(cat "$MONITOR_PID_FILE") 2>/dev/null; then
        echo "TPSU monitor is running."
    else
        echo "TPSU monitor is not running."
    fi

    if pgrep -f "$TPSU_SCRIPT" > /dev/null; then
        echo "TPSU script is running."
    else
        echo "TPSU script is not running."
    fi
}
EOF
#START=99 ensures it starts late in the boot process (similar to multi-user.target).
#STOP=10 ensures it stops early during shutdown.
#The monitor_loop function relaunches itself every 5 seconds
#Only one monitor runs at a time; duplicate starts are avoided.
#CPU usage is minimal because it sleeps 5 second between checks.

# make the script executable
chmod +x /etc/init.d/tpsu

# enable the service
/etc/init.d/tpsu enable

# start the service
/etc/init.d/tpsu start

