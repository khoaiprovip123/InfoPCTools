import psutil
import platform
from logic.info.system import get_local_ip
try:
    import wmi
except ImportError:
    wmi = None

def get_cpu_usage():
    return psutil.cpu_percent(interval=0.1)

def get_cpu_name():
    """
    Gets the detailed CPU name using WMI if available for more detail,
    otherwise falls back to platform.processor().
    """
    try:
        name = platform.processor()
        if name:
            return " ".join(name.split())
    except Exception:
        pass
    if wmi:
        try:
            c = wmi.WMI()
            cpu = c.Win32_Processor()[0]
            name = " ".join(cpu.Name.split()) # Normalize whitespace
            if name:
                return name
        except Exception:
            # WMI might fail, so we'll fall through to the next method
            pass

    return "Unknown CPU"

def get_ram_usage():
    ram = psutil.virtual_memory()
    return ram.percent, f"{ram.used / (1024**3):.1f}/{ram.total / (1024**3):.1f} GB"

def get_physical_disk_usage():
    if not wmi:
        return []

    physical_disks_data = {}
    try:
        c = wmi.WMI()
        for disk in c.Win32_DiskDrive():
            # Use Model as a unique identifier for physical disks
            disk_id = disk.Model.strip() if disk.Model else disk.DeviceID.strip()
            physical_disks_data[disk_id] = {
                "model": disk.Model,
                "total_size": 0,
                "used_size": 0,
                "partitions": []
            }
            # Map partitions to physical disks
            for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    try:
                        usage = psutil.disk_usage(logical_disk.Caption + "\\")
                        physical_disks_data[disk_id]["total_size"] += usage.total
                        physical_disks_data[disk_id]["used_size"] += usage.used
                        physical_disks_data[disk_id]["partitions"].append({
                            "device": logical_disk.Caption + "\\",
                            "fstype": logical_disk.FileSystem,
                            "total": usage.total,
                            "used": usage.used,
                            "percent": usage.percent
                        })
                    except PermissionError:
                        continue

        result = []
        for disk_id, data in physical_disks_data.items():
            if data["total_size"] > 0:
                percent = (data["used_size"] / data["total_size"]) * 100
            else:
                percent = 0
            result.append({
                "model": data["model"],
                "total": data["total_size"],
                "used": data["used_size"],
                "percent": percent,
                "partitions": data["partitions"]
            })
        return result
    except Exception as e:
        print(f"Error getting physical disk usage: {e}")
        return []

def get_network_io_counters():
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent

def get_network_usage():
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent

def get_hardware_info():
    if not wmi:
        return None, "WMI library is not available. Please ensure it is installed and accessible."

    try:
        c = wmi.WMI()
        cs = c.Win32_ComputerSystem()[0]
        bios = c.Win32_BIOS()[0]
        board = c.Win32_BaseBoard()[0]

        # --- System & Motherboard ---
        system_info = {
            "System Type": "Desktop" if not c.Win32_SystemEnclosure() or c.Win32_SystemEnclosure()[0].ChassisTypes[0] in [3, 4, 5, 6, 7, 15, 16] else "Laptop",
            "Hostname": platform.node(),
            "Manufacturer": cs.Manufacturer,
            "Model": cs.Model,
            "Serial Number": bios.SerialNumber,
        }
        motherboard_info = {
            "Manufacturer": board.Manufacturer,
            "Product": board.Product,
            "Serial Number": board.SerialNumber,
        }

        # --- CPU ---
        cpu = c.Win32_Processor()[0]
        cpu_info = {
            "Name": " ".join(cpu.Name.split()), # Normalize whitespace
            "Cores": psutil.cpu_count(logical=False),
            "Threads": psutil.cpu_count(logical=True),
            "Max Clock Speed": f"{cpu.MaxClockSpeed} MHz",
            "Current Clock Speed": f"{psutil.cpu_freq().current} MHz",
            "L2 Cache": f"{cpu.L2CacheSize} KB",
            "L3 Cache": f"{cpu.L3CacheSize} KB",
        }

        # --- RAM ---
        ram_slots = c.Win32_PhysicalMemoryArray()[0].MemoryDevices
        ram_info = {
            "Total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "Slots": f"{len(c.Win32_PhysicalMemory())} / {ram_slots}",
            "Modules": []
        }
        for mem in c.Win32_PhysicalMemory():
            ram_info["Modules"].append(
                f"{mem.DeviceLocator}: {int(mem.Capacity) / (1024**3):.0f}GB, {mem.Speed}MHz, {mem.Manufacturer}"
            )

        # --- GPU ---
        gpu_info = {} 
        for gpu in c.Win32_VideoController():
            gpu_info[gpu.Name] = {
                "VRAM": f"{int(gpu.AdapterRAM) / (1024**2):.0f} MB",
                "Driver Version": gpu.DriverVersion,
                "Status": gpu.Status,
            }

        # --- Storage ---
        storage_info = {}
        
        try:
            c_storage = wmi.WMI(namespace="root/Microsoft/Windows/Storage")
            advanced_disk_info = {
                disk.SerialNumber.strip(): (disk.MediaType, disk.BusType)
                for disk in c_storage.MSFT_PhysicalDisk()
            }
        except Exception:
            advanced_disk_info = {}

        for disk in c.Win32_DiskDrive():
            serial = disk.SerialNumber.strip()
            adv_info = advanced_disk_info.get(serial)
            
            disk_type = "Unknown"
            interface = "Unknown"

            if adv_info:
                media_type, bus_type = adv_info
                disk_type = {3: "HDD", 4: "SSD", 5: "SCM"}.get(media_type, "Unknown")
                interface = {11: "SATA", 17: "NVMe"}.get(bus_type, "Unknown Bus")
            else:
                model_caption = (disk.Model + disk.Caption).lower()
                is_ssd = "ssd" in model_caption
                is_nvme = "nvme" in model_caption or "nvm" in model_caption
                
                if is_nvme:
                    disk_type = "SSD"
                    interface = "NVMe"
                elif is_ssd:
                    disk_type = "SSD"
                    interface = "SATA"
                else:
                    disk_type = "HDD"
                    interface = "SATA"

            storage_info[disk.Caption] = {
                "Type": f"{disk_type} ({interface})",
                "Size": f"{int(disk.Size) / (1024**3):.2f} GB",
                "Partitions": disk.Partitions,
                "Serial Number": serial,
            }

        # --- Network ---
        network_info = {}
        for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            network_info[nic.Description] = {
                "MAC Address": nic.MACAddress,
                "IP Address": ", ".join(nic.IPAddress) if nic.IPAddress else "N/A",
                "Default Gateway": ", ".join(nic.DefaultIPGateway) if nic.DefaultIPGateway else "N/A",
                "DHCP Enabled": nic.DHCPEnabled,
            }

        info = {
            "System": system_info,
            "Motherboard": motherboard_info,
            "CPU": cpu_info,
            "RAM": ram_info,
            "GPU": gpu_info,
            "Storage": storage_info,
            "Network Adapters": network_info,
        }
        return info, None
    except Exception as e:
        return None, f"An error occurred: {e}"

