import customtkinter as ctk
from logic import logic, actions, localization

class SecurityView(ctk.CTkFrame):
    STYLE = {
        "font_family": "Roboto",
        "font_title": ("Roboto", 24, "bold"),
        "font_card_header": ("Roboto", 14, "bold"),
        "font_info": ("Roboto", 11),
        "font_info_bold": ("Roboto", 11, "bold"),
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._set_colors()

        ctk.CTkLabel(self, text=localization.get_text("Security"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0,5))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.populate_security_info()

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
            self.border_color = "#5C6370"
            self.hover_color = "#3E3E3E"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.border_color = "#DCE4EE"
            self.hover_color = "#CFCFCF"

    def populate_security_info(self):
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # System Security Section
        system_security_items = [
            (localization.get_text("Firewall Status"), logic.get_firewall_status(), actions.open_firewall_settings, "Open Settings"),
            (localization.get_text("Antivirus"), logic.get_antivirus_info(), None, None),
            (localization.get_text("Windows Update"), localization.get_text("Click to check"), actions.check_windows_update, "Check"),
            (localization.get_text("Windows Defender"), logic.get_windows_defender_status(), actions.open_windows_defender_settings, "Open Settings"),
            (localization.get_text("User Account Control (UAC)"), logic.get_uac_status(), actions.open_uac_settings, "Open Settings"),
        ]

        # Filter out Antivirus if status is Unknown or Not found
        antivirus_status = logic.get_antivirus_info()
        if antivirus_status in ["Unknown", "Not found", "WMI not available"]:
            system_security_items = [item for item in system_security_items if item[0] != localization.get_text("Antivirus")]

        self._create_section(
            localization.get_text("System Security"),
            system_security_items
        )

        # Firewall & Network Protection Section
        self._create_section(
            localization.get_text("Firewall & Network Protection"),
            [
                (localization.get_text("Firewall Status"), logic.get_firewall_status(), actions.enable_firewall, "Enable"),
                (localization.get_text("Firewall Status"), logic.get_firewall_status(), actions.disable_firewall, "Disable"),
            ]
        )

        # Virus & Threat Protection Section
        self._create_section(
            localization.get_text("Virus & Threat Protection"),
            [
                (localization.get_text("Real-time Protection"), logic.get_windows_defender_realtime_protection_status(), lambda: actions.toggle_windows_defender_realtime_protection(True), "Enable"),
                (localization.get_text("Real-time Protection"), logic.get_windows_defender_realtime_protection_status(), lambda: actions.toggle_windows_defender_realtime_protection(False), "Disable"),
                (localization.get_text("Virus Definitions"), localization.get_text("Last updated: N/A"), actions.update_virus_definitions, "Update"),
            ]
        )

        # Drive Encryption Section
        self._create_section(
            localization.get_text("Drive Encryption"),
            [
                (localization.get_text("BitLocker Status"), logic.get_bitlocker_status(), actions.open_bitlocker_settings, "Open Settings"),
            ]
        )

        # Security Scans Section
        self._create_section(
            localization.get_text("Security Scans"),
            [
                (localization.get_text("Quick Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "quick"),
                (localization.get_text("Full Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "full"),
                (localization.get_text("Custom Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "custom"),
            ]
        )

        # Application Updates Section
        self._create_section(
            localization.get_text("Application Updates"),
            [
                (localization.get_text("Check for App Updates"), localization.get_text("Last checked: N/A"), actions.update_applications, "Check"),
            ]
        )

    def _create_section(self, title, items):
        section_container = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=self.card_fg_color,
            corner_radius=8,
            border_width=1,
            border_color=self.border_color
        )
        section_container.pack(fill="x", padx=5, pady=8, expand=True)

        title_label = ctk.CTkLabel(section_container, text=title, font=self.STYLE["font_card_header"], text_color=self.text_color)
        title_label.pack(anchor="w", padx=15, pady=(10, 5))

        content_frame = ctk.CTkFrame(section_container, fg_color="transparent")
        content_frame.pack(fill="x", expand=True, padx=15, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        for i, item_data in enumerate(items):
            key, value, action_command, button_text_key = item_data[0], item_data[1], item_data[2], item_data[3]
            scan_type = item_data[4] if len(item_data) > 4 else None

            key_label = ctk.CTkLabel(
                content_frame,
                text=f"{key}:",
                font=self.STYLE["font_info_bold"],
                anchor="w",
                text_color=self.text_color
            )
            key_label.grid(row=i, column=0, sticky="nw", padx=(5, 10), pady=2)

            value_label = ctk.CTkLabel(
                content_frame,
                text=value,
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            )
            if not action_command: # Only grid if no action command
                value_label.grid(row=i, column=1, sticky="ew", padx=(0, 5), pady=2)

            if action_command:
                if scan_type:
                    action_button = ctk.CTkButton(
                        content_frame,
                        text=localization.get_text(button_text_key),
                        command=lambda s=scan_type: action_command(s),
                        font=self.STYLE["font_info"],
                        width=80
                    )
                else:
                    action_button = ctk.CTkButton(
                        content_frame,
                        text=localization.get_text(button_text_key),
                        command=action_command,
                        font=self.STYLE["font_info"],
                        width=80
                    )
                action_button.grid(row=i, column=1, sticky="e", padx=5, pady=2)

    def cancel_updates(self):
        # This view has no scheduled updates
        pass
