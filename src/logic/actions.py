

import os
import subprocess
import webbrowser

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

