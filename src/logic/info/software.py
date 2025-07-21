import psutil
import winreg
import datetime

_installed_apps_cache = None # Cache variable
_startup_apps_cache = None # Cache variable

def get_installed_apps():
    global _installed_apps_cache
    if _installed_apps_cache is not None:
        return _installed_apps_cache

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
    _installed_apps_cache = sorted(apps) # Cache the results
    return _installed_apps_cache

    _startup_apps_cache = None

def get_startup_apps():
    global _startup_apps_cache
    if _startup_apps_cache is not None:
        return _startup_apps_cache

    apps = {}

    # Registry keys for enabled startup apps
    run_keys = {
        winreg.HKEY_LOCAL_MACHINE: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        ],
        winreg.HKEY_CURRENT_USER: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        ]
    }

    # Registry keys for startup approval status (includes disabled apps)
    startup_approved_keys = {
        winreg.HKEY_LOCAL_MACHINE: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        ],
        winreg.HKEY_CURRENT_USER: [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        ]
    }

    # Get enabled apps from Run/RunOnce keys
    for hkey_const, subkeys in run_keys.items():
        for subkey_str in subkeys:
            try:
                with winreg.OpenKey(hkey_const, subkey_str) as key:
                    num_values = winreg.QueryInfoKey(key)[1]
                    for i in range(0, num_values):
                        value_name, path, _ = winreg.EnumValue(key, i)
                        apps[value_name] = {
                            "name": value_name,
                            "path": path,
                            "hkey": hkey_const,
                            "subkey": subkey_str,
                            "value_name": value_name,
                            "enabled": True
                        }
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error accessing registry key {hkey_const} - {subkey_str}: {e}")
                continue

    # Get status from StartupApproved keys and update existing apps or add new ones
    for hkey_const, subkeys in startup_approved_keys.items():
        for subkey_str in subkeys:
            try:
                with winreg.OpenKey(hkey_const, subkey_str) as key:
                    num_values = winreg.QueryInfoKey(key)[1]
                    for i in range(0, num_values):
                        value_name, data, _ = winreg.EnumValue(key, i)
                        # data is a REG_BINARY, first byte indicates status (0x02 enabled, 0x03 disabled)
                        is_enabled = (data[0] == 2)

                        if value_name in apps:
                            apps[value_name]["enabled"] = is_enabled
                        else:
                            # If not in 'Run' keys, it's a disabled app not directly in Run/RunOnce
                            # Its path is not directly available from StartupApproved keys.
                            apps[value_name] = {
                                "name": value_name,
                                "path": "N/A", # Path is not directly available for these entries
                                "hkey": hkey_const, 
                                "subkey": subkey_str,
                                "value_name": value_name,
                                "enabled": is_enabled
                            }
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error accessing registry key {hkey_const} - {subkey_str}: {e}")
                continue

    _startup_apps_cache = list(apps.values())
    return _startup_apps_cache

def set_startup_app_status(hkey_const, subkey_str, value_name, path, enable):
    try:
        if enable:
            with winreg.OpenKey(hkey_const, subkey_str, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, path)
        else:
            with winreg.OpenKey(hkey_const, subkey_str, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
        return True, None
    except Exception as e:
        return False, str(e)

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
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
