import threading
import time
import os
from bms import BMSBattery
from adam import ADAM
from zenoh import ZenohPub

THREAD_SLEEP = 5

IP_GPIO = '192.168.1.100'
IP_ANALOG = '192.168.1.101'
UNIT_ID_GPIO = 1            # Modbus slave ID (usually 1)
UNIT_ID_ANALOG = 2            # Modbus slave ID (usually 1)

bms_data = {}
states = {}
di = []
do = []
ai = []

# comms task 
def comms():
    while True:
        print("FAKE comms")
        time.sleep(THREAD_SLEEP)

# monitor bms task
def monitor_bms():

    while True:
        bms = BMSBattery()
        bms_data = bms.dump_bms_data()
        bms.close()
        print("FAKE BMS")
        time.sleep(THREAD_SLEEP)

# states task
def state_machine():

    adam_ios = ADAM(ip=IP_GPIO, unit_id=UNIT_ID_GPIO)
    adam_analog = ADAM(ip=IP_ANALOG, unit_id=UNIT_ID_ANALOG)

    while True:

        # Digital Inputs
        di = adam_ios.read_digital_inputs()
        print("Digital Inputs:", di)

        # Digital Outputs
        do = adam_ios.read_digital_outputs()
        print("Digital Outputs:", do)

        # Write DO0 ON
        adam_ios.write_digital_output(0, 1)
        print("DO0 set to 1")

        # Analog Inputs
        ai = adam_analog.read_analog_inputs(address=0, count=8)
        print("Analog Inputs:", ai)

        print("FAKE ADAMs")
        time.sleep(THREAD_SLEEP)


# events task
def events():
    while True:
        # Exemplo de uso

        #if event changes then send pub message

        pub = ZenohPub("topic/exemplo")
        pub.send_message({"key": "value"})
        pub.close()

        print("FAKE events")
        time.sleep(THREAD_SLEEP)

# main
if __name__ == "__main__":
    t1 = threading.Thread(target=comms, daemon=True)
    t2 = threading.Thread(target=monitor_bms, daemon=True)
    t3 = threading.Thread(target=state_machine, daemon=True)
    t4 = threading.Thread(target=events, daemon=True)

    #t1.start()
    t2.start()
    #t3.start()

    # Keep main thread alive
    while True:
        time.sleep(1)
