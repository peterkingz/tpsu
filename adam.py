from pymodbus.client import ModbusTcpClient

# --- Config ---
PORT = 502

class ADAM:
    def __init__(self, ip, port=PORT, unit_id=1):
        """
        Initialize connection to ADAM-6066 Modbus TCP.
        :param ip: Device IP address
        :param port: Modbus TCP port (default 502)
        :param unit_id: Modbus slave ID
        """
        self.ip = ip
        self.port = port
        self.unit_id = unit_id
        self.client = ModbusTcpClient(self.ip, port=self.port)
        if not self.client.connect():
            raise ConnectionError(f"Failed to connect to {self.ip}:{self.port}")
        print(f"[ADAM-6066] Connected to {self.ip}:{self.port}")

    def read_inputs(self, address=0, count=6):
        """
        Read digital inputs (DI) from ADAM-6066.
        :param address: Starting address (default 0)
        :param count: Number of inputs to read (default 6)
        :return: List of input states (0 or 1)
        """
        result = self.client.read_discrete_inputs(address, count, slave=self.unit_id)
        if result.isError():
            raise IOError("Failed to read digital inputs")
        return result.bits

    def read_outputs(self, address=0, count=6):
        """
        Read digital outputs (DO) from ADAM-6066.
        :param address: Starting address (default 0)
        :param count: Number of outputs to read (default 6)
        :return: List of output states (0 or 1)
        """
        result = self.client.read_coils(address, count, slave=self.unit_id)
        if result.isError():
            raise IOError("Failed to read digital outputs")
        return result.bits

    def write_output(self, address, value):
        """
        Write a digital output (DO) on ADAM-6066.
        :param address: Output address (0-5)
        :param value: 0 or 1
        :return: True if successful
        """
        result = self.client.write_coil(address, value, slave=self.unit_id)
        if result.isError():
            raise IOError(f"Failed to write output at address {address}")
        return True

    # --- Analog Inputs ---
    def read_analog_inputs(self, address=0, count=8):
        """
        Read analog inputs (AI) from ADAM series.
        Many ADAM AI modules use holding registers starting at 0.
        :param address: Starting register address
        :param count: Number of analog channels
        :return: List of integer values (raw ADC)
        """
        result = self.client.read_holding_registers(address, count, unit=self.unit_id)
        if result.isError():
            raise IOError("Failed to read analog inputs")
        return result.registers

    def close(self):
        """Close Modbus TCP connection."""
        self.client.close()
        print(f"[ADAM-6066] Disconnected from {self.ip}:{self.port}")