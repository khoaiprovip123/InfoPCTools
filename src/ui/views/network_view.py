import customtkinter as ctk
from logic import logic, localization, actions
from CTkMessagebox import CTkMessagebox

class NetworkView(ctk.CTkFrame):
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

        self.active_after_ids = {}

        ctk.CTkLabel(self, text=localization.get_text("Network"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

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

        network_info_tab = self.tab_view.add(localization.get_text("Network Configuration"))
        network_info_tab.configure(fg_color=self.card_fg_color)
        network_tools_tab = self.tab_view.add(localization.get_text("Network Tools"))
        network_tools_tab.configure(fg_color=self.card_fg_color)

        self._create_network_config_tab(network_info_tab)
        self._create_network_tools_tab(network_tools_tab)

        self.update_connections()

    def _create_network_config_tab(self, tab):
        # Network Configuration Table
        config_title_label = ctk.CTkLabel(tab, text=localization.get_text("Network Configuration"), font=self.STYLE["font_card_header"], text_color=self.text_color)
        config_title_label.pack(anchor="w", padx=10, pady=5)

        config_table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        config_table_frame.pack(fill="x", expand=True, padx=10, pady=5)

        # Table Headers
        config_table_frame.grid_columnconfigure(0, weight=1)
        config_table_frame.grid_columnconfigure(1, weight=1)
        config_table_frame.grid_columnconfigure(2, weight=1)
        config_table_frame.grid_columnconfigure(3, weight=1)
        config_table_frame.grid_columnconfigure(4, weight=1)
        config_table_frame.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(config_table_frame, text=localization.get_text("Interface"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(config_table_frame, text=localization.get_text("IP Address"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(config_table_frame, text=localization.get_text("Netmask"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(config_table_frame, text=localization.get_text("Gateway"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(config_table_frame, text=localization.get_text("MAC Address"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=4, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(config_table_frame, text=localization.get_text("DHCP Enabled"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=5, sticky="ew", padx=5, pady=2)

        for i, config in enumerate(logic.get_network_config()):
            row_num = i + 1
            ctk.CTkLabel(config_table_frame, text=config['interface'], text_color=self.text_color).grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(config_table_frame, text=config['address'], text_color=self.text_color).grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(config_table_frame, text=config['netmask'], text_color=self.text_color).grid(row=row_num, column=2, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(config_table_frame, text=config['gateway'], text_color=self.text_color).grid(row=row_num, column=3, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(config_table_frame, text=config['mac_address'], text_color=self.text_color).grid(row=row_num, column=4, sticky="ew", padx=5, pady=2)
            ctk.CTkLabel(config_table_frame, text=config['dhcp_enabled'], text_color=self.text_color).grid(row=row_num, column=5, sticky="ew", padx=5, pady=2)

        # Active Network Connections
        connections_title_label = ctk.CTkLabel(tab, text=localization.get_text("Active Network Connections"), font=self.STYLE["font_card_header"], text_color=self.text_color)
        connections_title_label.pack(anchor="w", padx=10, pady=5)
        
        self.scrollable_connections = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.scrollable_connections.pack(fill="both", expand=True)

        # Table Headers for Active Connections
        self.scrollable_connections.grid_columnconfigure(0, weight=1) # PID
        self.scrollable_connections.grid_columnconfigure(1, weight=2) # Process Name
        self.scrollable_connections.grid_columnconfigure(2, weight=2) # Remote Address

        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("PID"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("Process Name"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("Remote Address"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

    def _create_network_tools_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1) # Function Name
        tab.grid_columnconfigure(1, weight=3) # Description
        tab.grid_columnconfigure(2, weight=1) # Action Button

        # Header Row
        ctk.CTkLabel(tab, text=localization.get_text("Function Name"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(tab, text=localization.get_text("Description"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(tab, text=localization.get_text("Action"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        network_functions = [
            (localization.get_text("Flush DNS"), "flush_dns_desc", actions.flush_dns, "Run"),
            (localization.get_text("Release IP"), "release_ip_desc", actions.release_ip, "Run"),
            (localization.get_text("Renew IP"), "renew_ip_desc", actions.renew_ip, "Run"),
            (localization.get_text("Open Network and Sharing Center"), "open_network_sharing_center_desc", actions.open_network_sharing_center, "Open"),
            (localization.get_text("Ping Host"), "ping_host_desc", actions.ping_host, "Run"),
            (localization.get_text("Set DNS"), "set_dns_desc", actions.set_dns, "Configure"),
            (localization.get_text("Set Static IP"), "set_static_ip_desc", actions.set_static_ip, "Configure"),
        ]

        for i, (text, desc_key, command, button_text) in enumerate(network_functions):
            row_num = i + 1 # Start from row 1 after header

            ctk.CTkLabel(
                tab,
                text=text,
                font=self.STYLE["font_info"],
                anchor="w",
                text_color=self.text_color
            ).grid(row=row_num, column=0, sticky="nw", padx=(5, 10), pady=2)

            ctk.CTkLabel(
                tab,
                text=localization.get_text(desc_key),
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            ).grid(row=row_num, column=1, sticky="ew", padx=(0, 5), pady=2)

            action_button = ctk.CTkButton(
                tab,
                text=localization.get_text(button_text),
                command=command,
                font=self.STYLE["font_info"],
                width=80
            )
            action_button.grid(row=row_num, column=2, sticky="nsew", padx=5, pady=2)

    def update_connections(self):
        for widget in self.scrollable_connections.winfo_children():
            widget.destroy()
        
        # Add headers for the active connections table
        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("PID"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("Process Name"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("Remote Address"), font=self.STYLE["font_info_bold"], text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        connections = logic.get_active_connections()
        if connections and isinstance(connections[0], dict):
            for i, conn_info in enumerate(connections):
                row_num = i + 1
                ctk.CTkLabel(self.scrollable_connections, text=conn_info.get("pid", "N/A"), text_color=self.text_color).grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
                ctk.CTkLabel(self.scrollable_connections, text=conn_info.get("process_name", "N/A"), text_color=self.text_color).grid(row=row_num, column=1, sticky="ew", padx=5, pady=2)
                ctk.CTkLabel(self.scrollable_connections, text=conn_info.get("remote_address", "N/A"), text_color=self.text_color).grid(row=row_num, column=2, sticky="ew", padx=5, pady=2)
        else:
            ctk.CTkLabel(self.scrollable_connections, text=localization.get_text("access_denied_connections"), text_color=self.text_color).grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        self.active_after_ids["network_update"] = self.after(5000, self.update_connections)

    def cancel_updates(self, *args, **kwargs):
        for after_id in self.active_after_ids.values():
            self.after_cancel(after_id)
        self.active_after_ids.clear()
