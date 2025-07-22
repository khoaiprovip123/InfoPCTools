import customtkinter as ctk
from logic import actions, localization

class SystemRepairView(ctk.CTkFrame):
    STYLE = {
        "font_info": ("Roboto", 11),
        "font_info_bold": ("Roboto", 11, "bold"),
    }

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._set_colors()
        self.configure(fg_color=self.card_fg_color)

        self.grid_columnconfigure(0, weight=1) # Function Name
        self.grid_columnconfigure(1, weight=3) # Description
        self.grid_columnconfigure(2, weight=1) # Action Button

        # Header Row
        ctk.CTkLabel(self, text=localization.get_text("Function Name"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self, text=localization.get_text("Description"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self, text=localization.get_text("Action"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        repair_options = [
            (localization.get_text("Scan and Fix System Files (SFC)"), "sfc_scannow_desc", "sfc /scannow"),
            (localization.get_text("Check and Repair Disk (CHKDSK)"), "chkdsk_desc", "chkdsk /f /r"),
            (localization.get_text("Troubleshoot Print Spooler"), "print_spooler_desc", "net stop spooler && del %systemroot%\\System32\\spool\\printers\\* /Q /F /S && net start spooler"),
            (localization.get_text("Open Device Manager"), "device_manager_desc", "devmgmt.msc"),
            (localization.get_text("Create System Restore Point"), "create_restore_point_desc", "systempropertiesprotection.exe"),
            (localization.get_text("Backup Drivers"), "backup_drivers_desc", "pnputil /export-driver * .")
        ]
        
        ctk.CTkLabel(self, text=localization.get_text("driver_backup_info"), text_color=self.text_color).grid(row=len(repair_options)+1, column=0, columnspan=3, pady=5, padx=20, sticky="w")

        for i, (text, desc_key, command) in enumerate(repair_options):
            row_num = i + 1 # Start from row 1 after header

            ctk.CTkLabel(
                self,
                text=text,
                font=self.STYLE["font_info"],
                anchor="w",
                text_color=self.text_color
            ).grid(row=row_num, column=0, sticky="nw", padx=(5, 10), pady=2)

            ctk.CTkLabel(
                self,
                text=localization.get_text(desc_key),
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            ).grid(row=row_num, column=1, sticky="ew", padx=(0, 5), pady=2)

            is_backup = (text == localization.get_text("Backup Drivers"))
            button = ctk.CTkButton(
                self,
                text=localization.get_text("Run"), # Generic button text
                command=lambda c=command, b=is_backup: actions.run_repair_command(c, b),
                font=self.STYLE["font_info"],
                width=80
            )
            button.grid(row=row_num, column=2, sticky="nsew", padx=5, pady=2)

    def cancel_updates(self, *args, **kwargs):
        # This view has no scheduled updates
        pass