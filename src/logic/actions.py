


import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image
from . import logic # Import logic to get hardware info

def open_github():
    webbrowser.open("https://github.com/")

def check_windows_update():
    os.system("start ms-settings:windowsupdate")

def open_firewall_settings():
    os.system("start wf.msc")

def run_repair_command(command, backup=False):
    if backup:
        backup_dir = "C:\\driver-backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        command = f'pnputil /export-driver * "{backup_dir}"'
    
    try:
        subprocess.Popen(['powershell', '-Command', f'Start-Process cmd -Verb RunAs -ArgumentList "/c {command}"'], shell=True)
    except Exception as e:
        print(f"Error running command: {e}")

def export_hardware_info_to_txt(user_info: dict = None):
    info, error = logic.get_hardware_info()
    if error:
        # You might want to show an error message to the user
        print(f"Error getting hardware info: {error}")
        return

    # Set up the root window for the file dialog, then hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to choose where to save the file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.* ")],
        title="Save Hardware Info As..."
    )

    if not file_path:
        # User cancelled the save dialog
        return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if user_info:
                f.write("--- USER INFORMATION ---\n")
                for key, value in user_info.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")

            for section, data in info.items():
                f.write(f"--- {section.upper()} ---\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            f.write(f"{key}:\n")
                            for sub_key, sub_value in value.items():
                                f.write(f"  {sub_key}: {sub_value}\n")
                        elif isinstance(value, list):
                            f.write(f"{key}:\n")
                            for item in value:
                                f.write(f"  - {item}\n")
                        else:
                            f.write(f"{key}: {value}\n")
                f.write("\n")
        # Optionally, notify the user of success
        # For a GUI app, you'd use a message box
        print(f"Hardware info saved to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def export_qr_code_image(qr_image: Image.Image):
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.* ")],
        title="Save QR Code As..."
    )

    if not file_path:
        return

    try:
        qr_image.save(file_path)
        print(f"QR code saved to {file_path}")
    except Exception as e:
        print(f"Error saving QR code: {e}")

def open_windows_defender_settings():
    os.system("start windowsdefender:")

def open_uac_settings():
    os.system("UserAccountControlSettings.exe")

def open_bitlocker_settings():
    os.system("start manage-bde.exe")

def run_quick_scan():
    print("Running quick scan...")
    # Placeholder for actual quick scan command
    # Example: subprocess.run(["powershell", "-Command", "Start-MpScan -ScanType QuickScan"])

def run_full_scan():
    print("Running full scan...")
    # Placeholder for actual full scan command
    # Example: subprocess.run(["powershell", "-Command", "Start-MpScan -ScanType FullScan"])

def enable_firewall():
    try:
        subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "on"], check=True, shell=True)
        print("Firewall enabled.")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling firewall: {e}")

def disable_firewall():
    try:
        subprocess.run(["netsh", "advfirewall", "set", "allprofiles", "state", "off"], check=True, shell=True)
        print("Firewall disabled.")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling firewall: {e}")

def toggle_windows_defender_realtime_protection(enable: bool):
    command = "Set-MpPreference -DisableRealtimeMonitoring $false" if enable else "Set-MpPreference -DisableRealtimeMonitoring $true"
    try:
        subprocess.run(["powershell", "-Command", command], check=True, shell=True)
        print(f"Windows Defender Real-time Protection: {'Enabled' if enable else 'Disabled'}.")
    except subprocess.CalledProcessError as e:
        print(f"Error toggling Windows Defender Real-time Protection: {e}")

def update_virus_definitions():
    try:
        subprocess.run(["powershell", "-Command", "Update-MpSignature"], check=True, shell=True)
        print("Windows Defender virus definitions updated.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating virus definitions: {e}")

def run_windows_defender_scan(scan_type: str):
    if scan_type == "quick":
        command = "Start-MpScan -ScanType QuickScan"
    elif scan_type == "full":
        command = "Start-MpScan -ScanType FullScan"
    elif scan_type == "custom":
        command = "Start-MpScan -ScanType CustomScan" # This would typically require a path
    else:
        print("Invalid scan type.")
        return
    try:
        subprocess.run(["powershell", "-Command", command], check=True, shell=True)
        print(f"Windows Defender {scan_type} scan initiated.")
    except subprocess.CalledProcessError as e:
        print(f"Error initiating Windows Defender scan: {e}")

def update_applications():
    print("Checking for application updates...")
    # Placeholder for actual application update logic
    # This would typically involve checking package managers (Chocolatey, Winget, etc.)
    # or specific application update mechanisms.
    pass

def update_drivers():
    print("Checking for driver updates...")
    # Placeholder for actual driver update logic
    pass

def system_restore():
    """Opens the System Restore wizard."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process rstrui.exe -Verb RunAs'], shell=True)
    except Exception as e:
        print(f"Error opening System Restore: {e}")

def system_scan():
    """Runs SFC /scannow to scan and repair system files."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process cmd -Verb RunAs -ArgumentList "/c sfc /scannow"'], shell=True)
    except Exception as e:
        print(f"Error running system scan: {e}")

def fix_printer():
    """Opens the printer troubleshooter."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process "msdt.exe" -ArgumentList "/id PrinterDiagnostic"'], shell=True)
    except Exception as e:
        print(f"Error opening printer troubleshooter: {e}")

def delete_printer():
    """Opens the print management console to delete a printer."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process printmanagement.msc -Verb RunAs'], shell=True)
    except Exception as e:
        print(f"Error opening print management: {e}")

