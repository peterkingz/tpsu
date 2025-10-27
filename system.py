import os
import json
import platform
import pkg_resources
import subprocess

class SystemRUT:
    def __init__(self):
        pass

    def get_OS(self):
        # Prefer os.uname() with fall back to platform.uname()
        try:
            info = os.uname()
            data = {
                "system": info.sysname,
                "node": info.nodename,
                "release": info.release,
                "version": info.version,
                "machine": info.machine
            }
            return json.dumps(data, indent=4, ensure_ascii=False)
        
        except Exception:
            info = platform.uname()
            data = {
                "system": info.system,
                "node": info.node,
                "release": info.release,
                "version": info.version,
                "machine": info.machine
            }
            return json.dumps(data, indent=4, ensure_ascii=False)
            

    def get_temp_c(self):
        try:
            with open("/sys/devices/virtual/thermal/thermal_zone0/hwmon0/temp1_input", "r") as f:
                temp_millic = int(f.read().strip()) / 1000.0
            data={"temperature1": {"value":temp_millic, "unit":"°C"}}
            return json.dumps(data, indent=4, ensure_ascii=False)
        except Exception:
            data={"temperature1": {"value":"not found", "unit":"not found"}}
            return json.dumps(data, indent=4, ensure_ascii=False)

    def get_storage_usage(self, path="/tmp"):
        stat = os.statvfs(path)
        total = stat.f_blocks * stat.f_frsize / (1024 * 1024)
        free = stat.f_bfree * stat.f_frsize / (1024 * 1024)
        used = total - free

        data = {
            "storage": {
                "path": path,
                "total_MB": round(total, 2),
                "used_MB": round(used, 2),
                "available_MB": round(free, 2),
                "unit": "MB"
            }
        }
        return json.dumps(data, indent=4, ensure_ascii=False)

    def get_ram_usage(self):
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                key, value = line.split(":")
                meminfo[key.strip()] = value.strip()

        total = int(meminfo["MemTotal"].split()[0]) / 1024  # kB → MB
        free = int(meminfo["MemAvailable"].split()[0]) / 1024
        used = total - free

        data = {
            "ram": {
                "total_MB": round(total, 2),
                "used_MB": round(used, 2),
                "available_MB": round(free, 2),
                "unit": "MB"
            }
        }
        return json.dumps(data, indent=4, ensure_ascii=False)

    def get_installed_packages(self):
        packages = {}
        for dist in pkg_resources.working_set:
            packages[dist.project_name] = dist.version

        return json.dumps({"packages": packages}, indent=4, ensure_ascii=False)

    def modem_info(self):
        try:
            output = subprocess.check_output("gsmctl -iJmxyo", shell=True, stderr=subprocess.STDOUT)
            decoded = output.decode("utf-8").strip()
            lines = decoded.splitlines()
            
            # Expected order of fields from gsmctl output
            fields = [
                "imei",
                "iccid",
                "model",
                "imsi",
                "firmware_version",
                "operator"
            ]
            
            # Build a dictionary mapping field names to output lines
            info = dict(zip(fields, lines))
            info["rssi"] = self.modem_rssi()
            info["ip"] = self.modem_ip()
            
            # Return as JSON under "modem-info"
            return json.dumps({"modem-info": info}, indent=4, ensure_ascii=False)
        
        except subprocess.CalledProcessError as e:
            return json.dumps({
                "modem-info": None,
                "error": f"Command failed: {e.output.decode('utf-8', errors='ignore')}"
            }, indent=4, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "modem-info": None,
                "error": str(e)
            }, indent=4, ensure_ascii=False)

    def modem_rssi(self):
        try:
            # Run the full shell pipeline
            output = subprocess.check_output("gsmctl -q | grep RSSI", shell=True, stderr=subprocess.STDOUT)
            decoded = output.decode("utf-8").strip()
            # Expected line format: "RSSI: -76"
            parts = decoded.split(":")
            if len(parts) == 2:
                rssi_value = int(parts[1].strip())
                return int(rssi_value)
            else:
                return int(-99)
        except Exception as e:
            return int(-99)

    def modem_ip(self):
        try:
            # Run the ubus command for the modem
            output = subprocess.check_output("ubus call network.interface.mob1s1a1_4 status",shell=True,stderr=subprocess.STDOUT)
            decoded = output.decode("utf-8").strip()
            
            # Parse JSON output from ubus and extract IPv4 address
            data = json.loads(decoded)
            ipv4_list = data.get("ipv4-address", [])
            if ipv4_list and "address" in ipv4_list[0]:
                return ipv4_list[0]["address"]
            else:
                return "0.0.0.0"
        
        except Exception:
            # Return fallback if anything goes wrong
            return "0.0.0.0"
    

if __name__ == "__main__":
    sysinfo = SystemRUT()
    print(sysinfo.get_OS())
    print(sysinfo.get_temp_c())
    print(sysinfo.get_storage_usage())
    print(sysinfo.get_ram_usage())
    print(sysinfo.get_installed_packages())
    print(sysinfo.modem_info())



