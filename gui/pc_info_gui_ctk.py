import customtkinter as ctk
import os
import sys
import threading
import logging
from PIL import Image, ImageTk
from datetime import datetime
import win32com.client
from CTkMessagebox import CTkMessagebox # Import for message boxes

# Import các hàm cần thiết từ core
from core.pc_info_functions import (
    get_detailed_system_information, NOT_AVAILABLE,
    _connect_wmi, ERROR_WMI_CONNECTION,
    get_disk_partitions_usage,
    generate_battery_report,
    check_windows_activation_status,
    open_resource_monitor,
    clear_temporary_files,
    get_recent_event_logs,
    get_installed_software_versions,
    get_wifi_connection_info,
    get_system_temperatures,
    get_running_processes,
    reset_internet_connection,
    run_sfc_scan,
    update_all_winget_packages,
    run_windows_defender_scan,
    update_windows_defender_definitions,
    get_firewall_status,
    toggle_firewall,
    get_startup_programs, run_ping_test, create_system_restore_point
)
from core.pc_info_manager import (
    validate_user_input,
    generate_filename,
    save_text_to_file,
    format_pc_info_to_string,
    format_system_details_to_string
)

# --- Cấu hình Logging (Thêm nếu chưa có ở file chính) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối của resource (ảnh, file...) để tương thích với PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

def format_user_info_for_display(user_info):
    """
    Định dạng thông tin người dùng thành chuỗi, bao gồm cả ghi chú.
    """
    lines = ["--- THÔNG TIN NGƯỜI DÙNG ---"]
    lines.append(f"  Tên người dùng: {user_info.get('Name', NOT_AVAILABLE)}")
    lines.append(f"  Bộ phận: {user_info.get('Department', NOT_AVAILABLE)}")
    lines.append(f"  Tầng: {user_info.get('Floor', NOT_AVAILABLE)}")
    position = user_info.get('Position')
    lines.append(f"  Chức vụ: {position if position else NOT_AVAILABLE}")
    notes = user_info.get('Notes')
    if notes:
        indented_notes = notes.replace('\n', '\n    ')
        lines.append(f"  Ghi chú:\n    {indented_notes}")
    return "\n".join(lines)