def get_network_config():
    if not wmi:
        return []
    config = []
    try:
        c = wmi.WMI()
        for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if nic.IPAddress and nic.IPSubnet:
                config.append({
                    "interface": nic.Description,
                    "address": nic.IPAddress[0],
                    "netmask": nic.IPSubnet[0],
                    "gateway": nic.DefaultIPGateway[0] if nic.DefaultIPGateway else "N/A",
                    "mac_address": nic.MACAddress if nic.MACAddress else "N/A",
                    "dhcp_enabled": "Yes" if nic.DHCPEnabled else "No"
                })
    except Exception as e:
        print(f"Error getting network config: {e}")
    return config

import requests
import ping3

def get_cpu_speed():
    return f"{psutil.cpu_freq().current / 1000:.2f} GHz"

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except requests.RequestException:
        return "N/A"

def get_ping(host="8.8.8.8"):
    try:
        delay = ping3.ping(host, unit='ms')
        return f"{delay:.0f} ms" if delay is not None else "Timeout"
    except Exception:
        return "Error"

def get_disk_io():
    io = psutil.disk_io_counters()
    return io.read_bytes, io.write_bytes

def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            for entry in temps['coretemp']:
                if 'Package id' in entry.label or 'CPU' in entry.label:
                    return f"{entry.current:.1f}°C"
        elif 'cpu_thermal' in temps:
            for entry in temps['cpu_thermal']:
                return f"{entry.current:.1f}°C"
        return "N/A"
    except Exception:
        return "N/A"

def get_ram_cache():
    try:
        mem = psutil.virtual_memory()
        return f"{mem.cached / (1024**3):.1f} GB Cached"
    except Exception:
        return "N/A"

def get_total_disk_size():
    total_size = 0
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_size += usage.total
        except PermissionError:
            continue
    return f"{total_size / (1024**3):.1f} GB"

def get_mac_addresses():
    mac_addresses = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac_addresses.append(addr.address)
    return ", ".join(mac_addresses) if mac_addresses else "N/A"

def get_system_qr_data():
    cpu_name = get_cpu_name()
    ram_percent, ram_detail = get_ram_usage()
    total_disk_size = get_total_disk_size()
    local_ip = get_local_ip()
    mac_addresses = get_mac_addresses()

    system_type = "N/A"
    hostname = platform.node()
    motherboard_serial = "N/A"
    gpu_name = "N/A"

    if wmi:
        try:
            c = wmi.WMI()
            cs = c.Win32_ComputerSystem()[0]
            bios = c.Win32_BIOS()[0]
            gpus = c.Win32_VideoController()

            system_type = "Desktop" if not c.Win32_SystemEnclosure() or c.Win32_SystemEnclosure()[0].ChassisTypes[0] in [3, 4, 5, 6, 7, 15, 16] else "Laptop"
            motherboard_serial = bios.SerialNumber
            if gpus:
                gpu_name = gpus[0].Name
        except Exception:
            pass

    return {
        "system_type": system_type,
        "hostname": hostname,
        "motherboard_serial": motherboard_serial,
        "cpu_name": cpu_name,
        "ram_detail": ram_detail,
        "ram_percent": ram_percent,
        "total_disk_size": total_disk_size,
        "gpu_name": gpu_name,
        "local_ip": local_ip,
        "mac_addresses": mac_addresses
    }

def get_active_connections():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                try:
                    proc = psutil.Process(conn.pid)
                    connections.append({
                        "pid": conn.pid,
                        "process_name": proc.name(),
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    except psutil.AccessDenied:
        return [{"pid": "N/A", "process_name": "N/A", "remote_address": "Access Denied to retrieve network connections."}]
    return connections