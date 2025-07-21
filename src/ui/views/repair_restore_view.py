import customtkinter as ctk
from logic import actions, localization

class RepairRestoreView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        repair_options = {
            localization.get_text("Scan and Fix System Files"): "sfc /scannow",
            localization.get_text("Troubleshoot Print Spooler"): "net stop spooler && del %systemroot%\\System32\\spool\\printers\\* /Q /F /S && net start spooler",
            localization.get_text("Open Device Manager"): "devmgmt.msc",
            localization.get_text("Create System Restore Point"): "systempropertiesprotection.exe",
            localization.get_text("Backup Drivers"): "pnputil /export-driver * ."
        }
        
        ctk.CTkLabel(self, text=localization.get_text("driver_backup_info")).pack(pady=5, padx=20, anchor="w")

        for text, command in repair_options.items():
            is_backup = (text == localization.get_text("Backup Drivers"))
            button = ctk.CTkButton(self, text=text, command=lambda c=command, b=is_backup: actions.run_repair_command(c, b))
            button.pack(pady=10, padx=20, fill="x")

    def cancel_updates(self):
        # This view has no scheduled updates
        pass
