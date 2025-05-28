## 2. gui/pc_info_gui.py
# Tạo giao diện chính
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext # Use scrolledtext for simplicity
import os
import sys
import threading # Import threading
import logging # Import logging
from PIL import Image, ImageTk
from datetime import datetime # Import datetime
import win32com.client # For CoUninitialize in task runner

# Import các hàm cần thiết từ core
from core.pc_info_functions import (
    get_detailed_system_information, NOT_AVAILABLE,
    # Import thêm các hàm tiện ích bạn sẽ dùng
    _connect_wmi, ERROR_WMI_CONNECTION, # For task runner WMI handling
    get_disk_partitions_usage,
    generate_battery_report,
    check_windows_activation_status,
    open_resource_monitor,
    clear_temporary_files,
    # Placeholders for new functions to be implemented in core.pc_info_functions.py
    get_recent_event_logs,
    get_installed_software_versions,
    get_wifi_connection_info,
    get_system_temperatures,
    get_running_processes,
    reset_internet_connection,
    run_sfc_scan,
    update_all_winget_packages,
    run_windows_defender_scan, # Đã có, đảm bảo import
    update_windows_defender_definitions, 
    get_firewall_status, 
    toggle_firewall,
    # Các hàm mới được thêm
    get_startup_programs, run_ping_test, create_system_restore_point
)
# from core.pc_info_functions import get_pc_info, NOT_AVAILABLE # Dòng cũ
# Import các hàm tiện ích từ manager
from core.pc_info_manager import (
    validate_user_input,
    generate_filename,
    save_text_to_file,
    format_pc_info_to_string, # <--- Use this formatter
    format_system_details_to_string # <--- Import the missing function
)

# --- Cấu hình Logging (Thêm nếu chưa có ở file chính) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants for UI Styling ---
BG_COLOR = "#F0F0F0"  # Light gray background
ACCENT_COLOR = "#E0E0E0" # Slightly darker gray for accents/tabs
TEXT_COLOR = "#333333" # Dark gray for text
BUTTON_BG_COLOR = "#D0D0D0" # General button background (can be overridden by theme)
BUTTON_PRIMARY_BG = "#A0C4FF" # Calmer blue for primary actions (e.g., Refresh)
BUTTON_EXPORT_BG = "#A9D18E" # Green for export
BUTTON_DANGER_BG = "#FFB6C1" # Softer red for exit/danger actions
DEFAULT_FONT = ("Segoe UI", 10)
BOLD_FONT = ("Segoe UI", 10, "bold")
MONOSPACE_FONT = ("Consolas", 9) # For system info display

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối của resource (ảnh, file...) để tương thích với PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Not running as a PyInstaller bundle
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

# --- Định dạng thông tin người dùng (Giữ nguyên hoặc điều chỉnh nếu cần) ---
def format_user_info_for_display(user_info):
    """Định dạng thông tin người dùng thành chuỗi, bao gồm cả ghi chú."""
    lines = ["--- THÔNG TIN NGƯỜI DÙNG ---"]
    lines.append(f"  Tên người dùng: {user_info.get('Name', NOT_AVAILABLE)}")
    lines.append(f"  Bộ phận: {user_info.get('Department', NOT_AVAILABLE)}")
    lines.append(f"  Tầng: {user_info.get('Floor', NOT_AVAILABLE)}")
    position = user_info.get('Position')
    lines.append(f"  Chức vụ: {position if position else NOT_AVAILABLE}")
    notes = user_info.get('Notes')
    if notes:
        # Thụt lề các dòng mới trong ghi chú
        indented_notes = notes.replace('\n', '\n    ')
        lines.append(f"  Ghi chú:\n    {indented_notes}")
    return "\n".join(lines)


class PcInfoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thông Tin Cấu Hình PC")
        self.geometry("850x750") # Increased size slightly for more space
        self.configure(bg=BG_COLOR)
        self.resizable(True, True) # Cho phép thay đổi kích thước

        # --- Style Configuration ---
        self.style = ttk.Style(self)
        try:
            # 'clam' theme often looks more modern than 'default' on some systems
            self.style.theme_use('clam')
        except tk.TclError:
            logging.warning("Clam theme not found, using default.")
            self.style.theme_use('default') # Fallback to default theme

        self.style.configure('.', font=DEFAULT_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, padding=5)
        self.style.configure('TButton', font=BOLD_FONT, padding=(6, 3)) # Default button style - Reduced padding
        self.style.configure('Header.TLabel', font=("Segoe UI", 16, "bold"), background=BG_COLOR)
        self.style.configure('TLabelframe', background=BG_COLOR, bordercolor=ACCENT_COLOR, relief=tk.SOLID)
        self.style.configure('TLabelframe.Label', background=BG_COLOR, foreground=TEXT_COLOR, font=BOLD_FONT)
        self.style.configure('TNotebook', background=BG_COLOR, borderwidth=1)
        self.style.configure('TNotebook.Tab', font=DEFAULT_FONT, padding=(10, 5), background=ACCENT_COLOR)
        self.style.map('TNotebook.Tab', background=[('selected', BG_COLOR)], foreground=[('selected', TEXT_COLOR)])
        # self.style.configure('Treeview', font=DEFAULT_FONT, rowheight=25) # Example if Treeview is used
        # self.style.configure('Treeview.Heading', font=BOLD_FONT)

        # --- State Variables ---
        self.pc_info_dict = None # Store fetched PC data dictionary
        self.formatted_pc_info_string = "Chưa lấy thông tin." # Store formatted string

        # --- WMI Service for utilities (optional, can be fetched on demand) ---
        # self.wmi_service, self.com_initialized = _connect_wmi() # Cân nhắc việc quản lý kết nối WMI

        self.logo_photo = None # Initialize logo_photo
        self._load_logo() # Load the logo image first
        self._create_widgets()

        # --- Start initial info fetch ---
        # Lấy thông tin cho Trang chủ khi khởi động
        self.fetch_pc_info_threaded()

    def _load_logo(self):
        try:
            logo_relative_path = os.path.join("assets", "logo", "hpc-logo.png")
            logo_path = resource_path(logo_relative_path)
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image.thumbnail((70, 70), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
            else:
                logging.warning(f"Không tìm thấy file logo tại: {logo_path}")
                self.logo_photo = None
        except Exception as e:
            logging.error(f"Lỗi khi tải logo: {e}", exc_info=True)
            self.logo_photo = None

    def _create_widgets(self):
        # --- Main PanedWindow for resizable sections (optional) ---
        # main_paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        # main_paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Top Frame for Logo and Title (if needed) ---
        top_frame = ttk.Frame(self, style='TFrame')
        top_frame.pack(pady=(10,5), padx=20, fill=tk.X) # Reduced pady bottom

        if self.logo_photo: # Check if logo was loaded successfully
            logo_display_label = ttk.Label(top_frame, image=self.logo_photo, style='TLabel')
            logo_display_label.pack(side=tk.LEFT, padx=(0, 15), pady=5) # Adjust padding

        app_title_label = ttk.Label(top_frame, text="Công Cụ Hỗ Trợ PC", style='Header.TLabel')
        app_title_label.pack(side=tk.LEFT, pady=5) # Title flows after logo

        # --- Notebook for different sections ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        # --- Tab: Trang chủ ---
        self.tab_home = ttk.Frame(self.notebook, padding=15, style='TFrame') # Increased padding
        self.notebook.add(self.tab_home, text="Trang chủ")
        self._create_home_tab(self.tab_home)

        # --- Tab: Tiện ích ---
        self.tab_utilities = ttk.Frame(self.notebook, padding=15, style='TFrame')
        self.notebook.add(self.tab_utilities, text="Tiện ích")
        self._create_utilities_tab(self.tab_utilities)

        # --- Tab: Sửa lỗi hệ thống ---
        self.tab_fixes = ttk.Frame(self.notebook, padding=15, style='TFrame')
        self.notebook.add(self.tab_fixes, text="Sửa lỗi hệ thống")
        self._create_fixes_tab(self.tab_fixes)

        # --- Global Buttons Frame (Xuất file, Thoát) ---
        frame_global_buttons = ttk.Frame(self, style='TFrame')
        frame_global_buttons.pack(pady=(5, 15), fill=tk.X, padx=20)

        # Nút "Xuất Dữ liệu PC" chỉ còn ở tab Trang chủ (logic xử lý trong on_export_info)
        # Chúng ta sẽ thêm nút "Lưu Kết Quả" vào các tab Tiện ích và Sửa lỗi sau
        self.button_export_home = ttk.Button(frame_global_buttons, text="Xuất Dữ liệu PC (Trang chủ)", command=self.on_export_info, width=25, style='Export.TButton', state=tk.DISABLED)
        self.button_export_home.pack(side=tk.LEFT, padx=(0,10))

        self.style.configure('Exit.TButton', background=BUTTON_DANGER_BG, foreground="black") # Darker text for pink
        self.button_exit = ttk.Button(frame_global_buttons, text="Thoát Ứng Dụng", command=self.destroy, width=20, style='Exit.TButton')
        self.button_exit.pack(side=tk.RIGHT, padx=(10,0))

    def _create_home_tab(self, parent_tab):
        # --- User Info Frame ---
        frame_user = ttk.LabelFrame(parent_tab, text="Thông tin người dùng (cho file xuất)", padding=(10,5))
        frame_user.pack(pady=(0, 15), padx=0, fill=tk.X) # Increased pady bottom
        frame_user.columnconfigure(1, weight=1)
        frame_user.columnconfigure(3, weight=1)

        # User Info Grid
        user_info_pady = (5, 5) # Consistent padding for user info grid
        user_info_padx = (5, 5)

        ttk.Label(frame_user, text="Tên:").grid(row=0, column=0, padx=user_info_padx, pady=user_info_pady, sticky=tk.W)
        self.entry_name = ttk.Entry(frame_user, width=40, font=DEFAULT_FONT)
        self.entry_name.grid(row=0, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky=tk.EW)

        ttk.Label(frame_user, text="Phòng Ban:").grid(row=1, column=0, padx=user_info_padx, pady=user_info_pady, sticky=tk.W)
        self.entry_department = ttk.Entry(frame_user, width=40, font=DEFAULT_FONT)
        self.entry_department.grid(row=1, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky=tk.EW)

        ttk.Label(frame_user, text="Vị Trí Tầng:").grid(row=2, column=0, padx=user_info_padx, pady=user_info_pady, sticky=tk.W)
        floor_options = ["Tầng G", "Lầu 1", "Lầu 2", "Khác"]
        self.combo_floor = ttk.Combobox(frame_user, values=floor_options, state="readonly", width=15, font=DEFAULT_FONT)
        self.combo_floor.grid(row=2, column=1, padx=user_info_padx, pady=user_info_pady, sticky=tk.W)
        self.combo_floor.current(0)
        self.combo_floor.bind("<<ComboboxSelected>>", self.on_floor_change)

        self.entry_custom_floor_label = ttk.Label(frame_user, text="Nhập vị trí hiện tại:") # Use ttk.Label
        self.entry_custom_floor = ttk.Entry(frame_user, width=20, font=DEFAULT_FONT) # Use ttk.Entry
        self.on_floor_change() # Initial check for custom floor entry

        ttk.Label(frame_user, text="Chức Vụ:").grid(row=3, column=0, padx=user_info_padx, pady=user_info_pady, sticky=tk.W)
        self.entry_position = ttk.Entry(frame_user, width=40, font=DEFAULT_FONT)
        self.entry_position.grid(row=3, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky=tk.EW)

        ttk.Label(frame_user, text="Ghi chú:").grid(row=4, column=0, padx=user_info_padx, pady=user_info_pady, sticky=tk.NW)
        self.text_notes = tk.Text(frame_user, width=40, height=3, wrap=tk.WORD, font=DEFAULT_FONT, relief=tk.SOLID, borderwidth=1, bg="white", fg=TEXT_COLOR)
        self.text_notes.grid(row=4, column=1, columnspan=3, padx=user_info_padx, pady=user_info_pady, sticky=tk.EW)
        notes_scrollbar = ttk.Scrollbar(frame_user, command=self.text_notes.yview) # Use ttk.Scrollbar
        notes_scrollbar.grid(row=4, column=4, padx=(0,user_info_padx[1]), pady=user_info_pady, sticky=tk.NS)
        self.text_notes.config(yscrollcommand=notes_scrollbar.set)

        # --- System Info Display for Home Tab ---
        frame_home_results = ttk.LabelFrame(parent_tab, text="Thông tin hệ thống", padding=(10,5))
        frame_home_results.pack(fill=tk.BOTH, expand=True, padx=0, pady=10)

        self.text_home_info = scrolledtext.ScrolledText(frame_home_results, wrap=tk.WORD, height=15, state=tk.DISABLED, font=MONOSPACE_FONT, relief=tk.SOLID, borderwidth=1)
        self.text_home_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_home_info, "Đang tải thông tin ban đầu...")

        # --- Button to refresh Home tab info ---
        self.style.configure('RefreshHome.TButton', background=BUTTON_PRIMARY_BG, foreground="black") # Darker text for light blue
        self.button_refresh_home = ttk.Button(parent_tab, text="Làm mới Dữ liệu PC", command=self.fetch_pc_info_threaded, width=25, style='RefreshHome.TButton')
        self.button_refresh_home.pack(pady=(10,5)) # Added bottom padding

    def _create_utilities_tab(self, parent_tab):
        # --- Utilities Actions Frame ---
        # Main frame for utilities tab, allows for better organization if needed
        utilities_main_frame = ttk.Frame(parent_tab, style='TFrame')
        utilities_main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure columns: Column 0 for action buttons, Column 1 for results display
        utilities_main_frame.columnconfigure(0, weight=2) # Frame for buttons (cho nhiều không gian hơn một chút)
        utilities_main_frame.columnconfigure(1, weight=5) # Frame for results (lớn hơn đáng kể)
        utilities_main_frame.rowconfigure(0, weight=1) # Allow vertical expansion
 
        # --- Left Column: Action Buttons ---
        actions_column_frame = ttk.Frame(utilities_main_frame, style='TFrame', padding=(0,0,10,0)) # Add right padding
        actions_column_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0,5))
        
        utility_button_width = 27 # Reduced width
        utility_button_pady = (2,2) # Reduced vertical padding
        utility_button_padx = 5
        default_button_style = 'TButton'

        # --- Group: Bảo mật & Virus ---
        frame_security = ttk.LabelFrame(actions_column_frame, text="Bảo mật & Virus", padding=(10,5))
        frame_security.pack(pady=(0,10), padx=0, fill=tk.X)
        # frame_security.grid(row=0, column=0, sticky=tk.NSEW, padx=(0,5), pady=(0,10)) # Example for side-by-side

        btn_quick_scan = ttk.Button(frame_security, text="Quét Virus Nhanh", command=self.run_defender_quick_scan, width=utility_button_width, style=default_button_style)
        btn_quick_scan.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_full_scan = ttk.Button(frame_security, text="Quét Virus Toàn Bộ", command=self.run_defender_full_scan, width=utility_button_width, style=default_button_style)
        btn_full_scan.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_update_defender = ttk.Button(frame_security, text="Cập Nhật Định Nghĩa Virus", command=self.run_defender_update, width=utility_button_width, style=default_button_style)
        btn_update_defender.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)

        btn_check_firewall = ttk.Button(frame_security, text="Kiểm Tra Trạng Thái Tường Lửa", command=self.check_firewall_status_gui, width=utility_button_width, style=default_button_style)
        btn_check_firewall.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_enable_firewall = ttk.Button(frame_security, text="Bật Tường Lửa (Tất cả Profile)", command=self.enable_firewall_gui, width=utility_button_width, style=default_button_style)
        btn_enable_firewall.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_disable_firewall = ttk.Button(frame_security, text="Tắt Tường Lửa (Tất cả Profile)", command=self.disable_firewall_gui, width=utility_button_width, style=default_button_style)
        btn_disable_firewall.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)

        # --- Group: Thông tin & Chẩn đoán Hệ thống ---
        frame_diagnostics = ttk.LabelFrame(actions_column_frame, text="Thông tin & Chẩn đoán", padding=(10,5)) # Rút gọn tiêu đề
        frame_diagnostics.pack(pady=(0,10), padx=0, fill=tk.X)
        # frame_diagnostics.grid(row=0, column=1, sticky=tk.NSEW, padx=(5,0), pady=(0,10)) # Example for side-by-side

        btn_disk_usage = ttk.Button(frame_diagnostics, text="Xem Dung Lượng Ổ Đĩa", command=self.show_disk_usage, width=utility_button_width, style=default_button_style)
        btn_disk_usage.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_battery_report = ttk.Button(frame_diagnostics, text="Tạo Báo Cáo Pin (Laptop)", command=self.create_battery_report, width=utility_button_width, style=default_button_style)
        btn_battery_report.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_check_win_activation = ttk.Button(frame_diagnostics, text="Kiểm tra kích hoạt Windows", command=self.run_check_windows_activation, width=utility_button_width, style=default_button_style)
        btn_check_win_activation.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_event_logs = ttk.Button(frame_diagnostics, text="Xem Event Log Gần Đây", command=self.show_recent_event_logs, width=utility_button_width, style=default_button_style)
        btn_event_logs.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_installed_software = ttk.Button(frame_diagnostics, text="Kiểm Tra Phiên Bản Phần Mềm", command=self.show_installed_software, width=utility_button_width, style=default_button_style)
        btn_installed_software.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_wifi_info = ttk.Button(frame_diagnostics, text="Kiểm Tra Kết Nối Wifi", command=self.show_wifi_info, width=utility_button_width, style=default_button_style)
        btn_wifi_info.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_system_temps = ttk.Button(frame_diagnostics, text="Kiểm Tra Nhiệt Độ Hệ Thống", command=self.show_system_temperatures, width=utility_button_width, style=default_button_style)
        btn_system_temps.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_running_processes = ttk.Button(frame_diagnostics, text="Liệt Kê Tiến Trình Đang Chạy", command=self.show_running_processes, width=utility_button_width, style=default_button_style)
        btn_running_processes.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        btn_user_apps = ttk.Button(frame_diagnostics, text="Ứng Dụng Người Dùng Đã Cài", command=self.show_user_installed_applications, width=utility_button_width, style=default_button_style)
        btn_user_apps.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)
        # Nút mới: Thông tin RAM chi tiết
        # btn_ram_details = ttk.Button(frame_diagnostics, text="Thông Tin RAM Chi Tiết", command=self.show_ram_details, width=utility_button_width, style=default_button_style) # Chức năng này cần hàm get_ram_details được định nghĩa ở core
        # btn_ram_details.pack(pady=utility_button_pady, padx=utility_button_padx, anchor=tk.W)


        # --- Right Column: Utilities Results Display ---
        results_column_frame = ttk.Frame(utilities_main_frame, style='TFrame')
        results_column_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(5,0))
        results_column_frame.rowconfigure(0, weight=1) # Cho ScrolledText mở rộng
        results_column_frame.rowconfigure(1, weight=0) # Cho nút Lưu Kết Quả
        results_column_frame.columnconfigure(0, weight=1)

        frame_text_results_utils = ttk.LabelFrame(results_column_frame, text="Kết quả Tiện ích", padding=(10,5))
        frame_text_results_utils.grid(row=0, column=0, sticky=tk.NSEW, pady=(0,5))

        self.text_utilities_results = scrolledtext.ScrolledText(frame_text_results_utils, wrap=tk.WORD, height=10, state=tk.DISABLED, font=MONOSPACE_FONT, relief=tk.SOLID, borderwidth=1)
        self.text_utilities_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_utilities_results, "Kết quả của tiện ích sẽ hiển thị ở đây.") # Updated default text

        # Frame cho các nút dưới ô kết quả (ví dụ: Lưu, Ping)
        utils_results_buttons_frame = ttk.Frame(results_column_frame, style='TFrame')
        utils_results_buttons_frame.grid(row=1, column=0, pady=(5,0), sticky=tk.EW)

        self.button_save_utility_result = ttk.Button(utils_results_buttons_frame, text="Lưu Kết Quả", command=lambda: self.save_tab_result(self.text_utilities_results, "KetQua_TienIch"), width=20, state=tk.DISABLED)
        self.button_save_utility_result.pack(side=tk.RIGHT, padx=(5,0))
        btn_ping_test = ttk.Button(utils_results_buttons_frame, text="Kiểm Tra Ping (google.com)", command=self.run_ping_google, width=25)
        btn_ping_test.pack(side=tk.LEFT, padx=(0,5))

    def _create_fixes_tab(self, parent_tab):
        fixes_main_frame = ttk.Frame(parent_tab, style='TFrame')
        fixes_main_frame.pack(fill=tk.BOTH, expand=True)
        fixes_main_frame.columnconfigure(0, weight=2)
        fixes_main_frame.columnconfigure(1, weight=5)
        fixes_main_frame.rowconfigure(0, weight=1)

        actions_column_frame_fixes = ttk.Frame(fixes_main_frame, style='TFrame', padding=(0,0,10,0))
        actions_column_frame_fixes.grid(row=0, column=0, sticky=tk.NSEW, padx=(0,5))

        fix_button_width = 27 # Reduced width
        fix_button_pady = (2,2) # Reduced vertical padding
        fix_button_padx = 5
        default_button_style = 'TButton'

        # --- Group: Dọn dẹp & Tối ưu ---
        frame_cleanup = ttk.LabelFrame(actions_column_frame_fixes, text="Dọn dẹp & Tối ưu", padding=(10,5))
        frame_cleanup.pack(pady=(0,10), padx=0, fill=tk.X)

        btn_clear_temp = ttk.Button(frame_cleanup, text="Xóa File Tạm & Dọn Dẹp", command=self.run_clear_temp_files, width=fix_button_width, style=default_button_style)
        btn_clear_temp.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)
        btn_open_resmon = ttk.Button(frame_cleanup, text="Mở Resource Monitor", command=self.run_open_resource_monitor, width=fix_button_width, style=default_button_style)
        btn_open_resmon.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)

        # --- Group: Sửa lỗi Hệ thống ---
        frame_system_fix = ttk.LabelFrame(actions_column_frame_fixes, text="Sửa lỗi Hệ thống", padding=(10,5))
        frame_system_fix.pack(pady=(0,10), padx=0, fill=tk.X)

        btn_reset_internet = ttk.Button(frame_system_fix, text="Reset Kết Nối Internet", command=self.run_reset_internet_connection, width=fix_button_width, style=default_button_style)
        btn_reset_internet.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)
        btn_sfc_scan = ttk.Button(frame_system_fix, text="Chạy SFC Scan", command=self.run_sfc_scan_command, width=fix_button_width, style=default_button_style)
        btn_sfc_scan.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)
        # Nút mới: Tạo điểm khôi phục
        btn_create_restore_point = ttk.Button(frame_system_fix, text="Tạo Điểm Khôi Phục Hệ Thống", command=self.run_create_restore_point, width=fix_button_width, style=default_button_style)
        btn_create_restore_point.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)

        # --- Group: Cập nhật ---
        frame_updates = ttk.LabelFrame(actions_column_frame_fixes, text="Cập nhật", padding=(10,5))
        frame_updates.pack(pady=(0,10), padx=0, fill=tk.X)
        # Nút mới: Quản lý khởi động
        btn_startup_manager = ttk.Button(frame_updates, text="Quản Lý Khởi Động Cùng Windows", command=self.show_startup_programs, width=fix_button_width, style=default_button_style)
        btn_startup_manager.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)
        btn_winget_update = ttk.Button(frame_updates, text="Cập Nhật Phần Mềm (Winget)", command=self.run_winget_update_all, width=fix_button_width, style=default_button_style)
        btn_winget_update.pack(pady=fix_button_pady, padx=fix_button_padx, anchor=tk.W)

        # --- Right Column: Fixes Results Display ---
        results_column_frame_fixes = ttk.Frame(fixes_main_frame, style='TFrame')
        results_column_frame_fixes.grid(row=0, column=1, sticky=tk.NSEW, padx=(5,0))
        results_column_frame_fixes.rowconfigure(0, weight=1)
        results_column_frame_fixes.rowconfigure(1, weight=0)
        results_column_frame_fixes.columnconfigure(0, weight=1)

        frame_text_results_fixes = ttk.LabelFrame(results_column_frame_fixes, text="Kết quả Tác vụ Sửa lỗi", padding=(10,5))
        frame_text_results_fixes.grid(row=0, column=0, sticky=tk.NSEW, pady=(0,5))

        self.text_fixes_results = scrolledtext.ScrolledText(frame_text_results_fixes, wrap=tk.WORD, height=10, state=tk.DISABLED, font=MONOSPACE_FONT, relief=tk.SOLID, borderwidth=1)
        self.text_fixes_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._update_display_widget(self.text_fixes_results, "Chọn một tác vụ để thực hiện.")

        self.button_save_fix_result = ttk.Button(results_column_frame_fixes, text="Lưu Kết Quả Sửa Lỗi", command=lambda: self.save_tab_result(self.text_fixes_results, "KetQua_SuaLoi"), width=25, state=tk.DISABLED)
        self.button_save_fix_result.grid(row=1, column=0, pady=(5,0), sticky=tk.E)

    def on_floor_change(self, event=None):
        """Show/hide custom floor entry based on combobox selection."""
        user_info_pady = (5, 5) # Match padding from _create_home_tab
        user_info_padx = (5, 5)

        if self.combo_floor.get() == "Khác":
            self.entry_custom_floor_label.grid(row=2, column=2, padx=(10,user_info_padx[0]), pady=user_info_pady, sticky=tk.W)
            self.entry_custom_floor.grid(row=2, column=3, padx=(0,user_info_padx[1]), pady=user_info_pady, sticky=tk.EW)
        else:
            self.entry_custom_floor_label.grid_forget()
            self.entry_custom_floor.grid_forget()
            self.entry_custom_floor.delete(0, tk.END)

    def _update_display_widget(self, text_widget, content):
        """Safely update a given ScrolledText widget from any thread."""
        def update():
            text_widget.config(state=tk.NORMAL)
            text_widget.config(background="white", foreground=TEXT_COLOR) # Reset colors
            text_widget.delete("1.0", tk.END)
            if "Lỗi" in content or "Error" in content or "Không thể" in content: # Basic error coloring
                text_widget.config(foreground="red")
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
        # Schedule the update in the main Tkinter thread
        self.after(0, update)

    def _toggle_buttons(self, enable_refresh_home=True, enable_export_home=False, enable_save_utility=False, enable_save_fix=False):
        """Safely enable/disable buttons from any thread."""
        def toggle():
            self.button_refresh_home.config(state=tk.NORMAL if enable_refresh_home else tk.DISABLED)
            # Only enable export if data is valid
            pc_data_for_check = self.pc_info_dict.get("SystemInformation", {}).get("PC", {}) if self.pc_info_dict else {}
            has_errors_in_pc_data = isinstance(pc_data_for_check, dict) and \
                                    any("Lỗi" in str(v) or "Error" in str(v) for v in pc_data_for_check.values() if isinstance(v, str))
            can_export_home_data = enable_export_home and self.pc_info_dict and not has_errors_in_pc_data and pc_data_for_check != NOT_AVAILABLE
            self.button_export_home.config(state=tk.NORMAL if can_export_home_data else tk.DISABLED)
            
            # Enable/disable save result buttons
            self.button_save_utility_result.config(state=tk.NORMAL if enable_save_utility else tk.DISABLED)
            self.button_save_fix_result.config(state=tk.NORMAL if enable_save_fix else tk.DISABLED)
        self.after(0, toggle)

    def _fetch_task(self):
        """Task to run in a separate thread for fetching PC info."""
        try:
            self._update_display_widget(self.text_home_info, "Đang lấy thông tin, vui lòng chờ...")
            self._toggle_buttons(enable_refresh_home=False, enable_export_home=False)

            # Fetch data (potentially slow)
            self.pc_info_dict = get_detailed_system_information()

            # Format data using the manager's function
            # We only need the SystemInformation part for the home display directly
            home_info_data = self.pc_info_dict.get("SystemInformation", {"PC": {"Lỗi": "Không có dữ liệu SystemInformation"}})
            self.formatted_pc_info_string = format_system_details_to_string(home_info_data) # Format only system details for home

            # Update display and buttons
            self._update_display_widget(self.text_home_info, self.formatted_pc_info_string)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=True) # Enable export if successful

        except Exception as e:
            error_msg = f"Lỗi khi lấy thông tin:\n{e}"
            logging.exception("Lỗi trong luồng lấy thông tin PC:")
            self.pc_info_dict = None # Reset data on error
            self.formatted_pc_info_string = error_msg
            self._update_display_widget(self.text_home_info, error_msg)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=False) # Re-enable get, keep export disabled
            messagebox.showerror("Lỗi", error_msg)

    def fetch_pc_info_threaded(self):
        """Starts the info fetching process in a new thread."""
        # Create and start the thread
        fetch_thread = threading.Thread(target=self._fetch_task, daemon=True)
        fetch_thread.start()

    def on_export_info(self):
        """Handles the 'Export File' button click."""
        if not self.pc_info_dict:
            messagebox.showwarning("Chưa có thông tin", "Thông tin Trang chủ chưa được tải. Vui lòng đợi hoặc làm mới.")
            return

        try:
            # 1. Get user info from GUI
            user_name = self.entry_name.get().strip()
            department = self.entry_department.get().strip()
            floor_selection = self.combo_floor.get()
            custom_floor = self.entry_custom_floor.get().strip() if floor_selection == "Khác" else ""
            position = self.entry_position.get().strip()
            notes = self.text_notes.get("1.0", tk.END).strip()
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
            # Use the already formatted PC info string
            full_content_to_save = f"{formatted_user_text}\n\n{full_formatted_pc_info_for_file}"

            # 7. Generate filename
            filename = generate_filename(user_info, self.pc_info_dict)

            # 8. Determine save path
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Exports_Formatted_TXT")
            file_path = os.path.join(save_dir, filename)

            # 9. Save the file
            save_text_to_file(full_content_to_save, file_path) # Raises exceptions on failure

            # 10. Show success message (consider making the network path configurable or just instructional)
            network_instruction = "\\\\pc-it-08\\Tools\\User" # Keep as instruction?
            messagebox.showinfo(
                "Thành Công",
                f"Thông tin đã được lưu thành công vào file:\n{file_path}\n\n"
                f"Vui lòng copy file này và dán vào thư mục bằng cách nhấn Win+R "
                f"và nhập: {network_instruction}"
            )

        except ValueError as ve: # Validation error
            messagebox.showerror("Thiếu thông tin", str(ve))
        except (IOError, RuntimeError) as save_e: # File saving error
             messagebox.showerror("Lỗi Lưu File", f"Không thể lưu file:\n{save_e}")
        except Exception as e: # Other unexpected errors
            messagebox.showerror("Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi xuất file: {e}")
            logging.exception("Lỗi không xác định khi xuất file:")

    def save_tab_result(self, text_widget, default_prefix="KetQua"):
        """Saves the content of a ScrolledText widget to a .txt file."""
        content = text_widget.get("1.0", tk.END).strip()
        if not content or content == "Kết quả của tiện ích sẽ hiển thị ở đây." or content == "Chọn một tác vụ để thực hiện." or "Đang thực hiện:" in content:
            messagebox.showwarning("Không có kết quả", "Không có kết quả để lưu hoặc tác vụ đang chạy.")
            return

        try:
            # Generate a simple filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{default_prefix}_{timestamp}.txt"
            
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Tool_Results")
            file_path = os.path.join(save_dir, filename)

            save_text_to_file(content, file_path)
            messagebox.showinfo("Lưu Thành Công", f"Kết quả đã được lưu vào:\n{file_path}")

        except (IOError, RuntimeError) as save_e:
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu file kết quả:\n{save_e}")
        except Exception as e:
            messagebox.showerror("Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi lưu kết quả: {e}")
            logging.exception("Lỗi không xác định khi lưu kết quả tab:")

    def _format_task_result_for_display(self, result_data):
        """Formats the result data from a utility/fix task for display in a ScrolledText widget."""
        if isinstance(result_data, list):
            formatted_items = []
            for item in result_data:
                if isinstance(item, dict):
                    # Nicer formatting for dicts within a list
                    item_str = "\n".join([f"  {k}: {v}" for k, v in item.items()])
                    formatted_items.append(item_str)
                else:
                    formatted_items.append(str(item))
            final_display_text = "\n---\n".join(formatted_items)
            if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về."
        elif isinstance(result_data, dict):
            if "message" in result_data and "status" in result_data: # Standard status dict
                final_display_text = f"Trạng thái: {result_data.get('status', 'N/A')}\nThông điệp: {result_data['message']}"
                if "details" in result_data and result_data['details']:
                    details_content = result_data['details']
                    if isinstance(details_content, dict): # For structured details like from clear_temp
                        details_str = "\n".join([f"  {k_detail}: {v_detail}" for k_detail, v_detail in details_content.items() if k_detail != 'errors_list']) # Exclude raw error list for now
                        if 'errors_list' in details_content and details_content['errors_list']:
                            details_str += f"\n  Lỗi chi tiết:\n    " + "\n    ".join(details_content['errors_list'][:5]) + ("..." if len(details_content['errors_list']) > 5 else "") # Show first 5 errors
                        final_display_text += f"\n\nChi tiết:\n{details_str}"
                    else: # Generic details string
                        final_display_text += f"\n\nChi tiết:\n{details_content}"
                if "path" in result_data and result_data['path']: final_display_text += f"\n\nĐường dẫn file: {result_data['path']}" # For battery report etc.
            else: # Generic dict
                final_display_text = "\n".join([f"{k}: {v}" for k, v in result_data.items()])
                if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng)."
        else:
            final_display_text = str(result_data) if result_data is not None else "Tác vụ hoàn thành, không có dữ liệu trả về."

        return final_display_text




    # --- Handlers for Utilities Tab ---
    def _run_task_in_thread(self, target_widget, task_function, needs_wmi=False, *task_args):
        """
        Generic helper to run a task (utility or fix) in a separate thread.
        Handles WMI connection if needed and updates the target display widget.
        """
        # Disable the button that triggered this? (More complex, needs button passed or identified)
        # For now, user sees "Đang thực hiện..."
        self._update_display_widget(target_widget, f"Đang thực hiện: {task_function.__name__}...")
        # Disable save button for this tab
        if target_widget == self.text_utilities_results:
            self._toggle_buttons(enable_save_utility=False)
        elif target_widget == self.text_fixes_results:
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
                        # Prepend wmi_service to the arguments for the task_function
                        result_data = task_function(wmi_service_local, *task_args)
                else:
                    result_data = task_function(*task_args)

                self._update_display_widget(target_widget, self._format_task_result_for_display(result_data))
            except Exception as e:
                logging.exception(f"Lỗi khi chạy tiện ích {task_function.__name__}:")
                self._update_display_widget(target_widget, f"Lỗi khi thực hiện {task_function.__name__}:\n{e}")
            finally:
                if com_initialized_local: # Only uninitialize if this wrapper initialized it
                    try:
                        win32com.client.pythoncom.CoUninitialize()
                        logging.info(f"Đã giải phóng COM cho tác vụ {task_function.__name__}.")
                    except Exception as com_e:
                        logging.error(f"Lỗi khi giải phóng COM cho tác vụ {task_function.__name__}: {com_e}")
                # Re-enable save button for this tab
                if target_widget == self.text_utilities_results:
                    self._toggle_buttons(enable_save_utility=True)
                elif target_widget == self.text_fixes_results:
                    self._toggle_buttons(enable_save_fix=True)
                # Re-enable the button here if it was disabled

        threading.Thread(target=task_wrapper, daemon=True).start()

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
        self._run_task_in_thread(self.text_utilities_results, get_system_temperatures, needs_wmi=True) # Assuming WMI might be used

    def show_running_processes(self):
        self._run_task_in_thread(self.text_utilities_results, get_running_processes)

    def show_user_installed_applications(self):
        self._run_task_in_thread(self.text_utilities_results, get_installed_software_versions, needs_wmi=False) # wmi_service không còn cần thiết trực tiếp cho hàm này nữa

    # def show_ram_details(self):
    #     # Để sử dụng chức năng này, bạn cần định nghĩa hàm get_ram_details trong core.pc_info_functions.py
    #     self._run_task_in_thread(self.text_utilities_results, get_ram_details, needs_wmi=True)

    def run_ping_google(self):
        self._run_task_in_thread(self.text_utilities_results, run_ping_test, False, "google.com", 4) # host, count

    def run_defender_quick_scan(self):
        self._run_task_in_thread(self.text_utilities_results, run_windows_defender_scan, False, "QuickScan") # False for needs_wmi

    def run_defender_full_scan(self):
        self._run_task_in_thread(self.text_utilities_results, run_windows_defender_scan, False, "FullScan")

    def run_defender_update(self):
        self._run_task_in_thread(self.text_utilities_results, update_windows_defender_definitions)

    def check_firewall_status_gui(self):
        self._run_task_in_thread(self.text_utilities_results, get_firewall_status)

    def enable_firewall_gui(self):
        # Xác nhận trước khi bật
        if messagebox.askyesno("Xác nhận Bật Tường lửa", "Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?"):
            self._run_task_in_thread(self.text_utilities_results, toggle_firewall, False, True) # True để enable

    def disable_firewall_gui(self):
        # Xác nhận trước khi tắt, cảnh báo nguy cơ
        if messagebox.askyesno("XÁC NHẬN TẮT TƯỜNG LỬA", "CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?", icon='warning'):
            self._run_task_in_thread(self.text_utilities_results, toggle_firewall, False, False) # False để disable

    # --- Handlers for Fixes Tab ---
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
    app = PcInfoApp()
    # Example: Set window icon (ensure the .ico file exists at the specified path)
    # You might need to adjust the path or handle potential errors if the icon file is missing.
    # app.iconbitmap(resource_path(os.path.join("assets", "logo", "hpc-logo.ico")))
    app.mainloop()