def install_printer():
    """Opens the Add Printer wizard."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process "rundll32.exe" -ArgumentList "printui.dll,PrintUIEntry /il"'], shell=True)
    except Exception as e:
        print(f"Error opening Add Printer wizard: {e}")

def open_windows_security():
    """Opens the Windows Security app."""
    try:
        os.system("start windowsdefender:")
    except Exception as e:
        print(f"Error opening Windows Security: {e}")

def open_account_settings():
    """Opens the Windows account settings."""
    try:
        os.system("start ms-settings:signinoptions")
    except Exception as e:
        print(f"Error opening account settings: {e}")

def open_app_browser_control():
    """Opens the App & browser control settings."""
    try:
        os.system("start ms-settings:appsfeatures")
    except Exception as e:
        print(f"Error opening App & browser control: {e}")

def open_print_management():
    """Opens the Print Management console."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process printmanagement.msc -Verb RunAs'], shell=True)
    except Exception as e:
        print(f"Error opening Print Management: {e}")

def create_system_image():
    """Initiates the Windows System Image Backup wizard."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process sdclt.exe -Verb RunAs'], shell=True)
    except Exception as e:
        print(f"Error initiating System Image Backup: {e}")

def backup_files_folders():
    """Opens the File History settings for backing up files and folders."""
    try:
        os.system("start ms-settings:backup")
    except Exception as e:
        print(f"Error opening File History settings: {e}")

def restore_files_folders():
    """Opens the File History restore interface."""
    try:
        os.system("start control.exe /name Microsoft.FileHistory")
    except Exception as e:
        print(f"Error opening File History restore: {e}")

def open_recovery_drive_creator():
    """Opens the Recovery Drive Creator wizard."""
    try:
        subprocess.Popen(['powershell', '-Command', 'Start-Process recoverydrive.exe -Verb RunAs'], shell=True)
    except Exception as e:
        print(f"Error opening Recovery Drive Creator: {e}")

def flush_dns():
    """Flushes the DNS resolver cache."""
    try:
        result = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, check=True, shell=True)
        print("DNS cache flushed successfully.\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error flushing DNS cache: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def release_ip():
    """Releases the IP address for all adapters."""
    try:
        result = subprocess.run(["ipconfig", "/release"], capture_output=True, text=True, check=True, shell=True)
        print("IP address released successfully.\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error releasing IP address: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def renew_ip():
    """Renews the IP address for all adapters."""
    try:
        result = subprocess.run(["ipconfig", "/renew"], capture_output=True, text=True, check=True, shell=True)
        print("IP address renewed successfully.\n" + result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error renewing IP address: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def open_network_sharing_center():
    """Opens the Network and Sharing Center."""
    try:
        os.system("start control.exe /name Microsoft.NetworkAndSharingCenter")
    except Exception as e:
        print(f"Error opening Network and Sharing Center: {e}")

def ping_host():
    """Pings a specified host to check network connectivity."""
    root = tk.Tk()
    root.withdraw()
    host = simpledialog.askstring("Ping Host", "Enter host to ping:")
    root.destroy()
    if host:
        try:
            result = subprocess.run(["ping", host], capture_output=True, text=True, check=True, shell=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error pinging host: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def set_dns():
    """Allows the user to set custom DNS servers for a network adapter."""
    root = tk.Tk()
    root.withdraw()
    adapter_name = simpledialog.askstring("Set DNS", "Enter the name of the network adapter (e.g., Ethernet):")
    if adapter_name:
        dns_server = simpledialog.askstring("Set DNS", "Enter the preferred DNS server (e.g., 8.8.8.8):")
        if dns_server:
            try:
                # Set primary DNS
                subprocess.run(["netsh", "interface", "ipv4", "set", "dns", adapter_name, "static", dns_server, "primary"], check=True, shell=True)
                print(f"DNS set to {dns_server} for {adapter_name}.")
                # Optionally, set secondary DNS
                secondary_dns = simpledialog.askstring("Set DNS", "Enter the secondary DNS server (optional):")
                if secondary_dns:
                    subprocess.run(["netsh", "interface", "ipv4", "add", "dns", adapter_name, secondary_dns, "index=2"], check=True, shell=True)
                    print(f"Secondary DNS set to {secondary_dns} for {adapter_name}.")
            except subprocess.CalledProcessError as e:
                print(f"Error setting DNS: {e.stderr}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    root.destroy()

def set_static_ip():
    """Allows the user to set a static IP address for a network adapter."""
    root = tk.Tk()
    root.withdraw()
    adapter_name = simpledialog.askstring("Set Static IP", "Enter the name of the network adapter (e.g., Ethernet):")
    if adapter_name:
        ip_address = simpledialog.askstring("Set Static IP", "Enter the IP Address:")
        subnet_mask = simpledialog.askstring("Set Static IP", "Enter the Subnet Mask:")
        gateway = simpledialog.askstring("Set Static IP", "Enter the Default Gateway:")
        if all([ip_address, subnet_mask, gateway]):
            try:
                subprocess.run(["netsh", "interface", "ipv4", "set", "address", adapter_name, "static", ip_address, subnet_mask, gateway], check=True, shell=True)
                print(f"Static IP set for {adapter_name}: IP={ip_address}, Subnet={subnet_mask}, Gateway={gateway}")
            except subprocess.CalledProcessError as e:
                print(f"Error setting static IP: {e.stderr}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    root.destroy()
