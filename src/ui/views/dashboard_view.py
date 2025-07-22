import customtkinter as ctk
from PIL import Image
import time
from logic import logic, localization

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections

class DashboardView(ctk.CTkFrame):
    STYLE = {
        "font_family": "Roboto",
        "font_title": ("Roboto", 24, "bold"),
        "font_card_header": ("Roboto", 14, "bold"),
        "font_main_stat": ("Roboto", 36, "bold"),
        "font_detail": ("Roboto", 9),
        "font_info": ("Roboto", 10),
        "font_info_small": ("Roboto", 8),
        "border_color": "#4A4A4A",
        "hover_color": "#3E3E3E",
        "color_green": "#2ECC71",
        "color_yellow": "#F1C40F",
        "color_red": "#E74C3C",
        "color_blue": "#3498DB"
    }

    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.configure(fg_color="transparent")

        self._after_id = None
        self.disk_widgets = {}
        
        self.last_net_update_time = time.time()
        self.last_disk_update_time = time.time()
        self.last_bytes_recv, self.last_bytes_sent = logic.get_network_io_counters()
        self.last_read_bytes, self.last_write_bytes = logic.get_disk_io()

        self.cpu_name = logic.get_cpu_name()
        self.local_ip = logic.get_local_ip()
        self.public_ip = logic.get_public_ip()

        self._set_colors()

        self.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=4)  # Tăng trọng số cho hàng disk để chiếm nhiều không gian hơn

        ctk.CTkLabel(self, text=localization.get_text("Dashboard"), font=self.STYLE["font_title"]).grid(
            row=0, column=0, columnspan=2, pady=(0, 10), sticky="w"
        )

        self._create_all_cards()
        self._populate_all_cards()

        self.start_updates()

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.bg_color = "#23272E"
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
            self.hover_color = "#3B4252"
            self.border_color = "#5C6370"
        else:
            self.bg_color = "#F8F8F2"
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.hover_color = "#E5E9F0"
            self.border_color = "#B0B0B0"

        self.STYLE["border_color"] = self.border_color
        self.STYLE["hover_color"] = self.hover_color

        if hasattr(self, 'cpu_card'):
            for card in [self.cpu_card, self.ram_card, self.system_card, self.network_card, self.disk_card]:
                card.configure(
                    fg_color=self.card_fg_color,
                    border_color=self.border_color,
                    border_width=2,
                    corner_radius=16
                )

    def _create_card(self, row, column, title_key, icon_name, rowspan=1, colspan=1):
        card = ctk.CTkFrame(
            self,
            border_width=2,
            border_color=self.STYLE["border_color"],
            fg_color=self.card_fg_color,
            corner_radius=16
        )
        card.grid(row=row, column=column, rowspan=rowspan, columnspan=colspan, padx=20, pady=20, sticky="nsew")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 8))
        
        try:
            icon = ctk.CTkImage(Image.open(f"assets/icons/{icon_name}.png"), size=(28, 28))
        except FileNotFoundError:
            icon = None
            
        ctk.CTkLabel(
            header_frame,
            text=localization.get_text(title_key),
            image=icon,
            compound="left",
            font=self.STYLE["font_card_header"],
            text_color=self.text_color
        ).pack(side="left")

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(8, 15))
        card.content_frame = content_frame

        card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.hover_color, border_color=self.STYLE["color_blue"]))
        card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.card_fg_color, border_color=self.border_color))

        return card

    def _create_all_cards(self):
        # Sắp xếp lại bố cục cho cân đối hơn
        self.cpu_card = self._create_card(1, 0, "CPU Usage", "system")
        self.ram_card = self._create_card(1, 1, "RAM Usage", "efficiency")
        self.system_card = self._create_card(2, 0, "System Info", "dashboard")
        self.network_card = self._create_card(2, 1, "Network", "network")
        self.disk_card = self._create_card(3, 0, "Disk Usage", "system_fix", colspan=2)

    def _populate_all_cards(self):
        self._populate_cpu_card()
        self._populate_ram_card()
        self._populate_system_card()
        self._populate_network_card()
        self._populate_disk_card()

    def _populate_cpu_card(self):
        content = self.cpu_card.content_frame
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)

        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="")

        self.cpu_percent_label = ctk.CTkLabel(text_frame, text="0.0%", font=self.STYLE["font_main_stat"], text_color=self.STYLE["color_blue"])
        self.cpu_percent_label.pack(pady=(0,0))
        self.cpu_speed_label = ctk.CTkLabel(text_frame, text="0.00 GHz", font=self.STYLE["font_detail"], text_color=self.text_color)
        self.cpu_speed_label.pack()
        self.cpu_name_label = ctk.CTkLabel(text_frame, text=self.cpu_name, font=self.STYLE["font_detail"], wraplength=220, text_color=self.text_color)
        self.cpu_name_label.pack(pady=(8, 8))
        
        self.cpu_progress = ctk.CTkProgressBar(content, height=12, corner_radius=6)
        self.cpu_progress.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

    def _populate_ram_card(self):
        content = self.ram_card.content_frame
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)

        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="")

        self.ram_percent_label = ctk.CTkLabel(text_frame, text="0.0%", font=self.STYLE["font_main_stat"], text_color=self.STYLE["color_green"])
        self.ram_percent_label.pack(pady=(0,0))
        self.ram_detail_label = ctk.CTkLabel(text_frame, text="0.0 / 0.0 GB", font=self.STYLE["font_detail"], text_color=self.text_color)
        self.ram_detail_label.pack(pady=(0, 8))

        self.ram_progress = ctk.CTkProgressBar(content, height=12, corner_radius=6)
        self.ram_progress.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

    def _populate_system_card(self):
        content = self.system_card.content_frame
        content.grid_columnconfigure(0, weight=1)
        # Tăng padding cho các dòng thông tin
        self.os_label = self._create_info_line(content, "system", f"{localization.get_text('OS')}: -")
        self.os_label.grid(row=0, column=0, sticky='ew', pady=4)
        self.hostname_label = self._create_info_line(content, "home", f"{localization.get_text('Hostname')}: -")
        self.hostname_label.grid(row=1, column=0, sticky='ew', pady=4)
        self.uptime_label = self._create_info_line(content, "update", f"{localization.get_text('Uptime')}: -")
        self.uptime_label.grid(row=2, column=0, sticky='ew', pady=4)
        self.ip_label = self._create_info_line(content, "network", f"{localization.get_text('Local IP')}: {self.local_ip}")
        self.ip_label.grid(row=3, column=0, sticky='ew', pady=4)
        self.public_ip_label = self._create_info_line(content, "network", f"{localization.get_text('Public IP')}: {self.public_ip}")
        self.public_ip_label.grid(row=4, column=0, sticky='ew', pady=4)

    def _populate_network_card(self):
        content = self.network_card.content_frame
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="") # Center the frame

        self.ping_label = self._create_info_line(info_frame, "report", f"{localization.get_text('Ping')}: -")
        self.ping_label.pack(anchor='w', pady=4)
        self.net_down_label = self._create_info_line(info_frame, "utilities", "\u2193 0.0 KB/s")
        self.net_down_label.pack(anchor='w', pady=4)
        self.net_up_label = self._create_info_line(info_frame, "utilities", "\u2191 0.0 KB/s")
        self.net_up_label.pack(anchor='w', pady=4)

    def _populate_disk_card(self):
        content = self.disk_card.content_frame
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=0)

        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="")

        # Main disk percent label (show tổng % của disk 1, disk 2)
        self.disk_percent_label = ctk.CTkLabel(text_frame, text="0.0%", font=self.STYLE["font_main_stat"], text_color=self.STYLE["color_blue"])
        self.disk_percent_label.pack(pady=(0,0))

        # Detail label: show tổng dung lượng và % cho từng disk vật lý
        self.disk_detail_label = ctk.CTkLabel(text_frame, text="", font=self.STYLE["font_detail"], text_color=self.text_color)
        self.disk_detail_label.pack(pady=(0, 8))

        # Progress bar cho disk đầu tiên
        self.disk_progress = ctk.CTkProgressBar(content, height=12, corner_radius=6)
        self.disk_progress.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

    def _create_info_line(self, parent, icon_name, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        if icon_name:
            try:
                icon = ctk.CTkImage(Image.open(f"assets/icons/{icon_name}.png"), size=(18, 18))
            except FileNotFoundError:
                icon = None
        else:
            icon = None

        label = ctk.CTkLabel(frame, text=text, image=icon, compound="left", font=self.STYLE["font_info"], anchor="w", text_color=self.text_color)
        label.pack(side="left", padx=8)
        return frame

    def _get_progress_color(self, percentage):
        if percentage > 75:
            return self.STYLE["color_red"]
        elif percentage > 40:
            return self.STYLE["color_yellow"]
        else:
            return self.STYLE["color_green"]

    def start_updates(self):
        self.cancel_updates()
        self._update_all_info()
        self._after_id = self.after(1000, self.start_updates)

    def cancel_updates(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _update_all_info(self):
        self._set_colors()
        self.update_cpu()
        self.update_ram()
        self.update_system()
        self.update_network()
        self.update_disk()

    def _format_speed(self, bytes_per_second):
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024**2:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        else:
            return f"{bytes_per_second / 1024**2:.1f} MB/s"

    def update_cpu(self):
        cpu_percent = logic.get_cpu_usage()
        self.cpu_percent_label.configure(text=f"{cpu_percent:.1f}%")
        self.cpu_progress.set(cpu_percent / 100)
        self.cpu_progress.configure(progress_color=self._get_progress_color(cpu_percent))
        self.cpu_speed_label.configure(text=logic.get_cpu_speed())

    def update_ram(self):
        ram_percent, ram_detail = logic.get_ram_usage()
        self.ram_percent_label.configure(text=f"{ram_percent:.1f}%")
        self.ram_detail_label.configure(text=ram_detail)
        self.ram_progress.set(ram_percent / 100)
        self.ram_progress.configure(progress_color=self._get_progress_color(ram_percent))

    def update_system(self):
        system_summary = logic.get_system_summary()
        self.os_label.winfo_children()[0].configure(text=f"{localization.get_text('OS')}: {system_summary['os']}")
        self.hostname_label.winfo_children()[0].configure(text=f"{localization.get_text('Hostname')}: {system_summary['hostname']}")
        self.uptime_label.winfo_children()[0].configure(text=f"{localization.get_text('Uptime')}: {system_summary['uptime']}")

    def update_network(self):
        current_time = time.time()
        bytes_recv, bytes_sent = logic.get_network_io_counters()
        
        time_delta = current_time - self.last_net_update_time
        if time_delta > 0:
            download_speed = (bytes_recv - self.last_bytes_recv) / time_delta
            upload_speed = (bytes_sent - self.last_bytes_sent) / time_delta
        else:
            download_speed, upload_speed = 0, 0

        self.last_net_update_time = current_time
        self.last_bytes_recv = bytes_recv
        self.last_bytes_sent = bytes_sent

        self.ping_label.winfo_children()[0].configure(text=f"{localization.get_text('Ping')}: {logic.get_ping()}")
        self.net_down_label.winfo_children()[0].configure(text=f"\u2193 {self._format_speed(download_speed)}")
        self.net_up_label.winfo_children()[0].configure(text=f"\u2191 {self._format_speed(upload_speed)}")

    def update_disk(self):
        # Gom các phân vùng theo từng disk vật lý (model)
        physical_disks_data = logic.get_physical_disk_usage()
        if not physical_disks_data:
            self.disk_percent_label.configure(text="0.0%")
            self.disk_detail_label.configure(text="No disk found")
            self.disk_progress.set(0)
            self.disk_progress.configure(progress_color=self._get_progress_color(0))
            return

        # Gom nhóm các phân vùng theo từng disk vật lý
        disk_groups = {}
        for disk in physical_disks_data:
            model = disk.get('model', f"Disk {len(disk_groups)+1}")
            if model not in disk_groups:
                disk_groups[model] = {'used': 0, 'total': 0, 'percent_sum': 0, 'count': 0}
            disk_groups[model]['used'] += disk['used']
            disk_groups[model]['total'] += disk['total']
            disk_groups[model]['percent_sum'] += disk['percent']
            disk_groups[model]['count'] += 1

        # Hiển thị tổng % của disk đầu tiên lên label lớn và progress
        first_model = list(disk_groups.keys())[0]
        first_disk = disk_groups[first_model]
        percent = (first_disk['used'] / first_disk['total']) * 100 if first_disk['total'] > 0 else 0
        self.disk_percent_label.configure(text=f"{percent:.1f}%")
        self.disk_progress.set(percent / 100)
        self.disk_progress.configure(progress_color=self._get_progress_color(percent))

        # Hiển thị thông tin tổng cho từng disk vật lý
        detail_lines = []
        for idx, (model, disk) in enumerate(disk_groups.items()):
            used_gb = disk['used'] / (1024**3)
            total_gb = disk['total'] / (1024**3)
            percent = (disk['used'] / disk['total']) * 100 if disk['total'] > 0 else 0
            detail_lines.append(f"Disk {idx+1}: {used_gb:.1f}/{total_gb:.1f} GB ({percent:.1f}%)")
        self.disk_detail_label.configure(text="\n".join(detail_lines))

    def _card_clicked(self, title_key):
        self.app_instance.show_frame(f"Detail - {localization.get_text(title_key)}")
