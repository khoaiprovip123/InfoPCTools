import customtkinter as ctk
from logic import logic, localization

class ApplicationsView(ctk.CTkFrame):
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
            self.tab_text_color = "#FFD700"  # Vàng nổi bật cho tab
            self.tab_selected_text_color = "#00BFFF"  # Xanh nổi bật cho tab được chọn
            self.segmented_button_unselected_color = "#44475a"  # Màu tối cho nút chưa chọn
            self.segmented_button_selected_color = "#00BFFF"    # Xanh cho nút đã chọn
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.border_color = "#DCE4EE"
            self.hover_color = "#CFCFCF"
            self.tab_text_color = "#FF8C00"  # Cam nổi bật cho tab
            self.tab_selected_text_color = "#0078D7"  # Xanh nổi bật cho tab được chọn
            self.segmented_button_unselected_color = "#F0F0F0"  # Màu sáng cho nút chưa chọn
            self.segmented_button_selected_color = "#0078D7"    # Xanh cho nút đã chọn

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._set_colors()

        self.active_after_ids = {}

        ctk.CTkLabel(self, text=localization.get_text("Applications"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

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

        installed_tab = tab_view.add(localization.get_text("Installed Apps"))
        startup_tab = tab_view.add(localization.get_text("Startup Apps"))
        # Bỏ tab tiến trình để ứng dụng load nhanh hơn
        # processes_tab = tab_view.add(localization.get_text("Processes"))
        
        self._create_installed_apps_tab(installed_tab)
        self._create_startup_apps_tab(startup_tab)
        # self._create_processes_tab(processes_tab)

    def _create_installed_apps_tab(self, tab):
        # Main frame for the tab content
        main_tab_frame = ctk.CTkFrame(tab, fg_color="transparent")
        main_tab_frame.pack(fill="both", expand=True)
        main_tab_frame.grid_rowconfigure(2, weight=1) # Make scrollable frame expand
        main_tab_frame.grid_columnconfigure(0, weight=1)

        # Search bar frame (fixed at the top)
        search_frame = ctk.CTkFrame(main_tab_frame, fg_color=self.card_fg_color, corner_radius=8, border_width=1, border_color=self.border_color)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        self.installed_apps_search_entry = ctk.CTkEntry(search_frame, placeholder_text=localization.get_text("Search installed apps..."), font=self.STYLE["font_info"], text_color=self.text_color)
        self.installed_apps_search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.installed_apps_search_entry.bind("<KeyRelease>", self._filter_installed_apps)

        # Header row frame (fixed below search bar)
        header_frame = ctk.CTkFrame(main_tab_frame, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        header_font = self.STYLE["font_info_bold"]
        header_frame.grid_columnconfigure(0, weight=3) # Name
        header_frame.grid_columnconfigure(1, weight=3) # Publisher
        header_frame.grid_columnconfigure(2, weight=1) # Install Date
        header_frame.grid_columnconfigure(3, weight=1) # Action

        ctk.CTkLabel(header_frame, text=localization.get_text("Name"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Publisher"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Install Date"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Action"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Scrollable frame for the content
        installed_frame = ctk.CTkScrollableFrame(main_tab_frame, fg_color="transparent")
        installed_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0,5))

        installed_frame.grid_columnconfigure(0, weight=3) # Name
        installed_frame.grid_columnconfigure(1, weight=3) # Publisher
        installed_frame.grid_columnconfigure(2, weight=1) # Install Date
        installed_frame.grid_columnconfigure(3, weight=1) # Action

        self.installed_apps_widgets = []
        self.all_installed_apps = logic.get_installed_apps()
        self._display_installed_apps(installed_frame, self.all_installed_apps)

    def _display_installed_apps(self, parent_frame, apps_to_display):
        for widget in self.installed_apps_widgets:
            widget.destroy()
        self.installed_apps_widgets.clear()

        row_index = 0 # Start from the first row in the scrollable frame
        for name, publisher, date in apps_to_display:
            name_label = ctk.CTkLabel(parent_frame, text=name, wraplength=250, justify="left", font=self.STYLE["font_info"], text_color=self.text_color)
            name_label.grid(row=row_index, column=0, padx=5, pady=2, sticky="w")
            self.installed_apps_widgets.append(name_label)

            publisher_label = ctk.CTkLabel(parent_frame, text=publisher, wraplength=150, justify="left", font=self.STYLE["font_info"], text_color=self.text_color)
            publisher_label.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            self.installed_apps_widgets.append(publisher_label)

            date_label = ctk.CTkLabel(parent_frame, text=date, font=self.STYLE["font_info"], text_color=self.text_color)
            date_label.grid(row=row_index, column=2, padx=5, pady=2, sticky="w")
            self.installed_apps_widgets.append(date_label)

            uninstall_button = ctk.CTkButton(parent_frame, text=localization.get_text("Uninstall"), width=80, font=self.STYLE["font_info"], fg_color="#E74C3C", text_color="#fff", hover_color="#C0392B")
            uninstall_button.grid(row=row_index, column=3, padx=5, pady=2, sticky="e")
            self.installed_apps_widgets.append(uninstall_button)

            row_index += 1

    def _filter_installed_apps(self, event=None):
        query = self.installed_apps_search_entry.get().lower()
        filtered_apps = [app for app in self.all_installed_apps if query in app[0].lower() or query in app[1].lower()]
        self._display_installed_apps(filtered_apps)

    def _create_startup_apps_tab(self, tab):
        main_tab_frame = ctk.CTkFrame(tab, fg_color="transparent")
        main_tab_frame.pack(fill="both", expand=True)
        main_tab_frame.grid_rowconfigure(2, weight=1)
        main_tab_frame.grid_columnconfigure(0, weight=1)

        search_frame = ctk.CTkFrame(main_tab_frame, fg_color=self.card_fg_color, corner_radius=8, border_width=1, border_color=self.border_color)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        self.startup_apps_search_entry = ctk.CTkEntry(search_frame, placeholder_text=localization.get_text("Search startup apps..."), font=self.STYLE["font_info"], text_color=self.text_color)
        self.startup_apps_search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.startup_apps_search_entry.bind("<KeyRelease>", self._filter_startup_apps)

        header_frame = ctk.CTkFrame(main_tab_frame, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        header_font = self.STYLE["font_info_bold"]
        header_frame.grid_columnconfigure(0, weight=2)
        header_frame.grid_columnconfigure(1, weight=3)
        header_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(header_frame, text=localization.get_text("Name"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Path"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Status"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        startup_frame = ctk.CTkScrollableFrame(main_tab_frame, fg_color="transparent")
        startup_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0,5))

        startup_frame.grid_columnconfigure(0, weight=2)
        startup_frame.grid_columnconfigure(1, weight=3)
        startup_frame.grid_columnconfigure(2, weight=1)

        self.startup_apps_widgets = []
        all_startup_apps = logic.get_startup_apps()
        self.all_startup_apps = [app for app in all_startup_apps if app.get("enabled") is not None]
        self._display_startup_apps(startup_frame, self.all_startup_apps)

    def _display_startup_apps(self, parent_frame, apps_to_display):
        for widget in self.startup_apps_widgets:
            widget.destroy()
        self.startup_apps_widgets.clear()

        row_index = 0 # Start from the first row in the scrollable frame
        for app_info in apps_to_display:
            name_label = ctk.CTkLabel(parent_frame, text=app_info["name"], wraplength=200, justify="left", font=self.STYLE["font_info"], text_color=self.text_color)
            name_label.grid(row=row_index, column=0, padx=5, pady=2, sticky="w")
            self.startup_apps_widgets.append(name_label)

            path_label = ctk.CTkLabel(parent_frame, text=app_info["path"], wraplength=300, justify="left", font=self.STYLE["font_info"], text_color=self.text_color)
            path_label.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            self.startup_apps_widgets.append(path_label)
            
            switch = ctk.CTkSwitch(parent_frame, text="", font=self.STYLE["font_info"])
            def on_switch_toggle(current_app_info=app_info, switch_widget=switch):
                state = switch_widget.get() # Get the current state of the switch
                self._toggle_startup_app(current_app_info, state)
            switch.configure(command=on_switch_toggle)
            switch.grid(row=row_index, column=2, padx=5, pady=2, sticky="w")
            if app_info["enabled"]:
                switch.select()
            else:
                switch.deselect()
            self.startup_apps_widgets.append(switch)
            row_index += 1

    def _filter_startup_apps(self, event=None):
        query = self.startup_apps_search_entry.get().lower()
        filtered_apps = [app for app in self.all_startup_apps if query in app["name"].lower() or query in app["path"].lower()]
        self._display_startup_apps(filtered_apps)

    def _create_processes_tab(self, tab):
        main_tab_frame = ctk.CTkFrame(tab, fg_color="transparent")
        main_tab_frame.pack(fill="both", expand=True)
        main_tab_frame.grid_rowconfigure(2, weight=1)
        main_tab_frame.grid_columnconfigure(0, weight=1)

        search_frame = ctk.CTkFrame(main_tab_frame, fg_color=self.card_fg_color, corner_radius=8, border_width=1, border_color=self.border_color)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        search_frame.grid_columnconfigure(0, weight=1)
        self.processes_search_entry = ctk.CTkEntry(search_frame, placeholder_text=localization.get_text("Search processes..."), font=self.STYLE["font_info"], text_color=self.text_color)
        self.processes_search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        self.processes_search_entry.bind("<KeyRelease>", self._filter_processes)

        header_frame = ctk.CTkFrame(main_tab_frame, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        header_font = self.STYLE["font_info_bold"]
        header_frame.grid_columnconfigure(0, weight=3) # Process Name
        header_frame.grid_columnconfigure(1, weight=1) # PID
        header_frame.grid_columnconfigure(2, weight=1) # CPU
        header_frame.grid_columnconfigure(3, weight=1) # Memory

        ctk.CTkLabel(header_frame, text=localization.get_text("Process Name"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("PID"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("CPU"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=localization.get_text("Memory"), font=header_font, text_color=self.tab_text_color).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.processes_frame = ctk.CTkScrollableFrame(main_tab_frame, fg_color="transparent")
        self.processes_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0,5))

        self.processes_frame.grid_columnconfigure(0, weight=3) # Process Name
        self.processes_frame.grid_columnconfigure(1, weight=1) # PID
        self.processes_frame.grid_columnconfigure(2, weight=1) # CPU
        self.processes_frame.grid_columnconfigure(3, weight=1) # Memory

        self.processes_labels = []
        self.all_processes = [] # Will be updated by update_processes
        self.update_processes()

    def update_processes(self):
        for label in self.processes_labels:
            label.destroy()
        self.processes_labels.clear()

        processes_data = logic.get_running_processes()
        self.all_processes = processes_data # Update all_processes
        self._display_processes(self.processes_frame, processes_data)

        self.active_after_ids["processes"] = self.after(3000, self.update_processes)

    def _display_processes(self, parent_frame, processes_to_display):
        for label in self.processes_labels:
            label.destroy()
        self.processes_labels.clear()

        if not processes_to_display:
            no_processes_label = ctk.CTkLabel(parent_frame, text=localization.get_text("No running processes found."), font=self.STYLE["font_info"], text_color=self.text_color)
            no_processes_label.grid(row=1, column=0, columnspan=4, padx=5, pady=10) # Row 1 after header
            self.processes_labels.append(no_processes_label)
            return

        row_index = 1 # Start after header
        for proc in processes_to_display:
            name_label = ctk.CTkLabel(parent_frame, text=proc["name"], wraplength=200, justify="left", font=self.STYLE["font_info"], text_color=self.text_color)
            name_label.grid(row=row_index, column=0, padx=5, pady=2, sticky="w")
            self.processes_labels.append(name_label)

            pid_label = ctk.CTkLabel(parent_frame, text=str(proc["pid"]), font=self.STYLE["font_info"], text_color=self.text_color)
            pid_label.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")
            self.processes_labels.append(pid_label)

            cpu_label = ctk.CTkLabel(parent_frame, text=f"{proc['cpu_percent']:.1f}%", font=self.STYLE["font_info"], text_color=self.text_color)
            cpu_label.grid(row=row_index, column=2, padx=5, pady=2, sticky="w")
            self.processes_labels.append(cpu_label)

            mem_label = ctk.CTkLabel(parent_frame, text=f"{proc['memory_percent']:.1f}%", font=self.STYLE["font_info"], text_color=self.text_color)
            mem_label.grid(row=row_index, column=3, padx=5, pady=2, sticky="w")
            self.processes_labels.append(mem_label)

            row_index += 1

    def _filter_processes(self, event=None):
        query = self.processes_search_entry.get().lower()
        filtered_processes = [proc for proc in self.all_processes if query in proc["name"].lower()]
        self._display_processes(filtered_processes)

    def _toggle_startup_app(self, app_info, state):
        success, error = logic.set_startup_app_status(
            app_info["hkey"],
            app_info["subkey"],
            app_info["value_name"],
            app_info["path"],
            state
        )
        if not success:
            ctk.CTkMessageBox(title=localization.get_text("Error"), message=f"{localization.get_text('Failed to change startup app status')}: {error}").show_warning()

    def cancel_updates(self):
        for after_id in self.active_after_ids.values():
            self.after_cancel(after_id)
        self.active_after_ids.clear()
        self.active_after_ids.clear()
