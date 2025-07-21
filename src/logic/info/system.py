import psutil
import platform
import datetime
import socket

try:
    import wmi
except ImportError:
    wmi = None

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

def get_firewall_status():
    try:
        import subprocess
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

def get_windows_defender_status():
    if not wmi:
        return "WMI not available"
    try:
        c = wmi.WMI(namespace="//./root/SecurityCenter2")
        defender = c.AntiVirusProduct(displayName="Windows Defender")
        if defender and defender[0].productState == 266240: # 266240 means enabled and up to date
            return "On"
        return "Off"
    except Exception:
        return "Unknown"

def get_uac_status():
    if not wmi:
        return "WMI not available"
    try:
        c = wmi.WMI(namespace="//./root/cimv2")
        uac_setting = c.GetMethod("Win32_ComputerSystem", "EnableLUA")
        # This WMI method doesn't directly return status, it's more complex.
        # A simpler check is to read registry key:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
        enable_lua = winreg.QueryValueEx(key, "EnableLUA")[0]
        winreg.CloseKey(key)
        return "On" if enable_lua == 1 else "Off"
    except Exception:
        return "Unknown"

def get_bitlocker_status():
    if not wmi:
        return "WMI not available"
    try:
        c = wmi.WMI(namespace="//./root/cimv2/Security/MicrosoftVolumeEncryption")
        drives = c.Win32_EncryptableVolume()
        status = []
        for drive in drives:
            protection_status = "Unknown"
            if drive.ProtectionStatus == 0: protection_status = "Off"
            elif drive.ProtectionStatus == 1: protection_status = "On"
            status.append(f"{drive.DriveLetter}: {protection_status}")
        return ", ".join(status) if status else "Not found"
    except Exception:
        return "Unknown"

def get_windows_defender_realtime_protection_status():
    try:
        import subprocess
        # Using PowerShell to get real-time protection status
        command = "(Get-MpPreference).DisableRealtimeMonitoring"
        output = subprocess.check_output(["powershell", "-Command", command], universal_newlines=True).strip()
        return "Off" if output.lower() == "true" else "On"
    except Exception:
        return "Unknown"
