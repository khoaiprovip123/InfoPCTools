import psutil
import platform
import subprocess
import winreg
import socket
import datetime
import sys

try:
    import wmi
except ImportError:
    wmi = None
    print("WMI module not found. Please install it using 'pip install wmi'.")
except Exception as e:
    wmi = None
    print(f"Error importing WMI module: {e}")

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
        
        # Try to get advanced disk info from MSFT_PhysicalDisk
        try:
            c_storage = wmi.WMI(namespace="root/Microsoft/Windows/Storage")
            # Create a mapping from the physical disk's serial number to its type info
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
                # MediaType: 3=HDD, 4=SSD, 5=SCM
                disk_type = {3: "HDD", 4: "SSD", 5: "SCM"}.get(media_type, "Unknown")
                # BusType: 11=SATA, 17=NVMe
                interface = {11: "SATA", 17: "NVMe"}.get(bus_type, "Unknown Bus")
            else:
                # Fallback for older systems or if MSFT_PhysicalDisk fails
                model_caption = (disk.Model + disk.Caption).lower()
                is_ssd = "ssd" in model_caption
                is_nvme = "nvme" in model_caption or "nvm" in model_caption
                
                if is_nvme:
                    disk_type = "SSD"
                    interface = "NVMe"
                elif is_ssd:
                    disk_type = "SSD"
                    interface = "SATA"  # Assumption, but common
                else:
                    disk_type = "HDD"
                    # Could be SATA, IDE, etc. SATA is a safe guess.
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
                        install_date_str = winreg.QueryValueEx(skey, "InstallDate")[0]
                        # Format date to DD/MM/YYYY
                        try:
                            install_date = datetime.datetime.strptime(install_date_str, "%Y%m%d").strftime("%d/%m/%Y")
                        except ValueError:
                            install_date = install_date_str # Keep original if format is unexpected
                        apps.append((display_name, publisher, install_date))
                    except OSError:
                        continue
    except Exception:
        pass
    return sorted(apps)

def get_startup_apps():
    apps = []
    startup_keys = {
        winreg.HKEY_LOCAL_MACHINE: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        ],
        winreg.HKEY_CURRENT_USER: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        ]
    }
    
    for hkey_const, subkeys in startup_keys.items():
        for subkey_str in subkeys:
            print(f"Attempting to open registry key: {hkey_const} - {subkey_str}") # Debug print
            try:
                with winreg.OpenKey(hkey_const, subkey_str) as key:
                    num_values = winreg.QueryInfoKey(key)[1] # Get number of values
                    print(f"Found {num_values} values in {subkey_str}") # Debug print
                    for i in range(0, num_values):
                        value_name, path, _ = winreg.EnumValue(key, i)
                        apps.append({
                            "name": value_name,
                            "path": path,
                            "hkey": hkey_const,
                            "subkey": subkey_str,
                            "value_name": value_name,
                            "enabled": True # If it's found, it's enabled
                        })
            except FileNotFoundError:
                print(f"Registry key not found: {hkey_const} - {subkey_str}") # Debug print
                continue
            except Exception as e:
                print(f"Error accessing registry key {hkey_const} - {subkey_str}: {e}") # Debug print
                continue
    return apps

def set_startup_app_status(hkey_const, subkey_str, value_name, path, enable):
    try:
        if enable:
            # Ensure the key exists and set the value
            with winreg.OpenKey(hkey_const, subkey_str, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, path)
        else:
            # Delete the value
            with winreg.OpenKey(hkey_const, subkey_str, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
        return True, None
    except Exception as e:
        return False, str(e)

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

import json
import qrcode

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

def get_simplified_hardware_info(user_info: dict = None):
    info, error = get_hardware_info()
    if error:
        return None, error

    if not info:
        return None, "No hardware information available."

    simplified_info = {}

    if user_info:
        for key, value in user_info.items():
            if value:
                simplified_info[key] = value

    simplified_info.update({
        "Hostname": info["System"].get("Hostname", "N/A"),
        "CPU Name": info["CPU"].get("Name", "N/A"),
        "RAM Total": info["RAM"].get("Total", "N/A"),
        "OS Version": f"{platform.system()} {platform.release()}",
        "Total Disk Size": "N/A",
        "GPU Name": "N/A"
    })

    # Calculate total disk size
    total_disk_size_gb = 0
    for disk_name, disk_details in info["Storage"].items():
        size_str = disk_details.get("Size", "0 GB").replace(" GB", "")
        try:
            total_disk_size_gb += float(size_str)
        except ValueError:
            pass
    simplified_info["Total Disk Size"] = f"{total_disk_size_gb:.2f} GB"

    # Get GPU Name
    if info["GPU"]:
        simplified_info["GPU Name"] = ", ".join(info["GPU"].keys())

    return simplified_info, None

def generate_qr_code_for_hardware_info(user_info: dict = None):
    simplified_info, error = get_simplified_hardware_info(user_info)
    if error:
        return None, f"Error getting simplified hardware info: {error}"
    
    if simplified_info:
        try:
            # Convert the dictionary to a formatted string for QR code
            qr_data = ""
            for key, value in simplified_info.items():
                qr_data += f"{key}: {value}\n"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=5, # Smaller box size for direct display
                border=2,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            return img, None
        except Exception as e:
            return None, f"Error generating QR code: {e}"
    return None, "No simplified hardware information to generate QR code."

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    # Sort processes by CPU usage in descending order
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
