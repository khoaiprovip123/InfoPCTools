import psutil
import platform
import subprocess
import winreg
import socket
import datetime
try:
    import wmi
except ImportError:
    wmi = None

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_cpu_name():
    if wmi:
        try:
            c = wmi.WMI()
            return c.Win32_Processor()[0].Name
        except Exception:
            pass
    return platform.processor()

def get_ram_usage():
    ram = psutil.virtual_memory()
    return ram.percent, f"{ram.used / (1024**3):.1f}/{ram.total / (1024**3):.1f} GB"

def get_disk_usage():
    partitions_info = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions_info.append({
                "device": partition.device,
                "fstype": partition.fstype,
                "total": usage.total,
                "percent": usage.percent
            })
        except PermissionError:
            continue
    return partitions_info

def get_network_usage():
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent

def get_system_summary():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        "os": f"{platform.system()} {platform.release()}",
        "hostname": platform.node(),
        "uptime": f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
    }

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "N/A"

def get_hardware_info():
    if not wmi:
        return None, "wmi library not found. Please install it using 'pip install wmi'"
    
    try:
        c = wmi.WMI()
        info = {
            "System": {
                "System Type": "Desktop" if not c.Win32_SystemEnclosure() or c.Win32_SystemEnclosure()[0].ChassisTypes[0] in [3, 4, 5, 6, 7, 15, 16] else "Laptop",
                "Hostname": platform.node(),
                "Manufacturer": c.Win32_ComputerSystem()[0].Manufacturer,
            },
            "Operating System": {
                "OS": platform.system() + " " + platform.release(),
                "Version": platform.version(),
                "Build": platform.win32_ver()[1],
            },
            "CPU": {
                "Name": platform.processor(),
                "Cores": psutil.cpu_count(logical=False),
                "Threads": psutil.cpu_count(logical=True),
                "Clock Speed": f"{psutil.cpu_freq().current} Mhz",
            },
            "RAM": {
                "Total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "Type": "DDR4" # Placeholder
            },
            "GPU": {gpu.Name: f"{int(gpu.AdapterRAM) / (1024**2):.0f} MB VRAM" for gpu in c.Win32_VideoController()},
            "Storage": {disk.Caption: f"{disk.MediaType}, {int(disk.Size) / (1024**3):.2f} GB" for disk in c.Win32_DiskDrive()},
            "Network Adapters": {nic.Description: nic.IPAddress[0] for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True)}
        }
        return info, None
    except Exception as e:
        return None, f"An error occurred: {e}"

def get_installed_apps():
    apps = []
    uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                skey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, skey_name) as skey:
                    try:
                        display_name = winreg.QueryValueEx(skey, "DisplayName")[0]
                        publisher = winreg.QueryValueEx(skey, "Publisher")[0]
                        install_date = winreg.QueryValueEx(skey, "InstallDate")[0]
                        apps.append((display_name, publisher, install_date))
                    except OSError:
                        continue
    except Exception:
        pass
    return sorted(apps)

def get_startup_apps():
    apps = []
    startup_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
    ]
    for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for startup_key in startup_keys:
            try:
                with winreg.OpenKey(hkey, startup_key) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        name, path, _ = winreg.EnumValue(key, i)
                        apps.append((name, path))
            except FileNotFoundError:
                continue
    return apps

def get_firewall_status():
    try:
        output = subprocess.check_output(["netsh", "advfirewall", "show", "allprofiles", "state"], universal_newlines=True)
        return "On" if "State ON" in output else "Off"
    except Exception:
        return "Unknown"

def get_antivirus_info():
    if not wmi:
        return "WMI not available"
    try:
        c = wmi.WMI(namespace="//./root/SecurityCenter2")
        av_product = c.AntiVirusProduct()
        if av_product:
            return av_product[0].displayName
        return "Not found"
    except Exception:
        return "Unknown"

def get_network_config():
    config = []
    addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in addrs.items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                config.append({
                    "interface": interface_name,
                    "address": address.address,
                    "netmask": address.netmask
                })
    return config

def get_active_connections():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                try:
                    proc = psutil.Process(conn.pid)
                    connections.append(f"PID: {conn.pid} - {proc.name()} -> {conn.raddr.ip}:{conn.raddr.port}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    except psutil.AccessDenied:
        return ["Access Denied to retrieve network connections."]
    return connections