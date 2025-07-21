import customtkinter as ctk
from PIL import Image, ImageTk
from logic import logic, localization
import qrcode

class HardwareInfoView(ctk.CTkFrame):
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) # New column for user info
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(header_frame, text=localization.get_text("Hardware Info"), font=self.STYLE["font_title"]).grid(
            row=0, column=0, sticky="w", columnspan=2
        )

        # Content area: scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0,5))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.populate_hardware_info()
        self._create_user_info_section()

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
            self.border_color = "#5C6370"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.border_color = "#DCE4EE"

    def refresh_data(self):
        # Xóa nội dung cũ trước khi load lại
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.populate_hardware_info()

    def cancel_updates(self):
        # This view does not have continuous updates to cancel
        pass

    def populate_hardware_info(self):
        hardware_info, error = logic.get_hardware_info()

        if error:
            error_text = localization.get_text("wmi_not_found") if "wmi" in error.lower() else localization.get_text("error_occurred").format(e=error)
            error_label = ctk.CTkLabel(self.scrollable_frame, text=error_text, font=self.STYLE["font_card_header"], text_color="#E74C3C", wraplength=600)
            error_label.pack(pady=20, padx=10)
            return

        if not hardware_info:
            return

        category_order = ["System", "Motherboard", "CPU", "RAM", "GPU", "Storage", "Network Adapters"]
        for category_key in category_order:
            data = hardware_info.get(category_key)
            if data:
                self._create_section(category_key, data)

    def _create_user_info_section(self):
        user_info_frame = ctk.CTkFrame(
            self,
            fg_color=self.card_fg_color,
            corner_radius=8,
            border_width=1,
            border_color=self.border_color,
            width=300
        )
        user_info_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0,5))
        user_info_frame.grid_columnconfigure(0, weight=1) # Center content in this frame
        user_info_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9), weight=0) # Don't expand rows

        # User Info Section
        user_info_label = ctk.CTkLabel(user_info_frame, text=localization.get_text("User Information"), font=self.STYLE["font_card_header"])
        user_info_label.pack(pady=(10, 5), padx=15, anchor="w")

        # Full Name
        name_label = ctk.CTkLabel(user_info_frame, text=localization.get_text("Full Name:"), font=self.STYLE["font_info"], anchor="w")
        name_label.pack(fill="x", padx=15, pady=(5,0))
        self.name_entry = ctk.CTkEntry(user_info_frame, placeholder_text=localization.get_text("Enter full name"), font=self.STYLE["font_info"])
        self.name_entry.pack(fill="x", padx=15, pady=(0,5))

        # Department
        dept_label = ctk.CTkLabel(user_info_frame, text=localization.get_text("Department:"), font=self.STYLE["font_info"], anchor="w")
        dept_label.pack(fill="x", padx=15, pady=(5,0))
        self.dept_entry = ctk.CTkEntry(user_info_frame, placeholder_text=localization.get_text("Enter department"), font=self.STYLE["font_info"])
        self.dept_entry.pack(fill="x", padx=15, pady=(0,5))

        # Notes
        notes_label = ctk.CTkLabel(user_info_frame, text=localization.get_text("Notes:"), font=self.STYLE["font_info"], anchor="w")
        notes_label.pack(fill="x", padx=15, pady=(5,0))
        self.notes_entry = ctk.CTkEntry(user_info_frame, placeholder_text=localization.get_text("Add notes"), font=self.STYLE["font_info"])
        self.notes_entry.pack(fill="x", padx=15, pady=(0,10))

        # Buttons
        button_frame = ctk.CTkFrame(user_info_frame, fg_color="transparent")
        button_frame.pack(pady=5, padx=15, fill="x")
        button_frame.grid_columnconfigure((0,1), weight=1)

        save_button = ctk.CTkButton(button_frame, text=localization.get_text("Save"), command=self._save_user_info)
        save_button.grid(row=0, column=0, padx=(0,5), sticky="ew")

        print_button = ctk.CTkButton(button_frame, text=localization.get_text("Print"), command=self._print_info)
        print_button.grid(row=0, column=1, padx=(5,0), sticky="ew")

        # QR Code Section
        qr_label = ctk.CTkLabel(user_info_frame, text=localization.get_text("QR Code"), font=self.STYLE["font_card_header"])
        qr_label.pack(pady=(20, 5), padx=15, anchor="w")

        # Placeholder for QR data - will need to be generated from user info
        qr_data = self._get_qr_data_string()

        qr_img = qrcode.make(qr_data)
        qr_img = qr_img.resize((120, 120))
        self.qr_photo = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(120, 120)) # Store as instance variable

        self.qr_image_label = ctk.CTkLabel(user_info_frame, image=self.qr_photo, text="")
        self.qr_image_label.pack(padx=15, pady=(0, 10))

        # Bind entry changes to QR code update
        self.name_entry.bind("<KeyRelease>", self._update_qr_code)
        self.dept_entry.bind("<KeyRelease>", self._update_qr_code)
        self.notes_entry.bind("<KeyRelease>", self._update_qr_code)

    def _get_qr_data_string(self, include_user_info=False):
        system_info = logic.get_system_qr_data()
        
        qr_data = f"System Info:\n"
        qr_data += f"  System Type: {system_info['system_type']}\n"
        qr_data += f"  Hostname: {system_info['hostname']}\n"
        qr_data += f"  Motherboard Serial: {system_info['motherboard_serial']}\n"
        qr_data += f"  CPU: {system_info['cpu_name']}\n"
        qr_data += f"  RAM: {system_info['ram_detail']} ({system_info['ram_percent']:.1f}% used)\n"
        qr_data += f"  Total Disk: {system_info['total_disk_size']}\n"
        qr_data += f"  GPU: {system_info['gpu_name']}\n"

        user_info_str = ""
        if include_user_info:
            user_name = self.name_entry.get()
            user_dept = self.dept_entry.get()
            if user_name or user_dept:
                user_info_str = f"\n\nUser:\n  Name: {user_name}\n  Department: {user_dept}"
        return qr_data + user_info_str

    def _save_user_info(self):
        name = self.name_entry.get()
        department = self.dept_entry.get()
        notes = self.notes_entry.get()
        print(f"Saving User Info: Name={name}, Department={department}, Notes={notes}")
        # Here you would add logic to save this information, e.g., to a file or database

    def _print_info(self):
        print("Printing information...")
        qr_data_to_print = self._get_qr_data_string(include_user_info=True)
        qr_img = qrcode.make(qr_data_to_print)
        qr_img = qr_img.resize((300, 300)) # Larger for printing
        qr_img.show() # This will open the image in default viewer

    def _update_qr_code(self, event=None):
        qr_data = self._get_qr_data_string()
        qr_img = qrcode.make(qr_data)
        qr_img = qr_img.resize((120, 120))
        self.qr_photo = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(120, 120))
        self.qr_image_label.configure(image=self.qr_photo)

    def _create_section(self, title_key, data):
        # Card cho từng nhóm phần cứng
        section_container = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=self.card_fg_color,
            corner_radius=8,
            border_width=1,
            border_color=self.border_color
        )
        section_container.pack(fill="x", padx=5, pady=8, expand=True)

        # Tiêu đề nhóm
        title_label = ctk.CTkLabel(section_container, text=localization.get_text(title_key), font=self.STYLE["font_card_header"], text_color=self.text_color)
        title_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Nội dung nhóm
        content_frame = ctk.CTkFrame(section_container, fg_color="transparent")
        content_frame.pack(fill="x", expand=True, padx=15, pady=(0, 10))
        content_frame.grid_columnconfigure(1, weight=1)

        current_row = 0
        # Nếu là nhóm nhiều thiết bị (GPU, Storage, Network)
        if title_key in ["GPU", "Storage", "Network Adapters"]:
            for device_name, details in data.items():
                if current_row > 0:
                    separator = ctk.CTkFrame(content_frame, height=1, fg_color=self.border_color)
                    separator.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=8)
                    current_row += 1

                device_label = ctk.CTkLabel(content_frame, text=device_name, font=self.STYLE["font_info_bold"], anchor="w", wraplength=600)
                device_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(5, 2))
                current_row += 1
                
                for key, value in details.items():
                    self._add_info_row(content_frame, current_row, f"  {localization.get_text(key)}", value)
                    current_row += 1
        # Nếu là RAM (có nhiều module)
        elif title_key == "RAM":
            for key, value in data.items():
                if key == "Modules":
                    self._add_info_row(content_frame, current_row, localization.get_text(key), "")
                    current_row += 1
                    for module_info in value:
                        module_label = ctk.CTkLabel(content_frame, text=f"    • {module_info}", font=self.STYLE["font_info"], anchor="w", wraplength=500, justify="left")
                        module_label.grid(row=current_row, column=0, columnspan=2, sticky="w", padx=(15, 0), pady=1)
                        current_row += 1
                else:
                    self._add_info_row(content_frame, current_row, localization.get_text(key), value)
                    current_row += 1
        # Nếu là nhóm đơn giản (key-value)
        else:
            for key, value in data.items():
                self._add_info_row(content_frame, current_row, localization.get_text(key), value)
                current_row += 1

    def _add_info_row(self, parent, row, key, value):
        key_label = ctk.CTkLabel(
            parent,
            text=f"{key}:",
            font=self.STYLE["font_info_bold"],
            anchor="w",
            text_color=self.text_color
        )
        key_label.grid(row=row, column=0, sticky="nw", padx=(5, 10), pady=2)

        value_label = ctk.CTkLabel(
            parent,
            text=value,
            font=self.STYLE["font_info"],
            anchor="w",
            wraplength=550,
            justify="left",
            text_color=self.text_color
        )
        value_label.grid(row=row, column=1, sticky="ew", padx=(0, 5), pady=2)