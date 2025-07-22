import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from logic import logic, actions, localization

class UpdateView(ctk.CTkFrame):
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

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._set_colors()

        # Initialize status labels
        self.system_update_status = None
        self.app_update_status = None
        self.driver_update_status = None

        ctk.CTkLabel(self, text=localization.get_text("Cập nhật và bảo mật"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

        tab_view = ctk.CTkTabview(
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
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        update_settings_tab = tab_view.add(localization.get_text("Cập nhật"))
        update_settings_tab.configure(fg_color=self.card_fg_color)
        security_tab = tab_view.add(localization.get_text("Bảo mật"))
        security_tab.configure(fg_color=self.card_fg_color)

        self._create_update_settings_tab(update_settings_tab)
        self._create_security_tab(security_tab)


    def _create_update_settings_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        # Update functions with descriptions
        update_functions = [
            (localization.get_text("System Update"), "check_windows_update_desc", actions.check_windows_update, "system_update_status"),
            (localization.get_text("Application Updates"), "update_applications_desc", actions.update_applications, "app_update_status"),
            (localization.get_text("Driver Updates"), "update_drivers_desc", actions.update_drivers, "driver_update_status"),
            (localization.get_text("Export Hardware Info"), "export_hardware_info_desc", actions.export_hardware_info_to_txt, None),
        ]

        for i, (text, desc_key, command, status_label_attr) in enumerate(update_functions):
            frame = ctk.CTkFrame(tab, fg_color=self.card_fg_color)
            frame.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(frame, text=text).pack(side="left", padx=10)
            if status_label_attr:
                status_label_widget = ctk.CTkLabel(frame, text=localization.get_text("Last checked: N/A"))
                status_label_widget.pack(side="left", padx=10)
                setattr(self, status_label_attr, status_label_widget) # Dynamically set the status label attribute

            ctk.CTkButton(frame, text=localization.get_text("Check for Updates"), command=lambda cmd=command, name=text, sl_attr=status_label_attr: self.run_action(cmd, name, getattr(self, sl_attr) if sl_attr else None)).pack(side="right", padx=10)
            
            description_label = ctk.CTkLabel(frame, text=localization.get_text(desc_key), wraplength=400, justify="left", font=("Arial", 10))
            description_label.pack(pady=(0, 10), padx=20, anchor="w")


    def _create_security_tab(self, tab):
        self.scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent", corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0,5))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.populate_security_info()

    def populate_security_info(self):
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # System Security Section
        system_security_items = [
            (localization.get_text("Firewall Status"), logic.get_firewall_status(), actions.open_firewall_settings, "Open Settings", "open_firewall_settings_desc"),
            (localization.get_text("Antivirus"), logic.get_antivirus_info(), None, None, None),
            (localization.get_text("Windows Update"), localization.get_text("Click to check"), actions.check_windows_update, "Check", "check_windows_update_desc"),
            (localization.get_text("Windows Defender"), logic.get_windows_defender_status(), actions.open_windows_defender_settings, "Open Settings", "open_windows_defender_settings_desc"),
            (localization.get_text("User Account Control (UAC)"), logic.get_uac_status(), actions.open_uac_settings, "Open Settings", "open_uac_settings_desc"),
        ]

        # Filter out Antivirus if status is Unknown or Not found
        antivirus_status = logic.get_antivirus_info()
        if antivirus_status in ["Unknown", "Not found", "WMI not available"]:
            system_security_items = [item for item in system_security_items if item[0] != localization.get_text("Antivirus")]

        self._create_section(
            self.scrollable_frame,
            localization.get_text("System Security"),
            system_security_items
        )

        # Firewall & Network Protection Section
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Firewall & Network Protection"),
            [
                (localization.get_text("Enable Firewall"), localization.get_text("Click to enable"), actions.enable_firewall, "Enable", "enable_firewall_desc"),
                (localization.get_text("Disable Firewall"), localization.get_text("Click to disable"), actions.disable_firewall, "Disable", "disable_firewall_desc"),
            ]
        )

        # Virus & Threat Protection Section
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Virus & Threat Protection"),
            [
                (localization.get_text("Real-time Protection"), logic.get_windows_defender_realtime_protection_status(), lambda: actions.toggle_windows_defender_realtime_protection(True), "Enable", "toggle_realtime_protection_desc"),
                (localization.get_text("Real-time Protection"), logic.get_windows_defender_realtime_protection_status(), lambda: actions.toggle_windows_defender_realtime_protection(False), "Disable", "toggle_realtime_protection_desc"),
                (localization.get_text("Virus Definitions"), localization.get_text("Last updated: N/A"), actions.update_virus_definitions, "Update", "update_virus_definitions_desc"),
            ]
        )

        # Drive Encryption Section
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Drive Encryption"),
            [
                (localization.get_text("BitLocker Status"), logic.get_bitlocker_status(), actions.open_bitlocker_settings, "Open Settings", "open_bitlocker_settings_desc"),
            ]
        )

        # Security Scans Section
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Security Scans"),
            [
                (localization.get_text("Quick Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "run_quick_scan_desc", "quick"),
                (localization.get_text("Full Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "run_full_scan_desc", "full"),
                (localization.get_text("Custom Scan"), localization.get_text("Click to run"), actions.run_windows_defender_scan, "Run Scan", "run_custom_scan_desc", "custom"),
            ]
        )

        # New sections for Update & Security
        # Windows Security
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Windows Security"),
            [
                (localization.get_text("Open Windows Security"), localization.get_text("Manage security settings"), actions.open_windows_security, "Open", "open_windows_security_desc"),
            ]
        )

        # Account Protection
        self._create_section(
            self.scrollable_frame,
            localization.get_text("Account Protection"),
            [
                (localization.get_text("Manage Account Settings"), localization.get_text("View and manage your account"), actions.open_account_settings, "Open", "open_account_settings_desc"),
            ]
        )

        # App & Browser Control
        self._create_section(
            self.scrollable_frame,
            localization.get_text("App & Browser Control"),
            [
                (localization.get_text("Manage App & Browser Control"), localization.get_text("Control app and browser behavior"), actions.open_app_browser_control, "Open", "open_app_browser_control_desc"),
            ]
        )

    def run_action(self, action, action_name, status_label=None):
        try:
            result = action()
            if result:
                CTkMessagebox(title=localization.get_text("Success"), message=f"{action_name}: {result}")
            else:
                CTkMessagebox(title=localization.get_text("Success"), message=f"{action_name} {localization.get_text('completed successfully')}.")
            if status_label:
                from datetime import datetime
                status_label.configure(text=f"{localization.get_text('Last checked:')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            CTkMessagebox(title=localization.get_text("Error"), message=f"{localization.get_text('An error occurred during')} {action_name}: {e}", icon="cancel")

    def _create_section(self, parent, title, items):
        section_container = ctk.CTkFrame(
            parent,
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
        content_frame.grid_columnconfigure(0, weight=1) # Function Name
        content_frame.grid_columnconfigure(1, weight=3) # Description
        content_frame.grid_columnconfigure(2, weight=1) # Status/Action Button

        # Header Row
        ctk.CTkLabel(content_frame, text=localization.get_text("Function Name"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(content_frame, text=localization.get_text("Description"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(content_frame, text=localization.get_text("Status"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        for i, item_data in enumerate(items):
            key, value, action_command, button_text_key, desc_key = item_data[0], item_data[1], item_data[2], item_data[3], item_data[4]
            scan_type = item_data[5] if len(item_data) > 5 else None

            row_num = i + 1 # Start from row 1 after header

            key_label = ctk.CTkLabel(
                content_frame,
                text=key,
                font=self.STYLE["font_info"],
                anchor="w",
                text_color=self.text_color
            )
            key_label.grid(row=row_num, column=0, sticky="nw", padx=(5, 10), pady=2)

            description_label = ctk.CTkLabel(
                content_frame,
                text=localization.get_text(desc_key),
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            )
            description_label.grid(row=row_num, column=1, sticky="ew", padx=(0, 5), pady=2)

            if action_command:
                if scan_type:
                    action_button = ctk.CTkButton(
                        content_frame,
                        text=localization.get_text(button_text_key),
                        command=lambda s=scan_type, cmd=action_command, name=key: self.run_action(lambda: cmd(s), name),
                        font=self.STYLE["font_info"],
                        width=80
                    )
                else:
                    action_button = ctk.CTkButton(
                        content_frame,
                        text=localization.get_text(button_text_key),
                        command=lambda cmd=action_command, name=key: self.run_action(cmd, name),
                        font=self.STYLE["font_info"],
                        width=80
                    )
                action_button.grid(row=row_num, column=2, sticky="nsew", padx=5, pady=2)
            else:
                # Display current status if no action button
                status_color = self.text_color
                if isinstance(value, str):
                    if value.lower() in ["on", "enabled", "running"]:
                        status_color = self.status_ok_color
                    elif value.lower() in ["off", "disabled", "stopped"]:
                        status_color = self.status_bad_color

                status_label = ctk.CTkLabel(
                    content_frame,
                    text=value,
                    font=self.STYLE["font_info"],
                    anchor="w",
                    wraplength=100,
                    justify="left",
                    text_color=status_color
                )
                status_label.grid(row=row_num, column=2, sticky="ew", padx=(0, 5), pady=2)

    def cancel_updates(self, *args, **kwargs):
        # This view has no scheduled updates
        pass