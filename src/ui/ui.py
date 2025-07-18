import customtkinter as ctk
from PIL import Image
from logic import logic
from logic import actions
from logic import localization

class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.active_after_ids = {}

        self.title(localization.get_text("app_title"))
        self.geometry("1100x700")
        self.resizable(False, False)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        main_container = ctk.CTkFrame(self)
        main_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        logo_image = ctk.CTkImage(Image.open("assets/logo/hpc-logo.png"), size=(150, 150))
        logo_label = ctk.CTkLabel(sidebar, image=logo_image, text="")
        logo_label.pack(pady=20)

        menu_buttons = [
            (localization.get_text("Dashboard"), "assets/icons/dashboard.png", self.show_dashboard),
            (localization.get_text("Hardware Info"), "assets/icons/system.png", self.show_hardware_info),
            (localization.get_text("Applications"), "assets/icons/utilities.png", self.show_applications),
            (localization.get_text("Security"), "assets/icons/security.png", self.show_security),
            (localization.get_text("Network"), "assets/icons/network.png", self.show_network),
            (localization.get_text("Repair & Restore"), "assets/icons/system_fix.png", self.show_repair_restore),
            (localization.get_text("Settings"), "assets/icons/optimize.png", self.show_settings)
        ]

        for text, icon_path, command in menu_buttons:
            image = ctk.CTkImage(Image.open(icon_path), size=(24, 24))
            button = ctk.CTkButton(sidebar, text=text, image=image, anchor="w", command=command)
            button.pack(fill="x", padx=10, pady=5)

        self.content_frames = {}
        for name in ["Dashboard", "Hardware Info", "Applications", "Security", "Network", "Repair & Restore", "Settings"]:
            frame = ctk.CTkFrame(main_container)
            self.content_frames[name] = frame

        self.show_dashboard()
        self.active_after_ids = {}

    def show_frame(self, name):
        # Cancel any pending 'after' calls
        for after_id in list(self.active_after_ids.values()):
            self.after_cancel(after_id)
        self.active_after_ids.clear()

        for frame_name, frame in self.content_frames.items():
            if frame_name == name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def show_dashboard(self):
        self.show_frame("Dashboard")
        dashboard_frame = self.content_frames["Dashboard"]
        for widget in dashboard_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(dashboard_frame, text=localization.get_text("Dashboard"), font=("Arial", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Configure grid layout (2x2 for main stats, 1 row for disk)
        dashboard_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        dashboard_frame.grid_rowconfigure(1, weight=1, uniform="group1") # CPU/RAM row
        dashboard_frame.grid_rowconfigure(2, weight=1, uniform="group1") # System/Network row
        dashboard_frame.grid_rowconfigure(3, weight=2) # Disk row

        # --- CPU ---
        cpu_frame = ctk.CTkFrame(dashboard_frame)
        cpu_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        cpu_frame.grid_propagate(False)
        cpu_icon = ctk.CTkImage(Image.open("assets/icons/system.png"), size=(30, 30))
        ctk.CTkLabel(cpu_frame, text=localization.get_text("CPU Usage"), image=cpu_icon, compound="left", font=("Arial", 18, "bold")).pack(pady=(10,0))
        self.cpu_percent_label = ctk.CTkLabel(cpu_frame, text="", font=("Arial", 36, "bold"))
        self.cpu_percent_label.pack(expand=True)
        self.cpu_name_label = ctk.CTkLabel(cpu_frame, text="", font=("Arial", 12))
        self.cpu_name_label.pack(pady=(0,5))
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame, height=10)
        self.cpu_progress.pack(fill="x", padx=20, pady=(0,15))

        # --- RAM ---
        ram_frame = ctk.CTkFrame(dashboard_frame)
        ram_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ram_frame.grid_propagate(False)
        ram_icon = ctk.CTkImage(Image.open("assets/icons/system.png"), size=(30, 30))
        ctk.CTkLabel(ram_frame, text=localization.get_text("RAM Usage"), image=ram_icon, compound="left", font=("Arial", 18, "bold")).pack(pady=(10,0))
        self.ram_percent_label = ctk.CTkLabel(ram_frame, text="", font=("Arial", 36, "bold"))
        self.ram_percent_label.pack(expand=True)
        self.ram_detail_label = ctk.CTkLabel(ram_frame, text="", font=("Arial", 12))
        self.ram_detail_label.pack(pady=(0,5))
        self.ram_progress = ctk.CTkProgressBar(ram_frame, height=10)
        self.ram_progress.pack(fill="x", padx=20, pady=(0,15))

        # --- System Info ---
        system_frame = ctk.CTkFrame(dashboard_frame)
        system_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        system_frame.grid_propagate(False)
        system_icon = ctk.CTkImage(Image.open("assets/icons/system.png"), size=(30, 30))
        ctk.CTkLabel(system_frame, text=localization.get_text("System Info"), image=system_icon, compound="left", font=("Arial", 18, "bold")).pack(pady=(10,5))
        self.os_label = ctk.CTkLabel(system_frame, text="", font=("Arial", 14))
        self.os_label.pack(pady=5, padx=20, anchor="w")
        self.hostname_label = ctk.CTkLabel(system_frame, text="", font=("Arial", 14))
        self.hostname_label.pack(pady=5, padx=20, anchor="w")
        self.uptime_label = ctk.CTkLabel(system_frame, text="", font=("Arial", 14))
        self.uptime_label.pack(pady=5, padx=20, anchor="w")

        # --- Network Info ---
        network_frame = ctk.CTkFrame(dashboard_frame)
        network_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        network_frame.grid_propagate(False)
        network_icon = ctk.CTkImage(Image.open("assets/icons/network.png"), size=(30, 30))
        ctk.CTkLabel(network_frame, text=localization.get_text("Network"), image=network_icon, compound="left", font=("Arial", 18, "bold")).pack(pady=(10,5))
        self.ip_label = ctk.CTkLabel(network_frame, text="", font=("Arial", 14))
        self.ip_label.pack(pady=5, padx=20, anchor="w")
        self.net_down_label = ctk.CTkLabel(network_frame, text="", font=("Arial", 14))
        self.net_down_label.pack(pady=5, padx=20, anchor="w")
        self.net_up_label = ctk.CTkLabel(network_frame, text="", font=("Arial", 14))
        self.net_up_label.pack(pady=5, padx=20, anchor="w")

        # --- Disk ---
        disk_frame = ctk.CTkFrame(dashboard_frame)
        disk_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        disk_icon = ctk.CTkImage(Image.open("assets/icons/system.png"), size=(30, 30))
        ctk.CTkLabel(disk_frame, text=localization.get_text("Disk Usage"), image=disk_icon, compound="left", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)
        self.disk_info_frame = ctk.CTkFrame(disk_frame, fg_color="transparent")
        self.disk_info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.update_dashboard()

    def update_dashboard(self):
        # Update CPU
        cpu_percent = logic.get_cpu_usage()
        cpu_name = logic.get_cpu_name()
        self.cpu_percent_label.configure(text=f"{cpu_percent:.1f}%")
        self.cpu_name_label.configure(text=cpu_name)
        self.cpu_progress.set(cpu_percent / 100)

        # Update RAM
        ram_percent, ram_detail = logic.get_ram_usage()
        self.ram_percent_label.configure(text=f"{ram_percent:.1f}%")
        self.ram_detail_label.configure(text=ram_detail)
        self.ram_progress.set(ram_percent / 100)

        # Update System Info
        system_summary = logic.get_system_summary()
        self.os_label.configure(text=f"{localization.get_text("OS")}: {system_summary['os']}")
        self.hostname_label.configure(text=f"{localization.get_text("Hostname")}: {system_summary['hostname']}")
        self.uptime_label.configure(text=f"{localization.get_text("Uptime")}: {system_summary['uptime']}")

        # Update Network
        bytes_recv, bytes_sent = logic.get_network_usage()
        self.ip_label.configure(text=f"{localization.get_text("Local IP")}: {logic.get_local_ip()}")
        self.net_down_label.configure(text=f"\u2193 {localization.get_text("Download")}: {bytes_recv / (1024**2):.2f} MB")
        self.net_up_label.configure(text=f"\u2191 {localization.get_text("Upload")}: {bytes_sent / (1024**2):.2f} MB")

        # Update Disk
        for widget in self.disk_info_frame.winfo_children():
            widget.destroy()
        for i, disk in enumerate(logic.get_disk_usage()):
            disk_entry = ctk.CTkFrame(self.disk_info_frame)
            disk_entry.pack(fill="x", pady=2)
            label = ctk.CTkLabel(disk_entry, text=f"{disk['device']} ({disk['fstype']}) - {disk['total'] / (1024**3):.1f} GB", anchor="w")
            label.pack(side="left", padx=10)
            percent_label = ctk.CTkLabel(disk_entry, text=f"{disk['percent']}%")
            percent_label.pack(side="right", padx=10)
            progress = ctk.CTkProgressBar(disk_entry, height=8)
            progress.set(disk['percent'] / 100)
            progress.pack(side="right", fill="x", expand=True, padx=5)

        self.active_after_ids["dashboard_update"] = self.after(1000, self.update_dashboard)

    def show_hardware_info(self):
        self.show_frame("Hardware Info")
        hardware_frame = self.content_frames["Hardware Info"]
        for widget in hardware_frame.winfo_children():
            widget.destroy()

        info, error = logic.get_hardware_info()
        if error:
            ctk.CTkLabel(hardware_frame, text=localization.get_text("error_occurred").format(e=error), font=("Arial", 16)).pack(pady=20)
            return

        scrollable_frame = ctk.CTkScrollableFrame(hardware_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for title, info_dict in info.items():
            section_frame = ctk.CTkFrame(scrollable_frame, corner_radius=5)
            section_frame.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(section_frame, text=localization.get_text(title), font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
            for key, value in info_dict.items():
                info_entry = ctk.CTkFrame(section_frame)
                info_entry.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(info_entry, text=localization.get_text(key), anchor="w", width=200).pack(side="left")
                ctk.CTkLabel(info_entry, text=value, anchor="w").pack(side="left")

    def show_applications(self):
        self.show_frame("Applications")
        applications_frame = self.content_frames["Applications"]
        for widget in applications_frame.winfo_children():
            widget.destroy()

        tab_view = ctk.CTkTabview(applications_frame)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        installed_tab = tab_view.add(localization.get_text("Installed Apps"))
        startup_tab = tab_view.add(localization.get_text("Startup Apps"))

        installed_frame = ctk.CTkScrollableFrame(installed_tab)
        installed_frame.pack(fill="both", expand=True)
        for name, publisher, date in logic.get_installed_apps():
            app_entry = ctk.CTkFrame(installed_frame)
            app_entry.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(app_entry, text=f"{name} - {publisher} ({date})").pack(side="left", padx=5, expand=True, anchor="w")
            ctk.CTkButton(app_entry, text=localization.get_text("Uninstall"), width=80).pack(side="right", padx=5)

        startup_frame = ctk.CTkScrollableFrame(startup_tab)
        startup_frame.pack(fill="both", expand=True)
        for name, path in logic.get_startup_apps():
            startup_entry = ctk.CTkFrame(startup_frame)
            startup_entry.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(startup_entry, text=f"{name}\n{path}").pack(side="left", padx=5, expand=True, anchor="w")
            switch = ctk.CTkSwitch(startup_entry, text="")
            switch.pack(side="right", padx=5)
            switch.select()

    def show_security(self):
        self.show_frame("Security")
        security_frame = self.content_frames["Security"]
        for widget in security_frame.winfo_children():
            widget.destroy()

        security_info = {
            localization.get_text("Firewall Status"): logic.get_firewall_status(),
            localization.get_text("Antivirus"): logic.get_antivirus_info(),
            localization.get_text("Windows Update"): localization.get_text("Click to check")
        }

        for key, value in security_info.items():
            info_entry = ctk.CTkFrame(security_frame)
            info_entry.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(info_entry, text=key, anchor="w", width=150).pack(side="left")
            ctk.CTkLabel(info_entry, text=value, anchor="w").pack(side="left")
            if key == localization.get_text("Windows Update"):
                ctk.CTkButton(info_entry, text=localization.get_text("Check"), command=actions.check_windows_update).pack(side="right", padx=5)
            elif key == localization.get_text("Firewall Status"):
                ctk.CTkButton(info_entry, text=localization.get_text("Settings"), command=actions.open_firewall_settings).pack(side="right", padx=5)

    def show_network(self):
        self.show_frame("Network")
        network_frame = self.content_frames["Network"]
        for widget in network_frame.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(network_frame)
        config_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(config_frame, text=localization.get_text("Network Configuration"), font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        for config in logic.get_network_config():
            ctk.CTkLabel(config_frame, text=f"{localization.get_text("Interface")}: {config['interface']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(config_frame, text=f"  {localization.get_text("IP Address")}: {config['address']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(config_frame, text=f"  {localization.get_text("Netmask")}: {config['netmask']}").pack(anchor="w", padx=10)

        connections_frame = ctk.CTkFrame(network_frame)
        connections_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(connections_frame, text=localization.get_text("Active Network Connections"), font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        scrollable_connections = ctk.CTkScrollableFrame(connections_frame)
        scrollable_connections.pack(fill="both", expand=True)

        def update_connections():
            for widget in scrollable_connections.winfo_children():
                widget.destroy()
            for conn_info in logic.get_active_connections():
                ctk.CTkLabel(scrollable_connections, text=conn_info).pack(anchor="w")
            self.active_after_ids["network_update"] = self.after(5000, update_connections)

        update_connections()

    def show_repair_restore(self):
        self.show_frame("Repair & Restore")
        repair_frame = self.content_frames["Repair & Restore"]
        for widget in repair_frame.winfo_children():
            widget.destroy()

        repair_options = {
            localization.get_text("Scan and Fix System Files"): "sfc /scannow",
            localization.get_text("Troubleshoot Print Spooler"): "net stop spooler && del %systemroot%\\System32\\spool\\printers\\* /Q /F /S && net start spooler",
            localization.get_text("Open Device Manager"): "devmgmt.msc",
            localization.get_text("Create System Restore Point"): "systempropertiesprotection.exe",
            localization.get_text("Backup Drivers"): "pnputil /export-driver * ."
        }
        
        ctk.CTkLabel(repair_frame, text=localization.get_text("driver_backup_info")).pack(pady=5, padx=20, anchor="w")

        for text, command in repair_options.items():
            is_backup = (text == localization.get_text("Backup Drivers"))
            button = ctk.CTkButton(repair_frame, text=text, command=lambda c=command, b=is_backup: actions.run_repair_command(c, b))
            button.pack(pady=10, padx=20, fill="x")

    def show_settings(self):
        self.show_frame("Settings")
        settings_frame = self.content_frames["Settings"]
        for widget in settings_frame.winfo_children():
            widget.destroy()

        # Application Info
        app_info_frame = ctk.CTkFrame(settings_frame)
        app_info_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Application Information"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        ctk.CTkLabel(app_info_frame, text=f"{localization.get_text("Version")}: 1.0").pack(anchor="w", padx=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Developed by Gemini AI from Google.")).pack(anchor="w", padx=10)

        # Theme Settings
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(theme_frame, text=localization.get_text("Theme Settings"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        self.theme_switch = ctk.CTkSwitch(theme_frame, text=localization.get_text("Dark Mode"), command=self.toggle_theme)
        self.theme_switch.pack(anchor="w", padx=10, pady=5)
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

        # Language Settings
        lang_frame = ctk.CTkFrame(settings_frame)
        lang_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(lang_frame, text=localization.get_text("Language Settings"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        self.language_optionmenu = ctk.CTkOptionMenu(lang_frame, values=localization.get_available_languages(), command=self.change_language)
        self.language_optionmenu.set(localization.get_current_language_name()) # Set current language
        self.language_optionmenu.pack(anchor="w", padx=10, pady=5)

        # About Section
        about_frame = ctk.CTkFrame(settings_frame)
        about_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(about_frame, text=localization.get_text("About"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        about_text = localization.get_text("about_text")
        ctk.CTkLabel(about_frame, text=about_text, font=("Arial", 14), justify="left").pack(pady=5, padx=10, anchor="w")
        github_link = ctk.CTkLabel(about_frame, text=localization.get_text("github_repo"), text_color="cyan", cursor="hand2")
        github_link.pack(pady=5, padx=10, anchor="w")
        github_link.bind("<Button-1>", lambda e: actions.open_github())

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def change_language(self, new_language_name):
        localization.set_language_by_name(new_language_name)
        # Re-render the current frame to apply language changes
        current_frame_name = None
        for name, frame in self.content_frames.items():
            if frame.winfo_ismapped(): # Check if the frame is currently visible
                current_frame_name = name
                break
        if current_frame_name:
            # This will destroy and recreate widgets, applying new language strings
            if current_frame_name == "Dashboard":
                self.show_dashboard()
            elif current_frame_name == "Hardware Info":
                self.show_hardware_info()
            elif current_frame_name == "Applications":
                self.show_applications()
            elif current_frame_name == "Security":
                self.show_security()
            elif current_frame_name == "Network":
                self.show_network()
            elif current_frame_name == "Repair & Restore":
                self.show_repair_restore()
            elif current_frame_name == "Settings":
                self.show_settings()

    
