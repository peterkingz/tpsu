from pymodbus.client import ModbusSerialClient
import os

# --- Config ---
BMS_BAUDRATE = 9600
BMS_SLAVE_ID = 1

# --- Find available serial port ---
def find_serial_port():
    try:
        for dev in os.listdir("/dev"):
            if dev.startswith("usb_serial_"):
                port = "/dev/" + dev
                print("[Modbus] Found serial port:", port)
                return port
    except Exception as e:
        print(f"[Modbus] /dev directory not found! Error: {e}")
    print("[Modbus] No USB serial ports found!")
    return None

class BMSBattery:
    def __init__(self, baudrate=BMS_BAUDRATE, slave_id=BMS_SLAVE_ID, timeout=1):
        self.port = find_serial_port()
        if not self.port:
            raise FileNotFoundError("No USB serial port found for BMS")
        
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.timeout = timeout

        self.client = ModbusSerialClient(
            port=self.port,
            baudrate=self.baudrate,
            stopbits=1,
            bytesize=8,
            parity='N',
            timeout=self.timeout
        )
        if not self.client.connect():
            raise ConnectionError(f"Failed to connect to {self.port}")
        print(f"[Modbus] Connected to {self.port}")

    def read_registers(self, address, count=1):
        result = self.client.read_holding_registers(address, count, unit=self.slave_id)
        if result.isError():
            raise IOError(f"Modbus read error at address {address}")
        return result.registers

    def write_register(self, address, value):
        result = self.client.write_register(address, value, unit=self.slave_id)
        if result.isError():
            raise IOError(f"Modbus write error at address {address}")
        return True

    def read_coils(self, address, count=1):
        result = self.client.read_coils(address, count, unit=self.slave_id)
        if result.isError():
            raise IOError(f"Modbus read coils error at address {address}")
        return result.bits[:count]

    def write_coils(self, address, values):
        result = self.client.write_coils(address, values, unit=self.slave_id)
        if result.isError():
            raise IOError(f"Modbus write coils error at address {address}")
        return True

    def close(self):
        self.client.close()
        print(f"[Modbus] Disconnected from {self.port}")

    def dump_bms_data(self):
        """
        Dump BMS data.
        :return: List of BMS data
        """
        data = self.read_registers(0, 2)
        return data
