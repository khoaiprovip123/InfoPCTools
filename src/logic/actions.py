

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