class PcInfoAppCtK(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Thông Tin Cấu Hình PC")
        self.geometry("850x750")
        self.resizable(True, True)

        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

        self.pc_info_dict = None
        self.formatted_pc_info_string = "Chưa lấy thông tin."

        self.logo_photo = None
        self._load_logo()
        self._create_widgets()

        # Start initial info fetch after widgets are created
        self.fetch_pc_info_threaded()

    def _load_logo(self):
        try:
            logo_relative_path = os.path.join("assets", "logo", "hpc-logo.png")
            logo_path = resource_path(logo_relative_path)
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image.thumbnail((70, 70), Image.Resampling.LANCZOS)
                self.logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(70, 70))
            else:
                logging.warning(f"Không tìm thấy file logo tại: {logo_path}")
                self.logo_photo = None
        except Exception as e:
            logging.error(f"Lỗi khi tải logo: {e}", exc_info=True)
            self.logo_photo = None

    def _create_widgets(self):
        # Top Frame for Logo and Title
        top_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        top_frame.pack(pady=(10,5), padx=20, fill=ctk.X)

        if self.logo_photo:
            logo_display_label = ctk.CTkLabel(top_frame, image=self.logo_photo, text="")
            logo_display_label.pack(side=ctk.RIGHT, padx=(15, 0), pady=5)

        app_title_label = ctk.CTkLabel(top_frame, text="Công Cụ Hỗ Trợ PC", font=ctk.CTkFont(size=24, weight="bold"))
        app_title_label.pack(side=ctk.LEFT, pady=5)

        # Tabview for different sections
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(pady=5, padx=20, fill=ctk.BOTH, expand=True)

        self.tabview.add("Trang Chủ")
        self.tabview.add("Tiện ích")
        self.tabview.add("Sửa Lỗi Hệ Thống")

        self._create_home_tab(self.tabview.tab("Trang Chủ"))
        self._create_utilities_tab(self.tabview.tab("Tiện ích"))
        self._create_fixes_tab(self.tabview.tab("Sửa Lỗi Hệ Thống"))

        # Global Buttons Frame
        frame_global_buttons = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame_global_buttons.pack(pady=(5, 15), fill=ctk.X, padx=20)

        self.button_export_home = ctk.CTkButton(frame_global_buttons, text="Xuất Dữ liệu PC", command=self.on_export_info, width=180, state="disabled")
        self.button_export_home.pack(side=ctk.LEFT, padx=(0,10))

        self.button_exit = ctk.CTkButton(frame_global_buttons, text="Thoát Ứng Dụng", command=self.destroy, width=150, fg_color="red", hover_color="darkred")
        self.button_exit.pack(side=ctk.RIGHT, padx=(10,0))

    def _create_home_tab(self, parent_tab):
        # --- User Info Frame ---
        frame_user = ctk.CTkFrame(parent_tab, corner_radius=10, border_width=1)
        frame_user.pack(pady=(0, 15), padx=0, fill=ctk.X)
        frame_user.columnconfigure(1, weight=1)
        frame_user.columnconfigure(3, weight=1)

        # User Info Grid
        user_info_pady = (5, 5)
        user_info_padx = (5, 5)

        ctk.CTkLabel(frame_user, text="Tên:").grid(row=0, column=0, padx=user_info_padx, pady=user_info_pady, sticky="w")
        self.entry_name = ctk.CTkEntry(frame_user, width=250)
        self.entry_name.grid(row=0, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky="ew")

        ctk.CTkLabel(frame_user, text="Phòng Ban:").grid(row=1, column=0, padx=user_info_padx, pady=user_info_pady, sticky="w")
        self.entry_department = ctk.CTkEntry(frame_user, width=250)
        self.entry_department.grid(row=1, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky="ew")

        ctk.CTkLabel(frame_user, text="Vị Trí Tầng:").grid(row=2, column=0, padx=user_info_padx, pady=user_info_pady, sticky="w")
        floor_options = ["Tầng G", "Lầu 1", "Lầu 2", "Khác"]
        self.combo_floor = ctk.CTkComboBox(frame_user, values=floor_options, width=150)
        self.combo_floor.grid(row=2, column=1, padx=user_info_padx, pady=user_info_pady, sticky="w")
        self.combo_floor.set(floor_options[0]) # Set initial value
        self.combo_floor.bind("<<ComboboxSelected>>", self.on_floor_change)

        self.entry_custom_floor_label = ctk.CTkLabel(frame_user, text="Nhập vị trí hiện tại:")
        self.entry_custom_floor = ctk.CTkEntry(frame_user, width=150)
        self.on_floor_change() # Initial check for custom floor entry

        ctk.CTkLabel(frame_user, text="Chức Vụ:").grid(row=3, column=0, padx=user_info_padx, pady=user_info_pady, sticky="w")
        self.entry_position = ctk.CTkEntry(frame_user, width=250)
        self.entry_position.grid(row=3, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky="ew")

        ctk.CTkLabel(frame_user, text="Ghi chú:").grid(row=4, column=0, padx=user_info_padx, pady=user_info_pady, sticky="nw")
        self.text_notes = ctk.CTkTextbox(frame_user, width=250, height=70, wrap="word")
        self.text_notes.grid(row=4, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky="ew")
        # CustomTkinter CTkTextbox has built-in scrollbar, no need for separate scrollbar

        # --- System Info Display for Home Tab ---
        frame_home_results = ctk.CTkFrame(parent_tab, corner_radius=10, border_width=1)
        frame_home_results.pack(fill=ctk.BOTH, expand=True, padx=0, pady=10)

        self.text_home_info = ctk.CTkTextbox(frame_home_results, wrap="word", state="disabled", font=ctk.CTkFont("Consolas", 10))
        self.text_home_info.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_home_info, "Đang tải thông tin ban đầu...")

        # --- Button to refresh Home tab info ---
        self.button_refresh_home = ctk.CTkButton(parent_tab, text="Làm mới", command=self.fetch_pc_info_threaded, width=180)
        self.button_refresh_home.pack(pady=(10,5))

    def _create_utilities_tab(self, parent_tab):
        # Main frame for utilities tab
        utilities_main_frame = ctk.CTkFrame(parent_tab, fg_color="transparent")
        utilities_main_frame.pack(fill=ctk.BOTH, expand=True)

        # Configure columns
        utilities_main_frame.columnconfigure(0, weight=2) # Action buttons
        utilities_main_frame.columnconfigure(1, weight=5) # Results display
        utilities_main_frame.rowconfigure(0, weight=1) # Allow vertical expansion

        # --- Left Column: Action Buttons ---
        actions_column_frame = ctk.CTkFrame(utilities_main_frame, fg_color="transparent")
        actions_column_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        utility_button_width = 200 # Adjusted width for CustomTkinter buttons
        utility_button_pady = 5
        utility_button_padx = 5

        # --- Group: Bảo mật & Virus ---
        frame_security = ctk.CTkFrame(actions_column_frame, corner_radius=10, border_width=1)
        frame_security.pack(pady=(0,10), padx=0, fill=ctk.X)
        ctk.CTkLabel(frame_security, text="Bảo mật & Virus", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        ctk.CTkButton(frame_security, text="Quét Virus Nhanh", command=self.run_defender_quick_scan, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_security, text="Quét Virus Toàn Bộ", command=self.run_defender_full_scan, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_security, text="Cập Nhật Định Nghĩa Virus", command=self.run_defender_update, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_security, text="Kiểm Tra Trạng Thái Tường Lửa", command=self.check_firewall_status_gui, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_security, text="Bật Tường Lửa (Tất cả Profile)", command=self.enable_firewall_gui, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_security, text="Tắt Tường Lửa (Tất cả Profile)", command=self.disable_firewall_gui, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)

        # --- Group: Thông tin & Chẩn đoán Hệ thống ---
        frame_diagnostics = ctk.CTkFrame(actions_column_frame, corner_radius=10, border_width=1)
        frame_diagnostics.pack(pady=(0,10), padx=0, fill=ctk.X)
        ctk.CTkLabel(frame_diagnostics, text="Thông tin & Chẩn đoán", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        ctk.CTkButton(frame_diagnostics, text="Xem Dung Lượng Ổ Đĩa", command=self.show_disk_usage, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Tạo Báo Cáo Pin (Laptop)", command=self.create_battery_report, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Kiểm tra kích hoạt Windows", command=self.run_check_windows_activation, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Xem Event Log Gần Đây", command=self.show_recent_event_logs, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Kiểm Tra Phiên Bản Phần Mềm", command=self.show_installed_software, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Kiểm Tra Kết Nối Wifi", command=self.show_wifi_info, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Kiểm Tra Nhiệt Độ Hệ Thống", command=self.show_system_temperatures, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Liệt Kê Tiến Trình Đang Chạy", command=self.show_running_processes, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)
        ctk.CTkButton(frame_diagnostics, text="Ứng Dụng Người Dùng Đã Cài", command=self.show_user_installed_applications, width=utility_button_width).pack(pady=utility_button_pady, padx=utility_button_padx)

        # --- Right Column: Utilities Results Display ---
        results_column_frame = ctk.CTkFrame(utilities_main_frame, fg_color="transparent")
        results_column_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        results_column_frame.rowconfigure(0, weight=1)
        results_column_frame.rowconfigure(1, weight=0)
        results_column_frame.columnconfigure(0, weight=1)

        frame_text_results_utils = ctk.CTkFrame(results_column_frame, corner_radius=10, border_width=1)
        frame_text_results_utils.grid(row=0, column=0, sticky="nsew", pady=(0,10))
        ctk.CTkLabel(frame_text_results_utils, text="Kết quả Tiện ích", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        self.text_utilities_results = ctk.CTkTextbox(frame_text_results_utils, wrap="word", state="disabled", font=ctk.CTkFont("Consolas", 10))
        self.text_utilities_results.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_utilities_results, "Kết quả của tiện ích sẽ hiển thị ở đây.")

        # Frame for buttons below results
        utils_results_buttons_frame = ctk.CTkFrame(results_column_frame, fg_color="transparent")
        utils_results_buttons_frame.grid(row=1, column=0, pady=(5,0), sticky="ew")

        self.button_save_utility_result = ctk.CTkButton(utils_results_buttons_frame, text="Lưu Kết Quả", command=lambda: self.save_tab_result(self.text_utilities_results, "KetQua_TienIch"), width=150, state="disabled")
        self.button_save_utility_result.pack(side=ctk.RIGHT, padx=(5,0))
        ctk.CTkButton(utils_results_buttons_frame, text="Ping (google.com)", command=self.run_ping_google, width=180).pack(side=ctk.LEFT, padx=(0,5))

    def _create_fixes_tab(self, parent_tab):
        fixes_main_frame = ctk.CTkFrame(parent_tab, fg_color="transparent")
        fixes_main_frame.pack(fill=ctk.BOTH, expand=True)
        fixes_main_frame.columnconfigure(0, weight=2)
        fixes_main_frame.columnconfigure(1, weight=5)
        fixes_main_frame.rowconfigure(0, weight=1)

        actions_column_frame_fixes = ctk.CTkFrame(fixes_main_frame, fg_color="transparent")
        actions_column_frame_fixes.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        fix_button_width = 200
        fix_button_pady = 5
        fix_button_padx = 5

        # --- Group: Dọn dẹp & Tối ưu ---
        frame_cleanup = ctk.CTkFrame(actions_column_frame_fixes, corner_radius=10, border_width=1)
        frame_cleanup.pack(pady=(0,10), padx=0, fill=ctk.X)
        ctk.CTkLabel(frame_cleanup, text="Dọn dẹp & Tối ưu", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        ctk.CTkButton(frame_cleanup, text="Xóa File Tạm & Dọn Dẹp", command=self.run_clear_temp_files, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)
        ctk.CTkButton(frame_cleanup, text="Mở Resource Monitor", command=self.run_open_resource_monitor, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)

        # --- Group: Sửa lỗi Hệ thống ---
        frame_system_fix = ctk.CTkFrame(actions_column_frame_fixes, corner_radius=10, border_width=1)
        frame_system_fix.pack(pady=(0,10), padx=0, fill=ctk.X)
        ctk.CTkLabel(frame_system_fix, text="Sửa lỗi Hệ thống", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        ctk.CTkButton(frame_system_fix, text="Reset Kết Nối Internet", command=self.run_reset_internet_connection, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)
        ctk.CTkButton(frame_system_fix, text="Chạy SFC Scan", command=self.run_sfc_scan_command, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)
        ctk.CTkButton(frame_system_fix, text="Tạo Điểm Khôi Phục Hệ Thống", command=self.run_create_restore_point, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)

        # --- Group: Cập nhật ---
        frame_updates = ctk.CTkFrame(actions_column_frame_fixes, corner_radius=10, border_width=1)
        frame_updates.pack(pady=(0,10), padx=0, fill=ctk.X)
        ctk.CTkLabel(frame_updates, text="Cập nhật", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        ctk.CTkButton(frame_updates, text="Quản Lý Khởi Động Cùng Windows", command=self.show_startup_programs, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)
        ctk.CTkButton(frame_updates, text="Cập Nhật Phần Mềm (Winget)", command=self.run_winget_update_all, width=fix_button_width).pack(pady=fix_button_pady, padx=fix_button_padx)

        # --- Right Column: Fixes Results Display ---
        results_column_frame_fixes = ctk.CTkFrame(fixes_main_frame, fg_color="transparent")
        results_column_frame_fixes.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        results_column_frame_fixes.rowconfigure(0, weight=1)
        results_column_frame_fixes.rowconfigure(1, weight=0)
        results_column_frame_fixes.columnconfigure(0, weight=1)

        frame_text_results_fixes = ctk.CTkFrame(results_column_frame_fixes, corner_radius=10, border_width=1)
        frame_text_results_fixes.grid(row=0, column=0, sticky="nsew", pady=(0,10))
        ctk.CTkLabel(frame_text_results_fixes, text="Kết quả Tác vụ Sửa lỗi", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))

        self.text_fixes_results = ctk.CTkTextbox(frame_text_results_fixes, wrap="word", state="disabled", font=ctk.CTkFont("Consolas", 10))
        self.text_fixes_results.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_fixes_results, "Chọn một tác vụ để thực hiện.")

        self.button_save_fix_result = ctk.CTkButton(results_column_frame_fixes, text="Lưu Kết Quả Sửa Lỗi", command=lambda: self.save_tab_result(self.text_fixes_results, "KetQua_SuaLoi"), width=180, state="disabled")
        self.button_save_fix_result.grid(row=1, column=0, pady=(5,0), sticky="e")

    def on_floor_change(self, event=None):
        """Show/hide custom floor entry based on combobox selection."""
        user_info_pady = (5, 5)
        user_info_padx = (5, 5)

        if self.combo_floor.get() == "Khác":
            self.entry_custom_floor_label.grid(row=2, column=2, padx=(10,user_info_padx[0]), pady=user_info_pady, sticky="w")
            self.entry_custom_floor.grid(row=2, column=3, padx=(0,user_info_padx[1]), pady=user_info_pady, sticky="ew")
        else:
            self.entry_custom_floor_label.grid_forget()
            self.entry_custom_floor.grid_forget()
            self.entry_custom_floor.delete(0, ctk.END)

    def _update_display_widget(self, text_widget, content):
        def update():
            text_widget.configure(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("end", content)
            if "Lỗi" in content or "Error" in content or "Không thể" in content:
                text_widget.configure(text_color="red")
            else:
                text_widget.configure(text_color=ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
            text_widget.configure(state="disabled")
        self.after(0, update)

    def _toggle_buttons(self, enable_refresh_home=True, enable_export_home=False, enable_save_utility=False, enable_save_fix=False):
        def toggle():
            # Check if buttons exist before configuring
            if hasattr(self, 'button_refresh_home'):
                self.button_refresh_home.configure(state="normal" if enable_refresh_home else "disabled")

            if hasattr(self, 'button_export_home'):
                pc_data_for_check = self.pc_info_dict.get("SystemInformation", {}).get("PC", {}) if self.pc_info_dict else {}
                has_errors_in_pc_data = isinstance(pc_data_for_check, dict) and \
                                        any("Lỗi" in str(v) or "Error" in str(v) for v in pc_data_for_check.values() if isinstance(v, str))
                can_export_home_data = enable_export_home and self.pc_info_dict and not has_errors_in_pc_data and pc_data_for_check != NOT_AVAILABLE
                self.button_export_home.configure(state="normal" if can_export_home_data else "disabled")
            
            if hasattr(self, 'button_save_utility_result'):
                self.button_save_utility_result.configure(state="normal" if enable_save_utility else "disabled")
            if hasattr(self, 'button_save_fix_result'):
                self.button_save_fix_result.configure(state="normal" if enable_save_fix else "disabled")
        self.after(0, toggle)

    def _fetch_task(self):
        try:
            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, "Đang lấy thông tin, vui lòng chờ...")
            self._toggle_buttons(enable_refresh_home=False, enable_export_home=False)

            self.pc_info_dict = get_detailed_system_information()

            home_info_data = self.pc_info_dict.get("SystemInformation", {"PC": {"Lỗi": "Không có dữ liệu SystemInformation"}})
            self.formatted_pc_info_string = format_system_details_to_string(home_info_data)

            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, self.formatted_pc_info_string)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=True)

        except Exception as e:
            error_msg = f"Lỗi khi lấy thông tin:\n{e}"
            logging.exception("Lỗi trong luồng lấy thông tin PC:")
            self.pc_info_dict = None
            self.formatted_pc_info_string = error_msg
            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, error_msg)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=False)
            CTkMessagebox(title="Lỗi", message=error_msg, icon="cancel")

    def fetch_pc_info_threaded(self):
        fetch_thread = threading.Thread(target=self._fetch_task, daemon=True)
        fetch_thread.start()

    def on_export_info(self):
        """Handles the 'Export File' button click."""
        if not self.pc_info_dict:
            CTkMessagebox(title="Chưa có thông tin", message="Thông tin Trang chủ chưa được tải. Vui lòng đợi hoặc làm mới.", icon="warning")
            return

        try:
            # 1. Get user info from GUI
            user_name = self.entry_name.get().strip()
            department = self.entry_department.get().strip()
            floor_selection = self.combo_floor.get()
            custom_floor = self.entry_custom_floor.get().strip() if floor_selection == "Khác" else ""
            position = self.entry_position.get().strip()
            notes = self.text_notes.get("1.0", "end").strip()
            final_floor = custom_floor if floor_selection == "Khác" and custom_floor else floor_selection

            user_info = {
                "Name": user_name,
                "Department": department,
                "Floor": final_floor,
                "Position": position,
                "Notes": notes
            }

            # 2. Validate user input
            validate_user_input(user_info) # Raises ValueError on failure

            # 3. PC info is already in self.pc_info_dict
            # 4. Format the *entire* pc_info_dict for the file
            full_formatted_pc_info_for_file = format_pc_info_to_string(self.pc_info_dict)

            # 5. Format user info for saving
            formatted_user_text = format_user_info_for_display(user_info)
            # 6. Combine content for saving
            full_content_to_save = f"{formatted_user_text}\n\n{full_formatted_pc_info_for_file}"

            # 7. Generate filename
            filename = generate_filename(user_info, self.pc_info_dict)

            # 8. Determine save path
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Exports_Formatted_TXT")
            file_path = os.path.join(save_dir, filename)

            # 9. Save the file
            save_text_to_file(full_content_to_save, file_path) # Raises exceptions on failure

            # 10. Show success message
            network_instruction = "\\\\pc-it-08\\Tools\\User"
            CTkMessagebox(
                title="Thành Công",
                message=f"Thông tin đã được lưu thành công vào file:\n{file_path}\n\n"
                        f"Vui lòng copy file này và dán vào thư mục bằng cách nhấn Win+R "
                        f"và nhập: {network_instruction}",
                icon="check"
            )

        except ValueError as ve: # Validation error
            CTkMessagebox(title="Thiếu thông tin", message=str(ve), icon="warning")
        except (IOError, RuntimeError) as save_e: # File saving error
             CTkMessagebox(title="Lỗi Lưu File", message=f"Không thể lưu file:\n{save_e}", icon="cancel")
        except Exception as e: # Other unexpected errors
            CTkMessagebox(title="Lỗi Không Xác Định", message=f"Đã xảy ra lỗi không mong muốn khi xuất file: {e}", icon="cancel")
            logging.exception("Lỗi không xác định khi xuất file:")

    def save_tab_result(self, text_widget, default_prefix="KetQua"):
        """Saves the content of a CTkTextbox widget to a .txt file."""
        content = text_widget.get("1.0", "end").strip()
        if not content or content == "Kết quả của tiện ích sẽ hiển thị ở đây." or content == "Chọn một tác vụ để thực hiện." or "Đang thực hiện:" in content:
            CTkMessagebox(title="Không có kết quả", message="Không có kết quả để lưu hoặc tác vụ đang chạy.", icon="warning")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{default_prefix}_{timestamp}.txt"
            
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Tool_Results")
            file_path = os.path.join(save_dir, filename)

            save_text_to_file(content, file_path)
            CTkMessagebox(title="Lưu Thành Công", message=f"Kết quả đã được lưu vào:\n{file_path}", icon="check")

        except (IOError, RuntimeError) as save_e:
            CTkMessagebox(title="Lỗi Lưu File", message=f"Không thể lưu file kết quả:\n{save_e}", icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Lỗi Không Xác Định", message=f"Đã xảy ra lỗi không mong muốn khi lưu kết quả: {e}", icon="cancel")
            logging.exception("Lỗi không xác định khi lưu kết quả tab:")

    def _format_task_result_for_display(self, result_data):
        if isinstance(result_data, list):
            formatted_items = []
            for item in result_data:
                if isinstance(item, dict):
                    item_str = "\n".join([f"  {k}: {v}" for k, v in item.items()])
                    formatted_items.append(item_str)
                else:
                    formatted_items.append(str(item))
            final_display_text = "\n---\n".join(formatted_items)
            if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về."
        elif isinstance(result_data, dict):
            if "message" in result_data and "status" in result_data:
                final_display_text = f"Trạng thái: {result_data.get('status', 'N/A')}\nThông điệp: {result_data['message']}"
                if "details" in result_data and result_data['details']:
                    details_content = result_data['details']
                    if isinstance(details_content, dict):
                        details_str = "\n".join([f"  {k_detail}: {v_detail}" for k_detail, v_detail in details_content.items() if k_detail != 'errors_list'])
                        if 'errors_list' in details_content and details_content['errors_list']:
                            details_str += f"\n  Lỗi chi tiết:\n    " + "\n    ".join(details_content['errors_list'][:5]) + ("..." if len(details_content['errors_list']) > 5 else "")
                        final_display_text += f"\n\nChi tiết:\n{details_str}"
                    else:
                        final_display_text += f"\n\nChi tiết:\n{details_content}"
                if "path" in result_data and result_data['path']: final_display_text += f"\n\nĐường dẫn file: {result_data['path']}"
            else:
                final_display_text = "\n".join([f"{k}: {v}" for k, v in result_data.items()])
                if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng)."
        else:
            final_display_text = str(result_data) if result_data is not None else "Tác vụ hoàn thành, không có dữ liệu trả về."

        return final_display_text

    def _run_task_in_thread(self, target_widget, task_function, needs_wmi=False, *task_args):
        self._update_display_widget(target_widget, f"Đang thực hiện: {task_function.__name__}...")
        if hasattr(self, 'button_save_utility_result') and target_widget == self.text_utilities_results:
            self._toggle_buttons(enable_save_utility=False)
        elif hasattr(self, 'button_save_fix_result') and target_widget == self.text_fixes_results:
            self._toggle_buttons(enable_save_fix=False)

        def task_wrapper():
            wmi_service_local = None
            com_initialized_local = False
            result_data = None

            try:
                if needs_wmi:
                    wmi_service_local, com_initialized_local = _connect_wmi()
                    if not wmi_service_local:
                        result_data = {"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kết nối WMI cho tác vụ này."}
                    else:
                        result_data = task_function(wmi_service_local, *task_args)
                else:
                    result_data = task_function(*task_args)

                self._update_display_widget(target_widget, self._format_task_result_for_display(result_data))
            except Exception as e:
                logging.exception(f"Lỗi khi chạy tiện ích {task_function.__name__}:")
                self._update_display_widget(target_widget, f"Lỗi khi thực hiện {task_function.__name__}:\n{e}")
            finally:
                if com_initialized_local:
                    try:
                        win32com.client.pythoncom.CoUninitialize()
                        logging.info(f"Đã giải phóng COM cho tác vụ {task_function.__name__}.")
                    except Exception as com_e:
                        logging.error(f"Lỗi khi giải phóng COM cho tác vụ {task_function.__name__}: {com_e}")
                if hasattr(self, 'button_save_utility_result') and target_widget == self.text_utilities_results:
                    self._toggle_buttons(enable_save_utility=True)
                elif hasattr(self, 'button_save_fix_result') and target_widget == self.text_fixes_results:
                    self._toggle_buttons(enable_save_fix=True)

        threading.Thread(target=task_wrapper, daemon=True).start()

    # Handlers for Utilities Tab (will be moved to a separate class later)
    def show_disk_usage(self):
        self._run_task_in_thread(self.text_utilities_results, get_disk_partitions_usage, needs_wmi=True)

    def create_battery_report(self):
        self._run_task_in_thread(self.text_utilities_results, generate_battery_report)

    def run_check_windows_activation(self):
        self._run_task_in_thread(self.text_utilities_results, check_windows_activation_status)

    def show_recent_event_logs(self):
        self._run_task_in_thread(self.text_utilities_results, get_recent_event_logs, needs_wmi=True)

    def show_installed_software(self):
        self._run_task_in_thread(self.text_utilities_results, get_installed_software_versions, needs_wmi=True)

    def show_wifi_info(self):
        self._run_task_in_thread(self.text_utilities_results, get_wifi_connection_info)

    def show_system_temperatures(self):
        self._run_task_in_thread(self.text_utilities_results, get_system_temperatures, needs_wmi=True)

    def show_running_processes(self):
        self._run_task_in_thread(self.text_utilities_results, get_running_processes)

    def show_user_installed_applications(self):
        self._run_task_in_thread(self.text_utilities_results, get_installed_software_versions, needs_wmi=False)

    def run_ping_google(self):
        self._run_task_in_thread(self.text_utilities_results, run_ping_test, False, "google.com", 4)

    def run_defender_quick_scan(self):
        self._run_task_in_thread(self.text_utilities_results, run_windows_defender_scan, False, "QuickScan")

    def run_defender_full_scan(self):
        self._run_task_in_thread(self.text_utilities_results, run_windows_defender_scan, False, "FullScan")

    def run_defender_update(self):
        self._run_task_in_thread(self.text_utilities_results, update_windows_defender_definitions)

    def check_firewall_status_gui(self):
        self._run_task_in_thread(self.text_utilities_results, get_firewall_status)

    def enable_firewall_gui(self):
        msg = CTkMessagebox(title="Xác nhận Bật Tường lửa", message="Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?",
                            icon="question", option_1="No", option_2="Yes")
        if msg.get() == "Yes":
            self._run_task_in_thread(self.text_utilities_results, toggle_firewall, False, True)

    def disable_firewall_gui(self):
        msg = CTkMessagebox(title="XÁC NHẬN TẮT TƯỜNG LỬA", message="CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?",
                            icon="warning", option_1="No", option_2="Yes")
        if msg.get() == "Yes":
            self._run_task_in_thread(self.text_utilities_results, toggle_firewall, False, False)

    # Handlers for Fixes Tab (will be moved to a separate class later)
    def run_clear_temp_files(self):
        self._run_task_in_thread(self.text_fixes_results, clear_temporary_files)

    def run_open_resource_monitor(self):
        self._run_task_in_thread(self.text_fixes_results, open_resource_monitor)

    def run_reset_internet_connection(self):
        self._run_task_in_thread(self.text_fixes_results, reset_internet_connection)

    def run_sfc_scan_command(self):
        self._run_task_in_thread(self.text_fixes_results, run_sfc_scan)

    def run_winget_update_all(self):
        self._run_task_in_thread(self.text_fixes_results, update_all_winget_packages)

    def show_startup_programs(self):
        self._run_task_in_thread(self.text_fixes_results, get_startup_programs)

    def run_create_restore_point(self):
        self._run_task_in_thread(self.text_fixes_results, create_system_restore_point)

if __name__ == "__main__":
    app = PcInfoAppCtK()
    app.mainloop()
