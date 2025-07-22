import customtkinter as ctk
from logic import localization
from .system_repair_view import SystemRepairView
from .printer_management_view import PrinterManagementView
from logic import actions

class BackupRestoreView(ctk.CTkFrame):
    STYLE = {
        "font_family": "Roboto",
        "font_title": ("Roboto", 24, "bold"),
        "font_card_header": ("Roboto", 14, "bold"),
        "font_info": ("Roboto", 11),
        "font_info_bold": ("Roboto", 11, "bold"),
    }

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
            self.border_color = "#5C6370"
            self.hover_color = "#3E3E3E"
            self.tab_text_color = "#FFD700"
            self.tab_selected_text_color = "#00BFFF"
            self.segmented_button_unselected_color = "#44475a"
            self.segmented_button_selected_color = "#00BFFF"
            self.status_ok_color = "#50FA7B"
            self.status_bad_color = "#FF5555"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.border_color = "#DCE4EE"
            self.hover_color = "#CFCFCF"
            self.tab_text_color = "#FF8C00"
            self.tab_selected_text_color = "#0078D7"
            self.segmented_button_unselected_color = "#F0F0F0"
            self.segmented_button_selected_color = "#0078D7"
            self.status_ok_color = "#28A745"
            self.status_bad_color = "#DC3545"

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")

        self._set_colors()

        ctk.CTkLabel(self, text=localization.get_text("Backup & Restore"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=self.card_fg_color,
            segmented_button_fg_color=self.segmented_button_unselected_color,
            segmented_button_selected_color=self.segmented_button_selected_color,
            segmented_button_selected_hover_color=self.border_color,
            segmented_button_unselected_color=self.segmented_button_unselected_color,
            segmented_button_unselected_hover_color=self.hover_color,
            corner_radius=12,
            border_width=2,
            border_color=self.border_color,
            text_color=self.tab_text_color
        )
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        # System Repair Tab
        self.tab_view.add(localization.get_text("System Repair"))
        self.system_repair_view = SystemRepairView(self.tab_view.tab(localization.get_text("System Repair")))
        self.system_repair_view.pack(expand=True, fill="both")
        self.system_repair_view.configure(fg_color=self.card_fg_color)
        # Backup Tab
        self.tab_view.add(localization.get_text("Backup"))
        backup_tab_frame = self.tab_view.tab(localization.get_text("Backup"))
        backup_tab_frame.configure(fg_color=self.card_fg_color)
        
        # Backup functions with descriptions
        backup_functions = [
            (localization.get_text("Create System Image"), "create_system_image_desc", actions.create_system_image, "Run"),
            (localization.get_text("Backup Files and Folders"), "backup_files_folders_desc", actions.backup_files_folders, "Run"),
        ]
        self._create_function_table(backup_tab_frame, backup_functions)

        # Restore Tab
        self.tab_view.add(localization.get_text("Restore"))
        restore_tab_frame = self.tab_view.tab(localization.get_text("Restore"))
        restore_tab_frame.configure(fg_color=self.card_fg_color)

        # Restore functions with descriptions
        restore_functions = [
            (localization.get_text("System Restore"), "system_restore_desc", actions.system_restore, "Run"),
            (localization.get_text("Restore Files and Folders"), "restore_files_folders_desc", actions.restore_files_folders, "Run"),
            (localization.get_text("Create Recovery Drive"), "create_recovery_drive_desc", actions.open_recovery_drive_creator, "Run"),
        ]
        self._create_function_table(restore_tab_frame, restore_functions)

        # Printer Management Tab
        self.tab_view.add(localization.get_text("Printer Management"))
        self.printer_management_view = PrinterManagementView(self.tab_view.tab(localization.get_text("Printer Management")))
        self.printer_management_view.pack(expand=True, fill="both")
        self.printer_management_view.configure(fg_color=self.card_fg_color)

    def _create_function_table(self, parent_frame, functions_list):
        parent_frame.grid_columnconfigure(0, weight=1) # Function Name
        parent_frame.grid_columnconfigure(1, weight=3) # Description
        parent_frame.grid_columnconfigure(2, weight=1) # Action Button

        # Header Row
        ctk.CTkLabel(parent_frame, text=localization.get_text("Function Name"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(parent_frame, text=localization.get_text("Description"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(parent_frame, text=localization.get_text("Action"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        for i, (text, desc_key, command, button_text) in enumerate(functions_list):
            row_num = i + 1 # Start from row 1 after header

            ctk.CTkLabel(
                parent_frame,
                text=text,
                font=self.STYLE["font_info"],
                anchor="w",
                text_color=self.text_color
            ).grid(row=row_num, column=0, sticky="nw", padx=(5, 10), pady=2)

            ctk.CTkLabel(
                parent_frame,
                text=localization.get_text(desc_key),
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            ).grid(row=row_num, column=1, sticky="ew", padx=(0, 5), pady=2)

            action_button = ctk.CTkButton(
                parent_frame,
                text=localization.get_text(button_text),
                command=command,
                font=self.STYLE["font_info"],
                width=80
            )
            action_button.grid(row=row_num, column=2, sticky="nsew", padx=5, pady=2)

    def cancel_updates(self, *args, **kwargs):
        if hasattr(self.system_repair_view, 'cancel_updates'):
            self.system_repair_view.cancel_updates(*args, **kwargs)
        if hasattr(self.printer_management_view, 'cancel_updates'):
            self.printer_management_view.cancel_updates(*args, **kwargs)
