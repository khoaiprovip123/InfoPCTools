

import os
import subprocess
import webbrowser
import tkinter as tk
from tkinter import filedialog
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

