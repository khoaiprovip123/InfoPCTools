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

        ctk.set_appearance_mode("Light")  # Set light mode as default
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
        self.current_qr_image = None # To store the PIL Image for QR export
        self.processes_labels = [] # To store labels for dynamic updates

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
            percent_label = ctk.CTkLabel(disk_entry, text=f"{disk['percent']}%" )
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

        # Configure grid for the main hardware_frame
        hardware_frame.grid_rowconfigure(0, weight=0) # User Info section (fixed height)
        hardware_frame.grid_rowconfigure(1, weight=1) # Hardware Details section (expands)
        hardware_frame.grid_columnconfigure(0, weight=1) # Single column for both sections

        # --- User Information Section (Top) ---
        user_info_section = ctk.CTkFrame(hardware_frame)
        user_info_section.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        user_info_section.grid_columnconfigure(0, weight=3) # Input fields area
        user_info_section.grid_columnconfigure(1, weight=1) # QR code and buttons area

        # User Input Fields (Left side of User Info Section)
        input_fields_frame = ctk.CTkFrame(user_info_section, fg_color="transparent")
        input_fields_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_fields_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(input_fields_frame, text=localization.get_text("User Information"), font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        input_fields_frame.grid_columnconfigure(0, weight=0) # Label column
        input_fields_frame.grid_columnconfigure(1, weight=1) # Entry column

        # Full Name
        ctk.CTkLabel(input_fields_frame, text=localization.get_text("Full Name") + ":", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fullname_entry = ctk.CTkEntry(input_fields_frame, corner_radius=10, border_width=2, height=35)
        self.fullname_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Department
        ctk.CTkLabel(input_fields_frame, text=localization.get_text("Department") + ":", anchor="w").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.department_entry = ctk.CTkEntry(input_fields_frame, corner_radius=10, border_width=2, height=35)
        self.department_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Notes
        ctk.CTkLabel(input_fields_frame, text=localization.get_text("Notes") + ":", anchor="w").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.notes_entry = ctk.CTkEntry(input_fields_frame, corner_radius=10, border_width=2, height=35)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Export Buttons (on one row, aligned with entry fields)
        button_frame = ctk.CTkFrame(input_fields_frame, fg_color="transparent")
        button_frame.grid(row=4, column=1, pady=10, sticky="ew") # Changed column and removed columnspan
        button_frame.grid_columnconfigure((0, 1), weight=1) # Distribute space evenly for buttons

        self.export_qr_button = ctk.CTkButton(
            button_frame,
            text=localization.get_text("Export QR"),
            command=self.export_qr_code_with_user_info,
            state="disabled"
        )
        self.export_qr_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.export_txt_button = ctk.CTkButton(
            button_frame,
            text=localization.get_text("Export TXT"),
            command=self.export_txt_with_user_info,
            state="disabled"
        )
        self.export_txt_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.fullname_entry.bind("<KeyRelease>", self._check_export_button_state)
        self.department_entry.bind("<KeyRelease>", self._check_export_button_state)

        # QR Code (Right side of User Info Section)
        qr_export_frame = ctk.CTkFrame(user_info_section)
        qr_export_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        qr_export_frame.grid_columnconfigure(0, weight=1) # Center QR

        self.qr_code_label = ctk.CTkLabel(qr_export_frame, text="")
        self.qr_code_label.pack(pady=10)

        # --- Hardware Information Section (Bottom) ---
        hardware_details_section = ctk.CTkFrame(hardware_frame)
        hardware_details_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        hardware_details_section.grid_columnconfigure(0, weight=1) # Single column for hardware details

        ctk.CTkLabel(hardware_details_section, text=localization.get_text("Hardware Information"), font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 10))

        info, error = logic.get_hardware_info()
        if error:
            ctk.CTkLabel(hardware_details_section, text=localization.get_text("error_occurred").format(e=error), font=("Arial", 16)).pack(pady=20)
            return

        scrollable_frame = ctk.CTkScrollableFrame(hardware_details_section, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=5, pady=0)

        # Automatically generate and display QR code on load
        self.generate_and_display_qr_code_with_user_info()

        def create_info_row(parent, key, value, row_index, is_subheader=False):
            parent.grid_columnconfigure(1, weight=1)
            key_font = ("Arial", 12, "bold")
            val_font = ("Arial", 12)
            if is_subheader:
                key_font = ("Arial", 14, "bold")

            key_label = ctk.CTkLabel(parent, text=localization.get_text(key), font=key_font, anchor="w")
            key_label.grid(row=row_index, column=0, sticky="w", padx=10, pady=2)

            if value:
                value_label = ctk.CTkLabel(parent, text=value, font=val_font, anchor="w", wraplength=600, justify="left")
                value_label.grid(row=row_index, column=1, sticky="w", padx=10, pady=2)

        def create_section(title, info_data):
            section_container = ctk.CTkFrame(scrollable_frame)
            section_container.pack(fill="x", pady=(0, 10), padx=5)

            ctk.CTkLabel(section_container, text=localization.get_text(title), font=("Arial", 18, "bold")).pack(fill="x", padx=10, pady=5)
            
            content_frame = ctk.CTkFrame(section_container, fg_color="transparent")
            content_frame.pack(fill="x", expand=True, padx=5)

            if title in ["Storage", "GPU", "Network Adapters"]:
                for i, (device_name, device_details) in enumerate(info_data.items()):
                    if i > 0:
                        sep = ctk.CTkFrame(content_frame, height=1, fg_color="gray50")
                        sep.pack(fill="x", padx=10, pady=10)
                    
                    device_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    device_frame.pack(fill="x", expand=True)
                    
                    device_row_index = 0
                    create_info_row(device_frame, device_name, "", device_row_index, is_subheader=True)
                    device_row_index += 1
                    for key, value in device_details.items():
                        create_info_row(device_frame, f"  {key}", value, device_row_index)
                        device_row_index += 1
            elif title == "RAM":
                row_index = 0
                create_info_row(content_frame, "Total", info_data.get("Total"), row_index)
                row_index += 1
                create_info_row(content_frame, "Slots", info_data.get("Slots"), row_index)
                row_index += 1
                create_info_row(content_frame, "Modules", "", row_index)
                row_index += 1
                for module in info_data.get("Modules", []):
                    module_label = ctk.CTkLabel(content_frame, text=f"    - {module}", font=("Arial", 12), anchor="w")
                    module_label.grid(row=row_index, column=0, columnspan=2, sticky="w", padx=20, pady=1)
                    row_index += 1
            else:
                row_index = 0
                for key, value in info_data.items():
                    create_info_row(content_frame, key, value, row_index)
                    row_index += 1

        for section_title, section_data in info.items():
            create_section(section_title, section_data)

    def generate_and_display_qr_code_with_user_info(self):
        user_info = {
            "Full Name": self.fullname_entry.get(),
            "Department": self.department_entry.get(),
            "Notes": self.notes_entry.get()
        }
        qr_image, error = logic.generate_qr_code_for_hardware_info(user_info)
        if error:
            self.qr_code_label.configure(text=f"Error: {error}", text_color="red")
            self.qr_code_label.configure(image=None) # Clear any previous image
            self.current_qr_image = None
        elif qr_image:
            self.current_qr_image = qr_image # Store PIL Image
            ctk_qr_image = ctk.CTkImage(qr_image.convert("RGB"), size=(150, 150)) # Adjust size as needed
            self.qr_code_label.configure(image=ctk_qr_image, text="")
        else:
            self.qr_code_label.configure(text="No QR code generated.", text_color="red")
            self.qr_code_label.configure(image=None)
            self.current_qr_image = None

    def export_qr_code_with_user_info(self):
        fullname = self.fullname_entry.get()
        department = self.department_entry.get()

        if not fullname or not department:
            # Display an error message to the user
            customtkinter.CTkMessageBox(title=localization.get_text("Error"), message=localization.get_text("fullname_department_required")).show_warning()
            return

        if self.current_qr_image:
            actions.export_qr_code_image(self.current_qr_image)
        else:
            customtkinter.CTkMessageBox(title=localization.get_text("Error"), message=localization.get_text("no_qr_code_to_export")).show_warning()

    def export_txt_with_user_info(self):
        fullname = self.fullname_entry.get()
        department = self.department_entry.get()
        notes = self.notes_entry.get()

        if not fullname or not department:
            # Display an error message to the user
            customtkinter.CTkMessageBox(title=localization.get_text("Error"), message=localization.get_text("fullname_department_required")).show_warning()
            return

        user_info = {
            "Full Name": fullname,
            "Department": department,
            "Notes": notes
        }
        actions.export_hardware_info_to_txt(user_info)

    def _check_export_button_state(self, event=None):
        fullname_filled = bool(self.fullname_entry.get())
        department_filled = bool(self.department_entry.get())

        if fullname_filled and department_filled:
            self.export_qr_button.configure(state="normal")
            self.export_txt_button.configure(state="normal")
        else:
            self.export_qr_button.configure(state="disabled")
            self.export_txt_button.configure(state="disabled")

    def show_applications(self):
        self.show_frame("Applications")
        applications_frame = self.content_frames["Applications"]
        for widget in applications_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(applications_frame, text=localization.get_text("Applications"), font=("Arial", 24, "bold")).pack(pady=10)

        tab_view = ctk.CTkTabview(applications_frame)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        installed_tab = tab_view.add(localization.get_text("Installed Apps"))
        startup_tab = tab_view.add(localization.get_text("Startup Apps"))
        # --- Installed Apps Tab ---
        installed_frame = ctk.CTkScrollableFrame(installed_tab)
        installed_frame.pack(fill="both", expand=True)

        # Table Headers for Installed Apps
        header_font = ("Arial", 12, "bold")
        installed_frame.grid_columnconfigure(0, weight=3) # Name
        installed_frame.grid_columnconfigure(1, weight=2) # Publisher
        installed_frame.grid_columnconfigure(2, weight=1) # Install Date
        installed_frame.grid_columnconfigure(3, weight=1) # Action

        ctk.CTkLabel(installed_frame, text=localization.get_text("Name"), font=header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(installed_frame, text=localization.get_text("Publisher"), font=header_font).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(installed_frame, text=localization.get_text("Install Date"), font=header_font).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(installed_frame, text=localization.get_text("Action"), font=header_font).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Installed Apps Data
        row_index = 1
        for name, publisher, date in logic.get_installed_apps():
            ctk.CTkLabel(installed_frame, text=name, wraplength=250, justify="left").grid(row=row_index, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(installed_frame, text=publisher, wraplength=150, justify="left").grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(installed_frame, text=date).grid(row=row_index, column=2, padx=5, pady=2, sticky="w")
            ctk.CTkButton(installed_frame, text=localization.get_text("Uninstall"), width=80).grid(row=row_index, column=3, padx=5, pady=2, sticky="e")
            row_index += 1

        # --- Startup Apps Tab ---
        startup_frame = ctk.CTkScrollableFrame(startup_tab)
        startup_frame.pack(fill="both", expand=True)

        # Table Headers for Startup Apps
        startup_frame.grid_columnconfigure(0, weight=2) # Name
        startup_frame.grid_columnconfigure(1, weight=3) # Path
        startup_frame.grid_columnconfigure(2, weight=1) # Status

        ctk.CTkLabel(startup_frame, text=localization.get_text("Name"), font=header_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(startup_frame, text=localization.get_text("Path"), font=header_font).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(startup_frame, text=localization.get_text("Status"), font=header_font).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Startup Apps Data
        row_index = 1
        for app_info in logic.get_startup_apps():
            ctk.CTkLabel(startup_frame, text=app_info["name"], wraplength=200, justify="left").grid(row=row_index, column=0, padx=5, pady=2, sticky="w")
            ctk.CTkLabel(startup_frame, text=app_info["path"], wraplength=300, justify="left").grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            
            switch = ctk.CTkSwitch(startup_frame, text="")
            def on_switch_toggle(state, current_app_info=app_info):
                self._toggle_startup_app(current_app_info, state)
            switch.configure(command=on_switch_toggle)
            switch.grid(row=row_index, column=2, padx=5, pady=2, sticky="w")
            if app_info["enabled"]:
                switch.select()
            else:
                switch.deselect()
            row_index += 1

        

    def update_processes_display(self, parent_frame):
        # Clear existing process labels
        for label in self.processes_labels:
            label.destroy()
        self.processes_labels.clear()

        # Get and display current processes
        processes = logic.get_running_processes()
        if processes:
            # Create header row
            header_font = ("Arial", 12, "bold")
            
            header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(5, 0))

            ctk.CTkLabel(header_frame, text=localization.get_text("Process Name"), font=header_font).pack(side="left", padx=5, pady=5, expand=True, fill="x")
            ctk.CTkLabel(header_frame, text=localization.get_text("PID"), font=header_font).pack(side="left", padx=5, pady=5, expand=True, fill="x")
            ctk.CTkLabel(header_frame, text=localization.get_text("CPU"), font=header_font).pack(side="left", padx=5, pady=5, expand=True, fill="x")
            ctk.CTkLabel(header_frame, text=localization.get_text("Memory"), font=header_font).pack(side="left", padx=5, pady=5, expand=True, fill="x")

            for p in processes:
                process_row_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
                process_row_frame.pack(fill="x", pady=2)

                name_label = ctk.CTkLabel(process_row_frame, text=p["name"], wraplength=200, justify="left")
                name_label.pack(side="left", padx=5, pady=2, expand=True, fill="x")
                pid_label = ctk.CTkLabel(process_row_frame, text=str(p["pid"]))
                pid_label.pack(side="left", padx=5, pady=2, expand=True, fill="x")
                cpu_label = ctk.CTkLabel(process_row_frame, text=f"{p["cpu_percent"]:.1f}%")
                cpu_label.pack(side="left", padx=5, pady=2, expand=True, fill="x")
                mem_label = ctk.CTkLabel(process_row_frame, text=f"{p["memory_percent"]:.1f}%")
                mem_label.pack(side="left", padx=5, pady=2, expand=True, fill="x")

                self.processes_labels.extend([name_label, pid_label, cpu_label, mem_label])
        else:
            no_processes_label = ctk.CTkLabel(parent_frame, text=localization.get_text("No running processes found."))
            no_processes_label.pack(pady=20)
            self.processes_labels.append(no_processes_label)

        self.active_after_ids["processes_update"] = self.after(3000, lambda: self.update_processes_display(parent_frame))

    def _toggle_startup_app(self, app_info, state):
        print(f"_toggle_startup_app called with: {app_info['name']}, state: {state}") # Debug print
        success, error = logic.set_startup_app_status(
            app_info["hkey"],
            app_info["subkey"],
            app_info["value_name"],
            app_info["path"],
            state
        )
        if not success:
            customtkinter.CTkMessageBox(title=localization.get_text("Error"), message=f"{localization.get_text("Failed to change startup app status")}: {error}").show_warning()

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
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

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
            # If the current frame is Applications, ensure processes are updated
            if current_frame_name == "Applications":
                # Re-initialize the processes tab to ensure it updates correctly
                self.show_applications()