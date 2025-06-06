## gui/gui_qt.py
# Tạo giao diện chính với PyQt5
import sys
import os
import logging
import html # Thêm import html để escape nội dung
import csv # Import the csv module
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QStackedWidget, QListWidget, QListWidgetItem, QSplitter, QDialog, QFormLayout, QDialogButtonBox, QProgressBar,
    QGroupBox, QScrollArea, QMessageBox, QFileDialog, QGridLayout, QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog,
    QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextOption, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize # Import QSize

import win32com.client # For CoInitialize/CoUninitialize in threads

# Import các hàm cần thiết từ core
# Đảm bảo rằng Python có thể tìm thấy các module này.
# Nếu chạy main.py từ thư mục gốc, sys.path đã được điều chỉnh.
from core.pc_info_functions import ( # type: ignore
    get_detailed_system_information, NOT_AVAILABLE, ERROR_WMI_CONNECTION, NOT_FOUND,
    get_disk_partitions_usage, generate_battery_report, check_windows_activation_status,
    open_resource_monitor, clear_temporary_files, get_recent_event_logs,
    get_installed_software_versions, get_wifi_connection_info, get_system_temperatures,
    get_running_processes, reset_internet_connection, run_sfc_scan,
    update_all_winget_packages, run_windows_defender_scan,
    update_windows_defender_definitions, get_firewall_status, toggle_firewall, 
    get_network_configuration_details, # Import hàm mới
    get_startup_programs, run_ping_test, create_system_restore_point,
    # Giả định các hàm này sẽ được tạo trong core.pc_info_functions.py
    lookup_dns_address,      # Ví dụ: lookup_dns_address("google.com")
    get_active_network_connections, # Ví dụ: netstat    
    # Các hàm cho tính năng (một số sẽ bị loại bỏ khỏi GUI)
    run_cpu_benchmark, run_gpu_benchmark, run_memory_speed_test, run_disk_speed_test, # Cho tab Hiệu năng
    optimize_windows_services, clean_registry_with_backup, # Cho tab Fix Hệ Thống
    get_disk_health_status,   # Hàm mới cho tình trạng ổ cứng
    get_battery_details,      # Hàm mới cho chi tiết pin
    set_dns_servers,          # Hàm mới để cấu hình DNS
    flush_dns_cache           # Ví dụ: ipconfig /flushdns
)
from core.pc_info_manager import (
    validate_user_input, generate_filename, save_text_to_file,
    format_pc_info_to_string, format_system_details_to_string,
    format_user_info_for_display # Import hàm này
)

# --- Cấu hình Logging ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Logging nên được cấu hình ở main.py để tránh ghi đè hoặc xung đột

# --- Constants for UI Styling (Có thể dùng QSS sau) ---
DEFAULT_FONT_FAMILY = "Roboto"
MONOSPACE_FONT_FAMILY = "Consolas"
MONOSPACE_FONT_SIZE = 9
HIGHLIGHT_COLOR = QColor(255, 236, 179) # Material Amber A100 (FFECB3) for text search
H1_FONT_SIZE = 16
H2_FONT_SIZE = 12
BODY_FONT_SIZE = 10


# New Color Palette (Material Design inspired)
PRIMARY_COLOR = "#2196F3"  # Xanh dương (Blue)
SECONDARY_COLOR = "#4CAF50" # Xanh lá (Green)
ACCENT_COLOR = "#FF9800"   # Cam (Orange)

WINDOW_BG = "#E3F2FD"        # Light Blue 50 (Main background, derived from Primary)
FRAME_BG = "#FFFFFF"         # White (For content containers like tab panes - kept)
GROUPBOX_BG = "#FFFFFF"      # White (Background for GroupBoxes - kept)
TEXT_COLOR_PRIMARY = "#212121" # Dark Grey (Good contrast)
TEXT_COLOR_SECONDARY = "#757575" # Medium Grey

BORDER_COLOR_LIGHT = "#BBDEFB" # Light Blue 100 (Derived from Primary)
BORDER_COLOR_DARK = "#90CAF9"  # Light Blue 200 (Derived from Primary, for scrollbar handles etc.)

ACCENT_COLOR_HOVER = "#FFA726"  # Orange 400 (Derived from Accent)
ACCENT_COLOR_PRESSED = "#FB8C00" # Orange 600 (Derived from Accent)

BUTTON_PRIMARY_BG = PRIMARY_COLOR
BUTTON_PRIMARY_HOVER = "#1E88E5"  # Blue 600 (Derived from Primary)
BUTTON_PRIMARY_PRESSED = "#1976D2" # Blue 700 (Derived from Primary)

BUTTON_SECONDARY_BG = "#E0E0E0" # Grey 300 (Neutral secondary button)
BUTTON_SECONDARY_HOVER = "#BDBDBD" # Grey 400
BUTTON_SECONDARY_PRESSED = "#9E9E9E" # Grey 500
BUTTON_SECONDARY_TEXT = TEXT_COLOR_PRIMARY

BUTTON_EXPORT_BG = SECONDARY_COLOR
BUTTON_EXPORT_HOVER = "#43A047" # Green 600 (Darker shade of Secondary)
BUTTON_EXPORT_PRESSED = "#388E3C" # Green 700 (Even darker shade of Secondary)

BUTTON_DANGER_BG = "#F44336"  # Red 500
BUTTON_DANGER_HOVER = "#E53935" # Red 600

INPUT_BG = "#FFFFFF"         # Background for QLineEdit, QComboBox, etc.
INPUT_BORDER_COLOR = "#BDBDBD" # Grey 400 for input borders (Neutral)

TAB_BG_INACTIVE = "#90CAF9" # Light Blue 200 (Derived from Primary, same as BORDER_COLOR_DARK)

TAB_BG_ACTIVE = FRAME_BG    # White, same as pane
TAB_TEXT_INACTIVE = TEXT_COLOR_PRIMARY
TAB_TEXT_ACTIVE = ACCENT_COLOR # Orange for active tab text

# HTML text colors (used in _update_display_widget)
DEFAULT_TEXT_COLOR_HTML = TEXT_COLOR_PRIMARY
ERROR_TEXT_COLOR_HTML = BUTTON_DANGER_BG

# Toast Notification Colors
TOAST_INFO_BG = "rgba(33, 150, 243, 220)"  # Blue (Primary Color with alpha)
TOAST_SUCCESS_BG = "rgba(76, 175, 80, 220)" # Green (Secondary Color with alpha)
TOAST_ERROR_BG = "rgba(244, 67, 54, 220)"   # Red (Danger Color with alpha)
TOAST_TEXT_COLOR = "white"

# --- Status Bar Colors ---
STATUS_BAR_INFO_BG = "#BBDEFB"  # Light Blue 100
STATUS_BAR_SUCCESS_BG = "#C8E6C9" # Green 100
STATUS_BAR_WARNING_BG = "#FFF9C4" # Yellow 100
STATUS_BAR_ERROR_BG = "#FFCDD2"   # Red 100
STATUS_BAR_TEXT_COLOR = "#212121" # Dark Grey
# class PcInfoAppQt(QMainWindow): # Forward declaration removed or ensure constants are in the main class


class ToastNotification(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        self.default_style_sheet = f"""
            QLabel {{
                color: {TOAST_TEXT_COLOR};
                background-color: {TOAST_INFO_BG};
                padding: 10px 18px;
                border-radius: 6px;
                border: 1px solid rgba(0, 0, 0, 0.1); /* Thêm viền mờ nhẹ */
                font-size: 10pt;
                font-family: "{DEFAULT_FONT_FAMILY}";
            }}
        """
        self.setStyleSheet(self.default_style_sheet)
        self.setAlignment(Qt.AlignCenter)
        self.hide()

    def show_toast(self, message, duration_ms=5000, parent_widget=None, toast_type='info'):
        self.setText(message)
        self.adjustSize() # Điều chỉnh kích thước dựa trên nội dung mới

        if parent_widget:
            # Lấy tọa độ toàn cục và kích thước của parent_widget
            # để định vị chính xác cửa sổ toast (là top-level)
            parent_top_left_global = parent_widget.mapToGlobal(parent_widget.rect().topLeft())
            parent_width = parent_widget.width()
            parent_height = parent_widget.height()

            margin = 20  # Khoảng cách từ các cạnh của parent_widget

            # Tính toán vị trí cho góc dưới-phải của parent_widget
            toast_x = parent_top_left_global.x() + parent_width - self.width() - margin
            toast_y = parent_top_left_global.y() + parent_height - self.height() - margin
            
            # Đảm bảo toast không bị đẩy ra ngoài màn hình nếu parent_widget quá nhỏ hoặc ở gần cạnh màn hình
            # (Có thể thêm logic kiểm tra screen geometry ở đây nếu cần thiết)

            self.move(toast_x, toast_y)
        # else:
            # Nếu không có parent_widget, toast có thể xuất hiện ở góc màn hình
            # hoặc dựa trên vị trí cuối cùng của nó.

        bg_color = TOAST_INFO_BG if toast_type == 'info' else (TOAST_SUCCESS_BG if toast_type == 'success' else TOAST_ERROR_BG)
        self.setStyleSheet(f"QLabel {{ color: {TOAST_TEXT_COLOR}; background-color: {bg_color}; padding: 10px 18px; border-radius: 6px; border: 1px solid rgba(0,0,0,0.15); font-size: 10pt; font-family: \"{DEFAULT_FONT_FAMILY}\"; }}")
        
        self.show()
        self.timer.start(duration_ms)

# HTML text colors (used in _update_display_widget)
DEFAULT_TEXT_COLOR_HTML = TEXT_COLOR_PRIMARY
ERROR_TEXT_COLOR_HTML = BUTTON_DANGER_BG

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối của resource (ảnh, file...) để tương thích với PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError: # Sửa lỗi AttributeError khi không chạy từ PyInstaller
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

# --- Lớp QThread cho các tác vụ chạy nền ---
class WorkerThread(QThread):
    task_completed = pyqtSignal(str, object) # task_name, result_data
    task_error = pyqtSignal(str, str)       # task_name, error_message

    def __init__(self, task_function, task_name, needs_wmi=False, wmi_namespace="root\\CIMV2", *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.task_name = task_name
        self.needs_wmi = needs_wmi
        self.button_to_manage = kwargs.pop('button_to_manage', None) # Get the button
        self.original_button_text = kwargs.pop('original_button_text', "")
        self.wmi_namespace = wmi_namespace # Namespace WMI cần thiết cho tác vụ
        self.args = args
        self.kwargs = kwargs
        self.wmi_service_local = None
        self.com_initialized_local = False

    def run(self):
        if self.button_to_manage:
            self.button_to_manage.setEnabled(False)
            self.button_to_manage.setText("Đang xử lý...")

        result_data = None
        try:
            if self.needs_wmi:
                win32com.client.pythoncom.CoInitialize()
                self.com_initialized_local = True
                wmi_locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
                self.wmi_service_local = wmi_locator.ConnectServer(".", self.wmi_namespace)
                logging.info(f"WMI connected to {self.wmi_namespace} in thread for task: {self.task_name}")

                if not self.wmi_service_local:
                    self.task_error.emit(self.task_name, f"{ERROR_WMI_CONNECTION} for task {self.task_name}")
                    return
                result_data = self.task_function(self.wmi_service_local, *self.args, **self.kwargs)
            else:
                result_data = self.task_function(*self.args, **self.kwargs)

            self.task_completed.emit(self.task_name, result_data)

        except Exception as e:
            logging.exception(f"Error in worker thread for task {self.task_name}:")
            self.task_error.emit(self.task_name, str(e))
        finally:
            if self.com_initialized_local:
                try:
                    win32com.client.pythoncom.CoUninitialize()
                    logging.info(f"COM uninitialized in thread for task: {self.task_name}")
                except Exception as com_e:
                    logging.error(f"Error uninitializing COM in thread for {self.task_name}: {com_e}")
            if self.button_to_manage:
                self.button_to_manage.setText(self.original_button_text)
                self.button_to_manage.setEnabled(True)

class SetDnsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cấu hình DNS")
        self.setObjectName("SetDnsDialog") # Thêm objectName để styling
        self.setMinimumWidth(350)

        layout = QFormLayout(self)

        self.primary_dns_input = QLineEdit()
        self.primary_dns_input.setPlaceholderText("8.8.8.8")
        layout.addRow("DNS Chính:", self.primary_dns_input)

        self.secondary_dns_input = QLineEdit()
        self.secondary_dns_input.setPlaceholderText("1.1.1.1 (hoặc để trống)")
        layout.addRow("DNS Phụ:", self.secondary_dns_input)

        self.note_label = QLabel("Lưu ý: Thay đổi DNS yêu cầu quyền Administrator.\nCác DNS phổ biến: Google (8.8.8.8, 8.8.4.4), Cloudflare (1.1.1.1, 1.0.0.1)")
        self.note_label.setWordWrap(True)
        layout.addRow(self.note_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_dns_values(self):
        primary = self.primary_dns_input.text().strip()
        secondary = self.secondary_dns_input.text().strip()
        if not primary: # Nếu DNS chính trống, sử dụng placeholder
            primary = self.primary_dns_input.placeholderText()
        return primary, secondary if secondary else None # Trả về None nếu secondary trống

class PcInfoAppQt(QMainWindow):
    # Define common strings that represent unavailable or empty data
    UNAVAILABLE_STR_CONSTANTS = {
        NOT_AVAILABLE, # From core.pc_info_functions # type: ignore
        NOT_FOUND,     # From core.pc_info_functions
        "Unknown",
        "None",        # String "None"
        "",            # Empty string after strip
        "N/A",
        "Không xác định",
        "Not Available"
    }
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tối Ưu PC Pro") # Đổi tên ứng dụng
        self.setGeometry(100, 100, 950, 800) # Tăng kích thước một chút

        self.h1_font = QFont(DEFAULT_FONT_FAMILY, H1_FONT_SIZE, QFont.Bold)
        self.h2_font = QFont(DEFAULT_FONT_FAMILY, H2_FONT_SIZE, QFont.Bold)
        self.body_font = QFont(DEFAULT_FONT_FAMILY, BODY_FONT_SIZE)
        self.monospace_font = QFont(MONOSPACE_FONT_FAMILY, MONOSPACE_FONT_SIZE)

        # --- State Variables ---
        self.pc_info_dict = None
        # self.formatted_pc_info_string_home = "Chưa lấy thông tin." # No longer needed as we populate cards
        self.current_table_data = None # To store data for CSV export

        self.NAV_EXPANDED_WIDTH = 200
        self.NAV_COLLAPSED_WIDTH = 55 # Adjusted for icon + padding
        self.nav_panel_is_collapsed = False
        self.nav_is_collapsed = False # State for navigation panel

        self.threads = [] # List để giữ các QThread đang chạy

        self._load_logo()
        self._init_timers() # Khởi tạo các QTimer cho debouncing
        self._create_widgets()
        self._apply_styles()
        self.toast_notifier = ToastNotification(self) # Khởi tạo toast notifier

        self.fetch_pc_info_threaded()

    def _load_logo(self):
        self.logo_pixmap = None
        try:
            logo_relative_path = os.path.join("assets", "logo", "hpc-logo.png")
            logo_path = resource_path(logo_relative_path)
            if os.path.exists(logo_path):
                self.logo_pixmap = QPixmap(logo_path)
                if not self.logo_pixmap.isNull():
                    self.logo_pixmap = self.logo_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    logging.warning(f"Không thể tải QPixmap từ: {logo_path}")
                    self.logo_pixmap = None
            else:
                logging.warning(f"Không tìm thấy file logo tại: {logo_path}")
        except Exception as e:
            logging.error(f"Lỗi khi tải logo: {e}", exc_info=True)

    def _init_timers(self):
        """Khởi tạo QTimers cho việc debouncing các sự kiện tìm kiếm."""
        self.global_search_timer = QTimer(self)
        self.global_search_timer.setSingleShot(True)
        self.global_search_timer.timeout.connect(self._perform_global_search)

    def _create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Top Header Bar (New) ---
        top_header_bar = QFrame()
        top_header_bar.setObjectName("TopHeaderBar")
        top_header_layout = QHBoxLayout(top_header_bar)
        top_header_layout.setContentsMargins(5, 5, 10, 5)
        top_header_layout.setSpacing(10)

        # Navigation Toggle Button (Moved to Header)
        self.button_toggle_nav_header = QPushButton()
        self.button_toggle_nav_header.setCursor(Qt.PointingHandCursor)
        self.button_toggle_nav_header.setObjectName("NavToggleHeaderButton")
        self.button_toggle_nav_header.clicked.connect(self._toggle_nav_panel_visibility)
        self.button_toggle_nav_header.setFixedSize(35, 35) # Kích thước cho nút icon
        top_header_layout.addWidget(self.button_toggle_nav_header)

        try:
            self.icon_collapse_nav = QIcon(resource_path(os.path.join("assets", "icons", "menu_collapse.png"))) # e.g. left arrow or hamburger
            self.icon_expand_nav = QIcon(resource_path(os.path.join("assets", "icons", "menu_expand.png")))     # e.g. right arrow
        except Exception as e:
            logging.warning(f"Không thể tải icon cho nút thu/gọn thanh điều hướng: {e}")

        # App Title and Logo
        app_title_label = QLabel("Tối Ưu PC Pro")
        app_title_label.setFont(self.h1_font)
        app_title_label.setObjectName("AppTitleLabel")
        top_header_layout.addWidget(app_title_label)
        
        if self.logo_pixmap:
            self.logo_label = QLabel()
            self.logo_label.setPixmap(self.logo_pixmap)
            self.logo_label.setContentsMargins(5,0,5,0)
            top_header_layout.addWidget(self.logo_label)

        top_header_layout.addStretch(1) # Push search to the right

        # Global Search Bar (Moved to Header)
        self.search_bar_container = QWidget()
        search_bar_layout = QHBoxLayout(self.search_bar_container)
        search_bar_layout.setContentsMargins(0,0,0,0) # No margins for search bar container itself
        self.global_search_input = QLineEdit()
        self.global_search_input.setFont(self.body_font)
        self.global_search_input.setPlaceholderText("Tìm kiếm...")
        self.global_search_input.textChanged.connect(lambda: self.global_search_timer.start(300))
        search_bar_layout.addWidget(self.global_search_input)
        self.search_bar_container.setFixedWidth(250) # Set a fixed width for search bar
        self.search_bar_container.setVisible(False) # Initially hidden, shown by _on_navigation_changed
        top_header_layout.addWidget(self.search_bar_container)

        self.main_layout.addWidget(top_header_bar)

        # --- Main content area with Side Navigation and StackedWidget ---
        self.main_content_splitter = QSplitter(Qt.Horizontal) # Assign to self
        self.main_layout.addWidget(self.main_content_splitter, 1) # Add splitter with stretch factor

        # --- Left: Navigation Panel (Container for List and Toggle Button) ---
        left_nav_panel_widget = QWidget()
        left_nav_panel_layout = QVBoxLayout(left_nav_panel_widget)
        left_nav_panel_layout.setContentsMargins(0,0,0,0)
        left_nav_panel_layout.setSpacing(0) # No spacing between list and button

        self.nav_list_widget = QListWidget()
        self.nav_list_widget.setFont(self.h2_font) # Use H2 font for nav items
        # self.nav_list_widget.setFixedWidth(self.NAV_EXPANDED_WIDTH) # Width will be controlled by splitter
        self.nav_list_widget.setObjectName("NavList")
        left_nav_panel_layout.addWidget(self.nav_list_widget, 1) # List takes available space


        self.main_content_splitter.addWidget(left_nav_panel_widget)

        # --- Right: Content Area (Search + StackedWidget) ---
        right_pane_widget = QWidget()
        right_pane_layout = QVBoxLayout(right_pane_widget)
        right_pane_layout.setContentsMargins(0,0,0,0) # No margins for the container itself
        right_pane_layout.setSpacing(5)


        self.pages_stack = QStackedWidget()
        right_pane_layout.addWidget(self.pages_stack, 1) # StackedWidget takes remaining space

        self.main_content_splitter.addWidget(right_pane_widget)
        self.main_content_splitter.setSizes([self.NAV_EXPANDED_WIDTH, 750]) # Initial sizes for nav and content

        # --- Global Buttons Frame ---
        # MOVED EARLIER TO ENSURE BUTTONS EXIST BEFORE _on_navigation_changed IS CALLED
        global_buttons_frame = QFrame()
        global_buttons_layout = QHBoxLayout(global_buttons_frame)
        global_buttons_layout.setContentsMargins(10, 5, 10, 5) # Thêm margins cho global buttons

        global_buttons_layout.addStretch(1) # Stretch sẽ đẩy các nút sau nó sang phải

        # --- Nút Làm mới Dashboard (sẽ được hiển thị/ẩn tùy theo tab) ---
        self.button_refresh_dashboard_qt = QPushButton("Làm mới Dashboard") # Đổi tên
        self.button_refresh_dashboard_qt.setFont(self.body_font)
        self.button_refresh_dashboard_qt.setCursor(Qt.PointingHandCursor)
        self.button_refresh_dashboard_qt.clicked.connect(self.fetch_pc_info_threaded)
        self.button_refresh_dashboard_qt.setVisible(False) # Ban đầu ẩn
        global_buttons_layout.addWidget(self.button_refresh_dashboard_qt)

        self.button_save_active_tab_result = QPushButton("Lưu Kết Quả Tab")
        self.button_save_active_tab_result.setFont(self.body_font)
        self.button_save_active_tab_result.setFixedWidth(180) # Điều chỉnh độ rộng nếu cần
        self.button_save_active_tab_result.setCursor(Qt.PointingHandCursor)
        self.button_save_active_tab_result.clicked.connect(self.on_save_active_tab_result_qt)
        self.button_save_active_tab_result.setVisible(False) # Ban đầu ẩn, sẽ được quản lý bởi _update_active_save_button_state
        global_buttons_layout.addWidget(self.button_save_active_tab_result) # Thêm nút lưu/xuất


        # --- Populate Navigation and Pages ---
        self.page_dashboard = QWidget()
        self._create_dashboard_tab(self.page_dashboard) # New/Renamed method
        self._add_navigation_item("📊 Dashboard", self.page_dashboard, icon_path=resource_path(os.path.join("assets", "icons", "dashboard.png")))

        self.page_system_info = QWidget()
        self._create_system_info_tab(self.page_system_info) # New method
        self._add_navigation_item("💻 Hệ Thống", self.page_system_info, icon_path=resource_path(os.path.join("assets", "icons", "system.png")))

        self.page_security = QWidget()
        self._create_security_tab(self.page_security) # New method
        self._add_navigation_item("🛡️ Bảo Mật", self.page_security, icon_path=resource_path(os.path.join("assets", "icons", "security.png")))

        self.page_optimize = QWidget()
        self._create_optimize_tab(self.page_optimize) # New method
        self._add_navigation_item("🔧 Tối Ưu", self.page_optimize, icon_path=resource_path(os.path.join("assets", "icons", "optimize.png")))

        self.page_network = QWidget()
        self._create_network_tab(self.page_network) # New method
        self._add_navigation_item("🌐 Mạng", self.page_network, icon_path=resource_path(os.path.join("assets", "icons", "network.png")))

        self.page_report_settings = QWidget() # Was page_about
        self._create_report_settings_tab(self.page_report_settings) # Renamed method
        self._add_navigation_item("📋 Báo Cáo & Cài đặt", self.page_report_settings, icon_path=resource_path(os.path.join("assets", "icons", "report.png")))

        self.nav_list_widget.currentRowChanged.connect(self._on_navigation_changed)
        self.nav_list_widget.setCurrentRow(0) # Select the first item
        self._update_toggle_nav_button_state() # Set initial tooltip

        # self.button_export_csv = QPushButton("Xuất CSV (Bảng)")
        # self.button_export_csv.setFont(self.default_font)
        # self.button_export_csv.setFixedWidth(150)
        # self.button_export_csv.setCursor(Qt.PointingHandCursor)
        # self.button_export_csv.clicked.connect(self.on_export_csv_qt)
        # self.button_export_csv.setVisible(False) # Initially hidden
        # global_buttons_layout.addWidget(self.button_export_csv)
        # global_buttons_layout.addStretch(1) # Removed to keep export buttons together

        self.button_exit = QPushButton("Thoát")
        self.button_exit.setFont(self.body_font)
        self.button_exit.setFixedWidth(150)
        self.button_exit.setCursor(Qt.PointingHandCursor)
        self.button_exit.clicked.connect(self.close)
        global_buttons_layout.addWidget(self.button_exit)

        self.main_layout.addWidget(global_buttons_frame)

    def _add_navigation_item(self, name, page_widget, icon_path=None):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # item.setSizeHint(QSize(0, 35)) # Adjust item height if needed
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    item.setIcon(icon)
                else:
                    logging.warning(f"Could not create QIcon from: {icon_path} for item '{name}'")
            except Exception as e:
                logging.warning(f"Error loading icon {icon_path} for item '{name}': {e}")
        elif icon_path:
             logging.warning(f"Icon path not found: {icon_path} for item '{name}'")

        self.nav_list_widget.addItem(item)
        self.pages_stack.addWidget(page_widget)
        # Set icon size for the list widget items if desired
        icon_dimension = int(self.nav_list_widget.fontMetrics().height() * 1.2) # Calculate dimension as integer
        self.nav_list_widget.setIconSize(QSize(icon_dimension, icon_dimension)) # Create QSize object

    def _create_dashboard_tab(self, parent_tab_widget):
        layout = QVBoxLayout(parent_tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # --- System Status Display ---
        self.label_system_status = QLabel("Đang kiểm tra trạng thái hệ thống...")
        self.label_system_status.setFont(self.h2_font) # Hoặc một font lớn hơn
        self.label_system_status.setAlignment(Qt.AlignCenter)
        self.label_system_status.setObjectName("SystemStatusLabel")
        layout.addWidget(self.label_system_status)

        # --- Hardware Info Grid (CPU, RAM, SSD, GPU with ProgressBars) ---
        hardware_grid_group = QGroupBox("Tổng Quan Hệ Thống")
        hardware_grid_group.setFont(self.h2_font)
        grid_layout = QGridLayout(hardware_grid_group)
        grid_layout.setSpacing(10)

        # Helper to create a hardware row
        def create_hw_row(label_text):
            hw_label = QLabel(label_text)
            hw_label.setFont(self.body_font)
            hw_progress = QProgressBar()
            hw_progress.setFont(self.body_font)
            hw_progress.setRange(0, 100)
            hw_progress.setTextVisible(True)
            hw_progress.setFixedHeight(22)
            return hw_label, hw_progress

        # CPU
        self.label_cpu_name, self.progress_cpu = create_hw_row("CPU:")
        grid_layout.addWidget(self.label_cpu_name, 0, 0)
        grid_layout.addWidget(self.progress_cpu, 0, 1)

        # RAM
        self.label_ram_info, self.progress_ram = create_hw_row("RAM:")
        grid_layout.addWidget(self.label_ram_info, 1, 0)
        grid_layout.addWidget(self.progress_ram, 1, 1)

        # SSD (Primary Disk)
        self.label_ssd_info, self.progress_ssd = create_hw_row("SSD/HDD:")
        grid_layout.addWidget(self.label_ssd_info, 2, 0)
        grid_layout.addWidget(self.progress_ssd, 2, 1)

        # GPU
        self.label_gpu_info, self.progress_gpu = create_hw_row("GPU:")
        grid_layout.addWidget(self.label_gpu_info, 3, 0)
        grid_layout.addWidget(self.progress_gpu, 3, 1)
        
        grid_layout.setColumnStretch(0, 1) # Label column
        grid_layout.setColumnStretch(1, 3) # ProgressBar column (takes more space)

        layout.addWidget(hardware_grid_group)
        layout.addStretch(1) # Push content to top

        # Initialize progress bars with placeholder values
        self.progress_cpu.setValue(0)
        self.label_cpu_name.setText("CPU: Đang tải...")
        self.progress_ram.setValue(0)
        self.label_ram_info.setText("RAM: Đang tải...")
        self.progress_ssd.setValue(0)
        self.label_ssd_info.setText("SSD/HDD: Đang tải...")
        self.progress_gpu.setValue(0)
        self.label_gpu_info.setText("GPU: Đang tải...")

    def _create_system_info_tab(self, parent_tab_widget): # Was _create_home_tab
        layout = QVBoxLayout(parent_tab_widget)
        layout.setSpacing(15)
        # --- User Info Frame (QGroupBox) ---
        group_user_info = QGroupBox("Thông tin người dùng")
        group_user_info.setFont(self.h2_font) # Sử dụng font tiêu đề H2
        layout.addWidget(group_user_info)
        user_info_grid_layout = QGridLayout(group_user_info) # Đổi tên để rõ ràng hơn
        group_user_info.setObjectName("UserInfoGroup")

        # Dòng 1: Tên và Phòng Ban
        user_info_grid_layout.addWidget(QLabel("Tên:"), 0, 0)
        self.entry_name_qt = QLineEdit()
        self.entry_name_qt.setFont(self.body_font) # Sử dụng font mặc định
        user_info_grid_layout.addWidget(self.entry_name_qt, 0, 1)

        user_info_grid_layout.addWidget(QLabel("Phòng Ban:"), 0, 2)
        self.entry_department_qt = QLineEdit()
        self.entry_department_qt.setFont(self.body_font)
        user_info_grid_layout.addWidget(self.entry_department_qt, 0, 3) # Phòng ban ở cột 3

        # Dòng 1: Vị Trí Tầng (cột 0, 1) và ô nhập tầng tùy chỉnh (cột 2, 3 - sẽ được quản lý bởi on_floor_change_qt)
        # Đảm bảo label "Nhập vị trí hiện tại" dùng font mặc định
        user_info_grid_layout.addWidget(QLabel("Vị Trí:"), 1, 0) # Đổi tên label
        self.combo_floor_qt = QComboBox()
        self.combo_floor_qt.setFont(self.body_font)
        self.combo_floor_qt.addItems(["Tầng G", "Lầu 1", "Lầu 2", "Khác"])
        self.combo_floor_qt.currentIndexChanged.connect(self.on_floor_change_qt)
        user_info_grid_layout.addWidget(self.combo_floor_qt, 1, 1) # ComboBox ở cột 1

        self.entry_custom_floor_label_qt = QLabel("Vị trí khác:") # Đổi text 
        self.entry_custom_floor_label_qt.setFont(self.h2_font) # Đổi sang font in đậm
        self.entry_custom_floor_qt = QLineEdit()
        self.entry_custom_floor_qt.setFont(self.body_font)
        # Sẽ được thêm/xóa bởi on_floor_change_qt, không thêm vào layout cố định ở đây
        self.on_floor_change_qt() # Initial state

        # Dòng 2: Chức Vụ (cột 0,1) và Checkbox Ghi chú (cột 2)
        user_info_grid_layout.addWidget(QLabel("Chức Vụ:"), 2, 0) # Chức Vụ ở dòng 2, cột 0
        self.entry_position_qt = QLineEdit()
        self.entry_position_qt.setFont(self.body_font)
        user_info_grid_layout.addWidget(self.entry_position_qt, 2, 1) # Ô nhập Chức Vụ ở dòng 2, cột 1 (không kéo dài)

        self.checkbox_show_notes = QCheckBox("Thêm ghi chú")
        self.checkbox_show_notes.setFont(self.body_font)
        self.checkbox_show_notes.toggled.connect(self.toggle_notes_visibility)
        user_info_grid_layout.addWidget(self.checkbox_show_notes, 2, 2, 1, 2) # Checkbox ở dòng 2, cột 2, kéo dài 2 cột còn lại


        # Dòng 3: Ghi chú (ẩn/hiện) - đã được dời xuống
        self.label_notes_qt = QLabel("Ghi chú:")
        self.label_notes_qt.setFont(self.body_font)
        self.text_notes_qt = QTextEdit()
        self.text_notes_qt.setFont(self.body_font)
        self.text_notes_qt.setFixedHeight(60) # Giới hạn chiều cao
        user_info_grid_layout.addWidget(self.label_notes_qt, 3, 0, Qt.AlignTop) # Label Ghi chú ở dòng 3, cột 0
        user_info_grid_layout.addWidget(self.text_notes_qt, 3, 1, 1, 3) # Ô nhập Ghi chú ở dòng 3, cột 1, kéo dài 3 cột

        self.toggle_notes_visibility(False) # Ẩn ghi chú ban đầu

        user_info_grid_layout.setColumnStretch(1, 1) # Cho cột input của Tên và Tầng mở rộng
        user_info_grid_layout.setColumnStretch(3, 1) # Cho cột input của Phòng Ban và Chức Vụ mở rộng

        # --- System Info Display (Card Layout) ---
        # ScrollArea for cards if they overflow
        cards_scroll_area = QScrollArea()
        cards_scroll_area.setWidgetResizable(True)
        cards_scroll_area.setObjectName("CardsScrollArea")
        
        cards_container_widget = QWidget() # Widget to hold the grid of cards
        self.home_cards_layout = QGridLayout(cards_container_widget) # Use QGridLayout for cards
        self.home_cards_layout.setSpacing(15)

        # Create placeholder cards (will be populated in _on_fetch_pc_info_completed)
        self.card_general_info = self._create_info_card("Thông tin Chung")
        self.card_os_info = self._create_info_card("Hệ Điều Hành")
        self.card_cpu_info = self._create_info_card("CPU")
        self.card_ram_info = self._create_info_card("RAM")
        self.card_mainboard_info = self._create_info_card("Mainboard")
        self.card_disks_info = self._create_info_card("Ổ Đĩa") # For multiple disks
        self.card_gpus_info = self._create_info_card("Card Đồ Họa (GPU)") # For multiple GPUs
        self.card_screens_info = self._create_info_card("Màn Hình") # For multiple screens
        # self.card_disk_health_info = self._create_info_card("Tình Trạng Ổ Cứng (S.M.A.R.T)") # Removed as per request
        # self.card_battery_info = self._create_info_card("Thông Tin Pin (Laptop)") # Removed as per request


        self.home_cards_layout.addWidget(self.card_general_info, 0, 0)
        self.home_cards_layout.addWidget(self.card_os_info, 0, 1)
        self.home_cards_layout.addWidget(self.card_cpu_info, 1, 0)
        self.home_cards_layout.addWidget(self.card_ram_info, 1, 1)
        self.home_cards_layout.addWidget(self.card_mainboard_info, 2, 0)
        # self.home_cards_layout.addWidget(self.card_disk_health_info, 2, 1) # Removed
        self.home_cards_layout.addWidget(self.card_disks_info, 2, 1)    # Physical disks moved to (2,1)
        # self.home_cards_layout.addWidget(self.card_battery_info, 3, 1)  # Removed
        self.home_cards_layout.addWidget(self.card_gpus_info, 3, 0, 1, 2) # Span 2 columns for GPUs, moved to row 3
        self.home_cards_layout.addWidget(self.card_screens_info, 4, 0, 1, 2) # Span 2 columns for Screens, moved to row 4

        cards_scroll_area.setWidget(cards_container_widget)
        layout.addWidget(cards_scroll_area, 1) # Add scroll area to the main tab layout

    def _create_info_card(self, title):
        # This function is now used by _create_system_info_tab
        card = QGroupBox(title)
        card.setFont(self.h2_font)
        card.setObjectName("InfoCard")
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignTop)
        # Add a QLabel for content, it will be populated later
        content_label = QLabel("Đang tải...")
        content_label.setFont(self.monospace_font) # Monospace for consistent alignment
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard) # Cho phép copy
        content_label.setWordWrap(True)
        card_layout.addWidget(content_label)
        return card

    def on_floor_change_qt(self):
        is_custom = self.combo_floor_qt.currentText() == "Khác"
        # Lấy layout của group_user_info để thêm/xóa widget
        user_info_grid_layout = self.entry_name_qt.parentWidget().layout() # Cách lấy layout của QGroupBox

        if not is_custom:
            # Xóa widget nếu chúng đang tồn tại trong layout
            if self.entry_custom_floor_label_qt.parentWidget() is not None:
                user_info_grid_layout.removeWidget(self.entry_custom_floor_label_qt)
                self.entry_custom_floor_label_qt.setParent(None)
            if self.entry_custom_floor_qt.parentWidget() is not None:
                user_info_grid_layout.removeWidget(self.entry_custom_floor_qt)
                self.entry_custom_floor_qt.setParent(None)
                self.entry_custom_floor_qt.clear()
        else:
            # Thêm widget vào layout nếu chưa có
            if self.entry_custom_floor_label_qt.parentWidget() is None:
                 user_info_grid_layout.addWidget(self.entry_custom_floor_label_qt, 1, 2) # Dòng 2 (index 1), cột 3 (index 2)
            if self.entry_custom_floor_qt.parentWidget() is None:
                 user_info_grid_layout.addWidget(self.entry_custom_floor_qt, 1, 3) # Dòng 2 (index 1), cột 4 (index 3)
        self.entry_custom_floor_label_qt.setVisible(is_custom) # Vẫn dùng setVisible để đảm bảo trạng thái đúng
        self.entry_custom_floor_qt.setVisible(is_custom)

    def _create_security_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget) # Layout chính của tab là QVBoxLayout

        # --- Content Layout (Actions and Results side-by-side) ---
        content_layout = QHBoxLayout() # Layout ngang cho 2 cột nội dung
        tab_main_layout.addLayout(content_layout) # Thêm content_layout vào tab_main_layout


        # --- Left Column: Search Bar and Action Buttons ---
        left_column_widget = QWidget()
        left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setContentsMargins(0,0,0,0) # Remove margins for tighter fit
        left_column_layout.setSpacing(5) # Spacing between search and scroll area
        
        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        security_actions_widget_container = QWidget() 
        self.security_actions_layout = QVBoxLayout(security_actions_widget_container) 
        self.security_actions_layout.setSpacing(10) 
        self.security_actions_layout.setAlignment(Qt.AlignTop) 

        # Group: Bảo mật & Virus
        group_security = QGroupBox("Bảo mật & Virus")
        group_security.setFont(self.h2_font)
        sec_layout = QVBoxLayout(group_security)
        self._add_utility_button(sec_layout, "Quét Virus Nhanh", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_security, run_windows_defender_scan, "security_defender_quick_scan", needs_wmi=False, task_args=["QuickScan"]))
        self._add_utility_button(sec_layout, "Quét Virus Toàn Bộ", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_security, run_windows_defender_scan, "security_defender_full_scan", needs_wmi=False, task_args=["FullScan"]))
        self._add_utility_button(sec_layout, "Cập Nhật Định Nghĩa Virus", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_security, update_windows_defender_definitions, "security_defender_update", needs_wmi=False))
        self._add_utility_button(sec_layout, "Kiểm Tra Trạng Thái Tường Lửa", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_security, get_firewall_status, "security_firewall_status", needs_wmi=False))
        self._add_utility_button(sec_layout, "Bật Tường Lửa (Tất cả Profile)", self.enable_firewall_qt, object_name="WarningButton") # Example of specific style
        self._add_utility_button(sec_layout, "Tắt Tường Lửa (Tất cả Profile)", self.disable_firewall_qt, object_name="DangerButton")
        self.security_actions_layout.addWidget(group_security)

        # Thêm các group khác cho tab Bảo Mật nếu cần

        self.security_actions_layout.addStretch(1) 
        scroll_area_actions.setWidget(security_actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions) # Add scroll area below search bar
        content_layout.addWidget(left_column_widget, 2) # Tăng tỷ lệ cho cột trái

        # --- Right Column: Utilities Results Display ---
        results_container_widget = QWidget()
        self.utilities_results_main_layout = QVBoxLayout(results_container_widget) # Lưu layout này
        self.utilities_results_main_layout.setContentsMargins(0,0,0,0)

        # QStackedWidget for switching between QTextEdit and QTableWidget
        self.stacked_widget_results_security = QStackedWidget() # Đổi tên
        
        # Page 0: QTextEdit for general results
        results_group = QGroupBox("Kết quả Bảo Mật") # Đổi tên
        results_group.setFont(self.body_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_security_results_qt = QTextEdit() # Đổi tên
        self.text_security_results_qt.setReadOnly(True)
        self.text_security_results_qt.setFont(self.monospace_font)
        self.text_security_results_qt.setWordWrapMode(QTextOption.NoWrap)
        self.text_security_results_qt.setObjectName("SecurityResultTextEdit") # Đổi tên
        results_layout_inner.addWidget(self.text_security_results_qt)
        self._update_display_widget(self.text_security_results_qt, "Kết quả của tác vụ bảo mật sẽ hiển thị ở đây.")
        self.stacked_widget_results_security.addWidget(results_group)

        # Page 1: QTableWidget for table results
        self.table_security_results_qt = QTableWidget() # Đổi tên
        self._setup_results_table(self.table_security_results_qt) # Sử dụng hàm helper
        self.stacked_widget_results_security.addWidget(self.table_security_results_qt)

        self.utilities_results_main_layout.addWidget(self.stacked_widget_results_security, 1)
        content_layout.addWidget(results_container_widget, 3)

    def _create_optimize_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget)
        content_layout = QHBoxLayout()
        tab_main_layout.addLayout(content_layout)

        left_column_widget = QWidget()
        left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setContentsMargins(0,0,0,0)
        left_column_layout.setSpacing(5)
        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        optimize_actions_widget_container = QWidget()
        self.optimize_actions_layout = QVBoxLayout(optimize_actions_widget_container)
        self.optimize_actions_layout.setSpacing(10)
        self.optimize_actions_layout.setAlignment(Qt.AlignTop)

        # Group: Dọn dẹp & Tối ưu
        group_cleanup = QGroupBox("Dọn dẹp & Tối ưu Cơ Bản")
        group_cleanup.setFont(self.h2_font)
        cleanup_layout = QVBoxLayout(group_cleanup)
        self._add_utility_button(cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, clear_temporary_files, "optimize_clear_temp"))
        self._add_utility_button(cleanup_layout, "Mở Resource Monitor", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, open_resource_monitor, "optimize_resmon"))
        self._add_utility_button(cleanup_layout, "Quản Lý Khởi Động Cùng Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, get_startup_programs, "optimize_startup_programs", needs_wmi=True, result_type="table"))
        self.optimize_actions_layout.addWidget(group_cleanup)

        # Group: Sửa lỗi & Cập nhật Hệ thống (một phần chuyển sang Tối ưu)
        group_fix_update = QGroupBox("Sửa lỗi & Cập nhật")
        group_fix_update.setFont(self.h2_font)
        fix_update_layout = QVBoxLayout(group_fix_update)
        self._add_utility_button(fix_update_layout, "Chạy SFC Scan", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, run_sfc_scan, "optimize_sfc_scan"))
        self._add_utility_button(fix_update_layout, "Tạo Điểm Khôi Phục Hệ Thống", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, create_system_restore_point, "optimize_create_restore_point"))
        self._add_utility_button(fix_update_layout, "Cập Nhật Phần Mềm (Winget)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, update_all_winget_packages, "optimize_winget_update"))
        self.optimize_actions_layout.addWidget(group_fix_update)
        
        # Group: Tối ưu Nâng Cao
        group_advanced_optimization = QGroupBox("Tối ưu Nâng Cao")
        group_advanced_optimization.setFont(self.h2_font)
        advanced_opt_layout = QVBoxLayout(group_advanced_optimization)        
        self._add_utility_button(advanced_opt_layout, "Tối ưu Dịch Vụ Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, optimize_windows_services, "optimize_optimize_services"))
        self._add_utility_button(advanced_opt_layout, "Dọn Dẹp Registry (Có Sao Lưu)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, clean_registry_with_backup, "optimize_clean_registry"))
        self.optimize_actions_layout.addWidget(group_advanced_optimization)

        self.optimize_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(optimize_actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions)
        content_layout.addWidget(left_column_widget, 2)

        results_container_widget = QWidget()
        self.optimize_results_main_layout = QVBoxLayout(results_container_widget)
        self.optimize_results_main_layout.setContentsMargins(0,0,0,0)
        self.stacked_widget_results_optimize = QStackedWidget()
        
        results_group = QGroupBox("Kết quả Tối Ưu")
        results_group.setFont(self.body_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_optimize_results_qt = QTextEdit()
        self.text_optimize_results_qt.setReadOnly(True)
        self.text_optimize_results_qt.setFont(self.monospace_font)
        self.text_optimize_results_qt.setWordWrapMode(QTextOption.NoWrap)
        self.text_optimize_results_qt.setObjectName("OptimizeResultTextEdit")
        results_layout_inner.addWidget(self.text_optimize_results_qt)
        self._update_display_widget(self.text_optimize_results_qt, "Kết quả của tác vụ tối ưu sẽ hiển thị ở đây.")
        self.stacked_widget_results_optimize.addWidget(results_group)

        self.table_optimize_results_qt = QTableWidget()
        self._setup_results_table(self.table_optimize_results_qt)
        self.stacked_widget_results_optimize.addWidget(self.table_optimize_results_qt)

        self.optimize_results_main_layout.addWidget(self.stacked_widget_results_optimize, 1)
        content_layout.addWidget(results_container_widget, 3)

    def _create_network_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget)
        content_layout = QHBoxLayout()
        tab_main_layout.addLayout(content_layout)

        left_column_widget = QWidget()
        left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setContentsMargins(0,0,0,0)
        left_column_layout.setSpacing(5)
        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        network_actions_widget_container = QWidget()
        self.network_actions_layout = QVBoxLayout(network_actions_widget_container)
        self.network_actions_layout.setSpacing(10)
        self.network_actions_layout.setAlignment(Qt.AlignTop)

        # Group: Mạng
        group_network = QGroupBox("Công cụ Mạng")
        group_network.setFont(self.h2_font)
        net_layout = QVBoxLayout(group_network)
        self._add_utility_button(net_layout, "Kiểm Tra Kết Nối Wifi", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, get_wifi_connection_info, "network_wifi_info"))
        self._add_utility_button(net_layout, "Xem Cấu Hình Mạng Chi Tiết", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, get_network_configuration_details, "network_config", needs_wmi=True, result_type="table"))
        self._add_utility_button(net_layout, "Ping Google", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, run_ping_test, "network_ping_google", task_args=["google.com", 4]))
        self._add_utility_button(net_layout, "Phân giải IP tên miền", self.run_domain_ip_resolution_qt) # Sẽ cần cập nhật target_stacked_widget
        self._add_utility_button(net_layout, "Kết Nối Mạng Đang Hoạt Động", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, get_active_network_connections, "network_active_connections", result_type="table"))
        self._add_utility_button(net_layout, "Cấu hình DNS", self.run_set_dns_config_qt) # Sẽ cần cập nhật target_stacked_widget
        self._add_utility_button(net_layout, "Xóa Cache DNS", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, flush_dns_cache, "network_flush_dns"))
        self._add_utility_button(net_layout, "Reset Kết Nối Internet", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_network, reset_internet_connection, "network_reset_net"))
        self.network_actions_layout.addWidget(group_network)

        self.network_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(network_actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions)
        content_layout.addWidget(left_column_widget, 2)

        results_container_widget = QWidget()
        self.network_results_main_layout = QVBoxLayout(results_container_widget)
        self.network_results_main_layout.setContentsMargins(0,0,0,0)
        self.stacked_widget_results_network = QStackedWidget()
        
        results_group = QGroupBox("Kết quả Mạng")
        results_group.setFont(self.body_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_network_results_qt = QTextEdit()
        self.text_network_results_qt.setReadOnly(True)
        self.text_network_results_qt.setFont(self.monospace_font)
        self.text_network_results_qt.setWordWrapMode(QTextOption.NoWrap)
        self.text_network_results_qt.setObjectName("NetworkResultTextEdit")
        results_layout_inner.addWidget(self.text_network_results_qt)
        self._update_display_widget(self.text_network_results_qt, "Kết quả của tác vụ mạng sẽ hiển thị ở đây.")
        self.stacked_widget_results_network.addWidget(results_group)

        self.table_network_results_qt = QTableWidget()
        self._setup_results_table(self.table_network_results_qt)
        self.stacked_widget_results_network.addWidget(self.table_network_results_qt)

        self.network_results_main_layout.addWidget(self.stacked_widget_results_network, 1)
        content_layout.addWidget(results_container_widget, 3)

    def _create_utilities_tab(self, parent_tab_widget): # This tab is now for remaining diagnostics
        # This is a placeholder, you'd move relevant buttons from old _create_utilities_tab here
        # For example: Disk Usage, Battery Report, Windows Activation, Event Logs, Software Versions, Temps, Processes, Disk Speed
        # This function is not directly used by the new nav structure but can be a template
        # if you decide to have a "General Utilities" or "Diagnostics" tab.
        # For now, these functions might be integrated into "💻 Hệ Thống" or other specific tabs.
        pass

        content_layout.addWidget(results_container_widget, 3) # Điều chỉnh tỷ lệ cho cột phải

    def _add_utility_button(self, layout, text, on_click_action, object_name=None):
        button = QPushButton(text)
        if object_name:
            button.setObjectName(object_name) # Use provided object_name for specific styling
        else:
            button.setObjectName("UtilityButton") # Default object_name for general utility button styling
        button.setFont(self.body_font)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, btn=button: on_click_action(btn)) # Pass button to action
        layout.addWidget(button)
        return button

    def _create_fixes_tab(self, parent_tab_widget): # This tab is now split into Optimize and others
        # This function is not directly used by the new nav structure.
        tab_main_layout_fixes = QVBoxLayout(parent_tab_widget)

        # --- Content Layout (Actions and Results side-by-side) ---
        content_layout_fixes = QHBoxLayout()
        tab_main_layout_fixes.addLayout(content_layout_fixes)

        # --- Left Column: Search Bar and Action Buttons ---
        left_column_widget_fixes = QWidget()
        left_column_layout_fixes = QVBoxLayout(left_column_widget_fixes)
        left_column_layout_fixes.setContentsMargins(0,0,0,0)
        left_column_layout_fixes.setSpacing(5)
        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        actions_widget_container = QWidget()
        self.fixes_actions_layout = QVBoxLayout(actions_widget_container) # Store as instance member
        self.fixes_actions_layout.setSpacing(10) # Tăng khoảng cách giữa các GroupBox
        self.fixes_actions_layout.setAlignment(Qt.AlignTop)

        # Group 1: Tối ưu & Dọn dẹp Hệ thống
        group_optimize_cleanup = QGroupBox("Tối ưu & Dọn dẹp Hệ thống")
        group_optimize_cleanup.setFont(self.h2_font)
        optimize_cleanup_layout = QVBoxLayout(group_optimize_cleanup)
        self._add_utility_button(optimize_cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, clear_temporary_files, "fix_clear_temp", needs_wmi=False))
        self._add_utility_button(optimize_cleanup_layout, "Mở Resource Monitor", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, open_resource_monitor, "fix_resmon", needs_wmi=False))
        self._add_utility_button(optimize_cleanup_layout, "Quản Lý Khởi Động Cùng Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, get_startup_programs, "fix_startup_programs", needs_wmi=True, result_type="table"))
        self.fixes_actions_layout.addWidget(group_optimize_cleanup)

        # Group 2: Sửa lỗi & Cập nhật Hệ thống
        group_fix_update = QGroupBox("Sửa lỗi & Cập nhật Hệ thống")
        group_fix_update.setFont(self.h2_font)
        fix_update_layout = QVBoxLayout(group_fix_update)
        self._add_utility_button(fix_update_layout, "Reset Kết Nối Internet", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, reset_internet_connection, "fix_reset_net", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Chạy SFC Scan", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, run_sfc_scan, "fix_sfc_scan", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Tạo Điểm Khôi Phục Hệ Thống", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, create_system_restore_point, "fix_create_restore_point", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Cập Nhật Phần Mềm (Winget)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, update_all_winget_packages, "fix_winget_update", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_fix_update)

        # Group 3: Tối ưu Nâng Cao
        group_advanced_optimization = QGroupBox("Tối ưu Nâng Cao")
        group_advanced_optimization.setFont(self.h2_font)
        advanced_opt_layout = QVBoxLayout(group_advanced_optimization)        
        self._add_utility_button(advanced_opt_layout, "Tối ưu Dịch Vụ Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, optimize_windows_services, "fix_optimize_services", needs_wmi=False))
        self._add_utility_button(advanced_opt_layout, "Dọn Dẹp Registry (Có Sao Lưu)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, clean_registry_with_backup, "fix_clean_registry", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_advanced_optimization)

        self.fixes_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(actions_widget_container)
        left_column_layout_fixes.addWidget(scroll_area_actions) # Add scroll area below search bar
        content_layout_fixes.addWidget(left_column_widget_fixes, 2) # Tăng tỷ lệ cho cột trái


        # Right Column: Fixes Results Display
        results_container_widget = QWidget()
        self.fixes_results_main_layout = QVBoxLayout(results_container_widget) # Lưu layout này
        self.fixes_results_main_layout.setContentsMargins(0,0,0,0)

        self.stacked_widget_results_fixes = QStackedWidget()

        # Page 0 for Fixes Tab: QTextEdit
        results_group = QGroupBox("Kết quả Tác vụ Sửa lỗi")
        results_group.setFont(self.h2_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_fixes_results_qt = QTextEdit()
        self.text_fixes_results_qt.setReadOnly(True)
        self.text_fixes_results_qt.setFont(self.monospace_font)
        self.text_fixes_results_qt.setWordWrapMode(QTextOption.NoWrap)
        self.text_fixes_results_qt.setObjectName("FixesResultTextEdit")
        results_layout_inner.addWidget(self.text_fixes_results_qt)
        self._update_display_widget(self.text_fixes_results_qt, html.escape("Chọn một tác vụ để thực hiện."))
        self.stacked_widget_results_fixes.addWidget(results_group)

        # Page 1 for Fixes Tab: QTableWidget
        self.table_fixes_results_qt = QTableWidget()
        self.table_fixes_results_qt.setFont(self.body_font)
        self.table_fixes_results_qt.setAlternatingRowColors(True)
        self.table_fixes_results_qt.setSortingEnabled(True)
        self.table_fixes_results_qt.horizontalHeader().setStretchLastSection(True)
        self.table_fixes_results_qt.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_fixes_results_qt.setObjectName("ResultTableWidget")
        self.stacked_widget_results_fixes.addWidget(self.table_fixes_results_qt)

        self.fixes_results_main_layout.addWidget(self.stacked_widget_results_fixes, 1)
        
        # # Frame cho nút lưu kết quả ở tab Fixes (ĐÃ DI CHUYỂN RA GLOBAL)
        # fixes_buttons_frame = QFrame()
        # fixes_buttons_layout_inner = QHBoxLayout(fixes_buttons_frame) # Layout nội bộ cho các nút
        # fixes_buttons_layout_inner.addStretch(1) # Đẩy nút Lưu sang phải
        # self.button_save_fix_result_qt = QPushButton("Lưu Kết Quả Sửa Lỗi")
        # self._style_save_button(self.button_save_fix_result_qt, lambda: self.save_tab_result_qt(self.stacked_widget_results_fixes, "KetQua_SuaLoi"))
        # fixes_buttons_layout_inner.addWidget(self.button_save_fix_result_qt)
        # self.fixes_results_main_layout.addWidget(fixes_buttons_frame)

        content_layout_fixes.addWidget(results_container_widget, 3) # Điều chỉnh tỷ lệ cho cột phải

    def _perform_global_search(self):
        """Thực hiện tìm kiếm/lọc dựa trên tab hiện tại và nội dung của global_search_input."""
        if not hasattr(self, 'global_search_input'):
            return
        search_term = self.global_search_input.text()
        current_page_widget = self.pages_stack.currentWidget()

        if current_page_widget == self.page_security:
            if hasattr(self, 'security_actions_layout'):
                self._filter_action_buttons(search_term, self.security_actions_layout)
            if hasattr(self, 'stacked_widget_results_security') and self.stacked_widget_results_security.widget(0).findChild(QTextEdit):
                self._perform_text_search(self.stacked_widget_results_security.widget(0).findChild(QTextEdit), search_term)
        elif current_page_widget == self.page_optimize:
            if hasattr(self, 'optimize_actions_layout'):
                self._filter_action_buttons(search_term, self.optimize_actions_layout)
            if hasattr(self, 'stacked_widget_results_optimize') and self.stacked_widget_results_optimize.widget(0).findChild(QTextEdit):
                self._perform_text_search(self.stacked_widget_results_optimize.widget(0).findChild(QTextEdit), search_term)
        elif current_page_widget == self.page_network:
            if hasattr(self, 'network_actions_layout'):
                self._filter_action_buttons(search_term, self.network_actions_layout)
            if hasattr(self, 'stacked_widget_results_network') and self.stacked_widget_results_network.widget(0).findChild(QTextEdit):
                self._perform_text_search(self.stacked_widget_results_network.widget(0).findChild(QTextEdit), search_term)
        # Add search for self.page_system_info if it contains searchable text/tables
        # elif current_page_widget == self.page_system_info:
            # Example: if system_info tab has a QTextEdit for detailed logs or similar
            # text_edit_system = self.page_system_info.findChild(QTextEdit, "SystemInfoTextDisplay")
            # if text_edit_system:
            #     self._perform_text_search(text_edit_system, search_term)

        # Add other pages if they need search functionality


    def _create_report_settings_tab(self, parent_tab_widget): # Was _create_about_tab
        layout = QVBoxLayout(parent_tab_widget)
        layout.setContentsMargins(20, 20, 20, 20) # Thêm padding cho dễ nhìn
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)
        # Styling for button_save_active_tab_result will be handled in _apply_styles

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_content_widget)
        scroll_layout.setAlignment(Qt.AlignTop)

        # --- Nút Xuất Báo Cáo PC ---
        self.button_export_pc_report_tab = QPushButton("Xuất Báo Cáo Thông Tin PC")
        self.button_export_pc_report_tab.setFont(self.body_font)
        self.button_export_pc_report_tab.setCursor(Qt.PointingHandCursor)
        self.button_export_pc_report_tab.clicked.connect(self.on_export_info_qt)
        self.button_export_pc_report_tab.setObjectName("ExportReportButton") # For styling if needed
        scroll_layout.addWidget(self.button_export_pc_report_tab)

        # --- Tiêu đề ứng dụng ---
        title_label = QLabel("Công Cụ Hỗ Trợ PC")
        title_label.setFont(self.h1_font) # Use H1 font

        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse) # Cho phép copy
        title_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title_label)

        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Phiên bản:", "V.2.1 (Concept UI)"))
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Người sáng lập:", "HPC"))
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Liên hệ:", "support@example.com"))
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Giấy phép:", "Phần mềm nội bộ"))

        readme_text = """**README:**

Đây là công cụ hỗ trợ thu thập thông tin cấu hình máy tính và thực hiện một số tác vụ tiện ích, sửa lỗi cơ bản trên hệ điều hành Windows.

**Các chức năng chính:**
- Thu thập thông tin chi tiết về phần cứng, phần mềm.
- Cung cấp các tiện ích quét virus, kiểm tra ổ đĩa, pin, kích hoạt Windows.
- Hỗ trợ các tác vụ sửa lỗi hệ thống như dọn dẹp file tạm, reset kết nối mạng, chạy SFC scan."""
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Mô tả:", readme_text, is_html=True))
        scroll_area.setWidget(scroll_content_widget)
        layout.addWidget(scroll_area)

    def _create_info_section_qt(self, parent, title_text, content_text, is_html=False):
        section_group = QGroupBox(title_text)
        section_group.setFont(self.h2_font)
        section_layout = QVBoxLayout(section_group)

        content_label = QLabel()
        content_label.setFont(self.body_font)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard) # Cho phép copy
        if is_html:
            # Xử lý markdown đơn giản (**bold**) thành HTML
            html_content = html.escape(content_text).replace("**", "<b>").replace("</b>", "</b>", 1) # Chỉ replace cặp đầu tiên
            # Để xử lý nhiều cặp bold, cần regex hoặc logic phức tạp hơn, ví dụ:
            import re
            html_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html.escape(content_text))
            html_content = html_content.replace("\n", "<br>")
            content_label.setTextFormat(Qt.RichText) # Cho phép hiển thị HTML
            content_label.setText(html_content)
        else:
            content_label.setText(content_text)

        section_layout.addWidget(content_label)
        return section_group

    def _apply_styles(self):
        # Sử dụng các hằng số màu và font đã định nghĩa
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {WINDOW_BG};
                font-family: "{DEFAULT_FONT_FAMILY}"; /* Default font for the whole window */
                font-size: {BODY_FONT_SIZE}pt; /* Base font size for the application */
            }}
            QFrame#TopHeaderBar {{
                background-color: {FRAME_BG}; /* Or a specific header color */
                border-bottom: 1px solid {BORDER_COLOR_LIGHT};
                padding: 0px; /* Remove padding if QHBoxLayout handles it */
            }}
            QWidget {{ /* Apply default font to all child widgets */
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {BODY_FONT_SIZE}pt;
                color: {TEXT_COLOR_PRIMARY};
            }}
            QGroupBox {{
                background-color: {GROUPBOX_BG}; /* Background for groupbox */
                border: 1px solid {BORDER_COLOR_LIGHT};
                border-radius: 8px; /* Increased border radius */
                margin-top: 20px; /* Increased margin for title */
                padding: 10px; /* Padding inside groupbox */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 8px; /* Increased title padding */
                margin-left: 10px; /* Indent title slightly */
                background-color: {WINDOW_BG}; /* Title background same as window */
                border-radius: 4px;
                color: {ACCENT_COLOR}; /* Color for groupbox title */
                /* font-family, font-size, font-weight for GroupBox titles are set by self.h2_font in Python */
                /* e.g., group_user_info.setFont(self.h2_font) */
            }}
            QLabel {{
                padding: 3px;
                background-color: transparent; /* Ensure labels don't have own background unless intended */
            }}
            QPushButton {{
                /* Default button style - will be overridden by specific objectNames or classes */
                background-color: {BUTTON_SECONDARY_BG};
                color: {TEXT_COLOR_PRIMARY};
                border: 1px solid {BORDER_COLOR_DARK};
                border-radius: 6px; /* Increased border radius */
                padding: 8px 15px; /* Increased padding */
                min-height: 20px; /* Minimum height */
                /* font-family and font-size are inherited from QWidget or set by self.default_font */
            }}
            QPushButton:hover {{
                background-color: {BUTTON_SECONDARY_HOVER};
                border-color: {ACCENT_COLOR_HOVER}; /* Highlight border on hover */
            }}
            QPushButton:pressed {{
                background-color: {BUTTON_SECONDARY_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: #E0E0E0; /* Lighter grey for disabled */
                color: #A0A0A0; /* Lighter text for disabled */
                border-color: #D0D0D0;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER_COLOR};
                border-radius: 5px; /* Moderate border radius */
                padding: 6px; /* Increased padding */
                color: {TEXT_COLOR_PRIMARY};
                /* font-family and font-size are inherited or set by specific QFont in code */
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: {ACCENT_COLOR}; /* Highlight border on focus */
            }}
            QComboBox::drop-down {{
                border: none;
                /* If you want a custom arrow, uncomment and provide the image */
                /* subcontrol-origin: padding; */
                /* subcontrol-position: top right; */
                /* width: 15px; */
                /* border-left-width: 1px; */
                /* border-left-color: darkgray; */
                /* border-left-style: solid; */
                /* border-top-right-radius: 3px; */
                /* border-bottom-right-radius: 3px; */
            }}
            /*
            QComboBox::down-arrow {{
                image: url({resource_path(os.path.join("assets", "icons", "arrow_down.png"))});
                width: 12px;
                height: 12px;
                margin-right: 2px;
            }}
            */
            QTextEdit {{ /* General style for QTextEdit, e.g., notes_qt. Specific ones below */
                /* Font will be set by self.default_font or self.monospace_font in Python */
            }}
            QTabWidget::pane {{ /* The tab widget frame */
                border: 1px solid {BORDER_COLOR_LIGHT};
                border-top: none; /* Remove top border of pane as tab has it */
                background: {FRAME_BG};
                border-bottom-left-radius: 8px; /* Rounded corners for pane */
                border-bottom-right-radius: 8px;
            }}
            QTabBar::tab {{
                background: {TAB_BG_INACTIVE};
                color: {TAB_TEXT_INACTIVE};
                border: 1px solid {BORDER_COLOR_LIGHT};
                border-bottom: none; /* Crucial: tab has no bottom border when inactive */
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 15px; /* Adjusted padding for tabs */
                margin-right: 2px; /* Spacing between tabs */
                /* font is set by self.notebook.setFont(self.bold_font) */
            }}
            QTabBar::tab:selected {{
                background: {TAB_BG_ACTIVE}; /* Active tab background same as pane */
                color: {TAB_TEXT_ACTIVE};
                border-color: {BORDER_COLOR_LIGHT};
                border-bottom: 1px solid {TAB_BG_ACTIVE}; /* "Erase" tab bottom border with pane color */
            }}
            QListWidget#NavList {{
                background-color: {WINDOW_BG}; /* Match window background or a slightly different shade */
                border: 1px solid {BORDER_COLOR_LIGHT};
                padding: 5px;
                outline: 0; /* Remove focus outline if not desired */
            }}
            QListWidget#NavList::item {{
                padding: 10px 8px; /* Padding for each item */
                border-radius: 4px; /* Rounded corners for items */
            }}
            QListWidget#NavList::item:selected {{
                background-color: {PRIMARY_COLOR}; /* Primary color for selected item */
                color: white; /* White text for selected item */
            }}
            QTabBar::tab:!selected:hover {{
                background: {ACCENT_COLOR_HOVER}; /* Use accent color for hover on inactive tabs */
                color: white;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent; /* Scroll area background should be transparent */
            }}
            QSplitter::handle {{
                background-color: {BORDER_COLOR_LIGHT}; /* Color for the splitter handle */
            }}
            QSplitter::handle:hover {{ background-color: {BORDER_COLOR_DARK}; }}
            QScrollBar:vertical {{
                border: 1px solid {BORDER_COLOR_LIGHT};
                background: {WINDOW_BG};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR_DARK};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px; /* Hide arrows if not needed */
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            /* Styles for result display QTextEdit and QTableWidget widgets */
            QTextEdit#ResultTextEdit, QTextEdit#SecurityResultTextEdit, QTextEdit#OptimizeResultTextEdit, QTextEdit#NetworkResultTextEdit, QTextEdit#FixesResultTextEdit {{
                 font-family: "{MONOSPACE_FONT_FAMILY}";
                 font-size: {MONOSPACE_FONT_SIZE}pt;
                 background-color: #FAFAFA; /* Slightly different background for readability */
                 border: 1px solid {BORDER_COLOR_LIGHT};
            }}
            QTableWidget#ResultTableWidget {{
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {BODY_FONT_SIZE-1}pt; /* Slightly smaller for table data */
                alternate-background-color: #F5F5F5; /* Light grey for alternate rows */
                gridline-color: {BORDER_COLOR_LIGHT};
                border: 1px solid {BORDER_COLOR_LIGHT};
            }}
            QTableWidget#ResultTableWidget::item:hover {{
                background-color: {ACCENT_COLOR_HOVER};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {BUTTON_SECONDARY_BG};
                padding: 4px;
                border: 1px solid {BORDER_COLOR_LIGHT};
                font-weight: bold; /* Đã có, giữ lại */
            }}
            /* Styling for QMessageBox */
            QMessageBox {{
                background-color: {WINDOW_BG};
                /* dialogTitleBarButtons-icon-size: 0px; */ /* Hide title bar buttons if desired, tricky */
            }}
            QMessageBox QLabel {{ /* Message text */
                color: {TEXT_COLOR_PRIMARY};
                font-size: {BODY_FONT_SIZE}pt;
                background-color: transparent;
            }}
            QMessageBox QPushButton {{ /* Buttons in QMessageBox */
                background-color: {BUTTON_SECONDARY_BG};
                color: {BUTTON_SECONDARY_TEXT};
                border: 1px solid {BORDER_COLOR_DARK};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 70px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {BUTTON_SECONDARY_HOVER};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {BUTTON_SECONDARY_PRESSED};
            }}
            /* Styling for SetDnsDialog */
            QDialog#SetDnsDialog {{
                background-color: {WINDOW_BG};
            }}
            QDialog#SetDnsDialog QLabel {{
                color: {TEXT_COLOR_PRIMARY};
                background-color: transparent;
            }}
            QDialog#SetDnsDialog QLineEdit {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
                color: {TEXT_COLOR_PRIMARY};
            }}
            QDialog#SetDnsDialog QLineEdit:focus {{
                border-color: {ACCENT_COLOR};
            }}
            QDialog#SetDnsDialog QPushButton {{ /* Buttons inside SetDnsDialog (from QDialogButtonBox) */
                background-color: {BUTTON_SECONDARY_BG};
                color: {BUTTON_SECONDARY_TEXT};
                border: 1px solid {BORDER_COLOR_DARK};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 70px;
            }}
            QDialog#SetDnsDialog QPushButton:hover {{
                background-color: {BUTTON_SECONDARY_HOVER};
            }}
            QDialog#SetDnsDialog QPushButton:pressed {{
                background-color: {BUTTON_SECONDARY_PRESSED};
            }}
            /* Style the OK button in SetDnsDialog as a primary button */
            QDialog#SetDnsDialog QPushButton[text="OK"], QDialog#SetDnsDialog QPushButton[text="&OK"] {{
                background-color: {BUTTON_PRIMARY_BG};
                color: white;
            }}
            QDialog#SetDnsDialog QPushButton[text="OK"]:hover, QDialog#SetDnsDialog QPushButton[text="&OK"]:hover {{
                background-color: {BUTTON_PRIMARY_HOVER};
            }}
            QDialog#SetDnsDialog QPushButton[text="OK"]:pressed, QDialog#SetDnsDialog QPushButton[text="&OK"]:pressed {{
                font-weight: bold;
            }}
            QPushButton#NavToggleHeaderButton {{
                background-color: transparent;
                border: none;
                padding: 5px; /* Adjust as needed */
            }}
            QPushButton#NavToggleHeaderButton:hover {{
                background-color: {BUTTON_SECONDARY_HOVER}; /* Light hover effect */
            }}
            QLabel#AppTitleLabel {{
                /* Style for app title if needed, e.g., color, padding */
            }}
        """)
        # Specific button styles (override general QPushButton style)
        self.button_exit.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_DANGER_BG};
                color: white;
                border: none;
            }}
            QPushButton:hover {{ background-color: {BUTTON_DANGER_HOVER}; }}
            QPushButton:pressed {{ background-color: {BUTTON_DANGER_BG}; }}
        """)
        # self.button_export_csv.setStyleSheet(f"""
        #     QPushButton {{
        #         background-color: {BUTTON_EXPORT_BG};
        #         color: white;
        #         border: none;
        #     }}
        #     QPushButton:hover {{ background-color: {BUTTON_EXPORT_HOVER}; }}
        #     QPushButton:pressed {{ background-color: {BUTTON_EXPORT_PRESSED}; }}
        # """)

        # Style for "Refresh" button on Home tab
        if hasattr(self, 'button_refresh_dashboard_qt'):
            self.button_refresh_dashboard_qt.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BUTTON_PRIMARY_BG};
                    color: white;
                    border: none;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {BUTTON_PRIMARY_HOVER}; }}
                QPushButton:pressed {{ background-color: {BUTTON_PRIMARY_PRESSED}; }}
            """)
        # Style for "Save Result" buttons
        common_save_button_style = f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
            }}
            QPushButton:hover {{ background-color: {ACCENT_COLOR_HOVER}; }}
            QPushButton:pressed {{ background-color: {ACCENT_COLOR_PRESSED}; }}
            QPushButton:disabled {{
                background-color: {BORDER_COLOR_DARK}; /* Use a color from the new palette */
                color: {TEXT_COLOR_SECONDARY}; /* Use a color from the new palette */
                border: none;
            }}
        """
        #if hasattr(self, 'button_save_utility_result_qt'):
        #   self.button_save_utility_result_qt.setStyleSheet(common_save_button_style)
        #if hasattr(self, 'button_save_fix_result_qt'):
        #    self.button_save_fix_result_qt.setStyleSheet(common_save_button_style)
        
        if hasattr(self, 'button_save_active_tab_result'):
            self.button_save_active_tab_result.setStyleSheet(common_save_button_style)

        # Style for InfoCards on Home tab
        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#InfoCard {{ /* Loại bỏ viền cho các card thông tin */
                background-color: {GROUPBOX_BG}; /* Giữ lại màu nền */
                border: 5px; /* Loại bỏ viền */
                border-radius: 8px; /* Giữ lại bo góc cho nền */
                margin-top: 10px; /* Giảm margin-top so với QGroupBox chung */
                padding: 5px 5px 8px 5px;    /* Điều chỉnh padding (top, right, bottom, left) */
            }}
            QGroupBox#ResultsDisplayGroup {{ /* Đã có từ yêu cầu trước, đảm bảo nó không bị ảnh hưởng */
                border: 5px;
                margin-top: 5px;
                padding: 0px;
            }}
            QProgressBar {{
                border: 1px solid {BORDER_COLOR_DARK};
                border-radius: 5px;
                text-align: center; /* Center the percentage text */
                background-color: {INPUT_BG}; /* Background of the unfilled part */
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_COLOR}; /* Color of the filled part */
                border-radius: 4px; /* Slightly smaller radius for the chunk */
                /* width: 10px; */ /* Optional: if you want a segmented look */
            }}
        """)
        self._update_status_bar("Ứng dụng sẵn sàng.", "info") # Set initial status

    def _update_status_bar(self, message, status_type="info"):
        """Cập nhật nội dung và màu sắc của thanh trạng thái."""
        parent_for_toast = self # Mặc định là cửa sổ chính (QMainWindow)
        target_parent_is_visible = self.isVisible() # Kiểm tra cửa sổ chính có hiển thị không

        current_page_widget = self.pages_stack.currentWidget()
        if current_page_widget == self.page_security and hasattr(self, 'stacked_widget_results_security'):
            parent_for_toast = self.stacked_widget_results_security 
            target_parent_is_visible = parent_for_toast.isVisible() and self.isVisible()
        elif current_page_widget == self.page_optimize and hasattr(self, 'stacked_widget_results_optimize'):
            parent_for_toast = self.stacked_widget_results_optimize
            target_parent_is_visible = parent_for_toast.isVisible() and self.isVisible()
        elif current_page_widget == self.page_network and hasattr(self, 'stacked_widget_results_network'):
            parent_for_toast = self.stacked_widget_results_network
            target_parent_is_visible = parent_for_toast.isVisible() and self.isVisible()
        elif current_page_widget == self.page_system_info: # Example for system info tab
            parent_for_toast = self.page_system_info.findChild(QScrollArea) or self.page_system_info # Find a suitable child or use the tab itself
            target_parent_is_visible = parent_for_toast.isVisible() and self.isVisible()

        # if target_parent_is_visible: # Chỉ hiển thị toast nếu parent dự kiến của nó đang hiển thị
            # self.toast_notifier.show_toast(message, parent_widget=parent_for_toast, toast_type=status_type)


    def _update_display_widget(self, text_widget, content, is_error=False):
        # content is now assumed to be an HTML string, or plain text that needs escaping by the caller.
        # For plain text messages passed directly (e.g. "Đang tải..."), they should be escaped by the caller.
        # For content generated by _format_task_result_for_display_generic or _populate_card, it's already HTML.
        # For content generated by _format_task_result_for_display_generic or _populate_card, it's already HTML.
        text_widget.clear()

        final_html_content = content # Assume content is already HTML or properly escaped plain text formatted as HTML

        # Determine text color based on is_error flag or keywords in the content.
        # The is_error flag is the most reliable way to indicate an error.
        text_color_to_use = DEFAULT_TEXT_COLOR_HTML # Access module-level constant
        if is_error:
            text_color_to_use = ERROR_TEXT_COLOR_HTML # Access module-level constant
        # Removed the secondary keyword check for error color; rely on is_error flag.
        # The _on_task_error method correctly sets is_error=True.


        if isinstance(text_widget, QLabel):
            text_widget.setTextFormat(Qt.RichText)
            colored_html_content = f"<font color='{text_color_to_use}'>{final_html_content}</font>"
            text_widget.setText(colored_html_content)
        elif isinstance(text_widget, QTextEdit):
            text_widget.setHtml(f"<font color='{text_color_to_use}'><pre style='color:{text_color_to_use}; white-space: pre-wrap; word-wrap: break-word;'>{final_html_content}</pre></font>")
        else:
            logging.warning(f"Unsupported widget type for _update_display_widget: {type(text_widget)}")
            try: text_widget.setText(content) # Try plain text as a fallback
            except AttributeError: pass

    def _clear_text_highlights(self, text_edit_widget):
        """Clears background highlights from a QTextEdit."""
        cursor = QTextCursor(text_edit_widget.document())
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        default_format.setBackground(Qt.transparent) # Set background to transparent
        cursor.mergeCharFormat(default_format)
        text_edit_widget.setTextCursor(QTextCursor(text_edit_widget.document())) # Reset cursor position

    def _perform_text_search(self, text_edit_widget, search_term):
        """Performs text search in a QTextEdit and highlights occurrences."""
        self._clear_text_highlights(text_edit_widget) # Clear previous highlights

        if not search_term:
            # If search term is empty, ensure the original content's formatting (like bolding) is restored
            # by re-calling _update_display_widget if necessary, or ensure _clear_text_highlights
            # doesn't remove HTML formatting.
            # The current _update_display_widget sets HTML, so clearing highlights and doing nothing
            # else if search_term is empty should be fine as the HTML structure remains.
            return

        doc = text_edit_widget.document()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(HIGHLIGHT_COLOR)

        cursor = QTextCursor(doc)
        first_match_cursor = None # To scroll to the first match

        while True:
            # Find next occurrence
            # QTextDocument.FindCaseSensitively for case-sensitive
            cursor = doc.find(search_term, cursor) # Default is case-insensitive

            if cursor.isNull():
                break # No more occurrences

            if first_match_cursor is None:
                first_match_cursor = QTextCursor(cursor) # Copy cursor state for scrolling

            # Apply highlight
            cursor.mergeCharFormat(highlight_format)

        if first_match_cursor:
            text_edit_widget.setTextCursor(first_match_cursor) # Scroll to the first match
            text_edit_widget.ensureCursorVisible()

    def _filter_action_buttons(self, search_term, actions_container_layout):
        """Filters QPushButtons within QGroupBoxes in a given layout."""
        search_term_lower = search_term.lower()
        for i in range(actions_container_layout.count()):
            widget = actions_container_layout.itemAt(i).widget()
            if isinstance(widget, QGroupBox):
                group_box = widget
                group_should_be_visible = False
                buttons = group_box.findChildren(QPushButton)
                for button in buttons:
                    button_visible = search_term_lower in button.text().lower()
                    button.setVisible(button_visible)
                    if button_visible:
                        group_should_be_visible = True
                group_box.setVisible(group_should_be_visible) # Chỉ ẩn group nếu không có button nào khớp

    def fetch_pc_info_threaded(self):
        # Update placeholder text in cards
        current_page = self.pages_stack.currentWidget()
        if current_page == self.page_dashboard:
            self.label_cpu_name.setText("CPU: Đang tải...")
            self.progress_cpu.setValue(0)
            self.label_ram_info.setText("RAM: Đang tải...")
            self.progress_ram.setValue(0)
            self.label_ssd_info.setText("SSD/HDD: Đang tải...")
            self.progress_ssd.setValue(0)
            self.label_gpu_info.setText("GPU: Đang tải...")
            self.progress_gpu.setValue(0)
            self.label_system_status.setText("Đang kiểm tra trạng thái...")
        elif current_page == self.page_system_info:
             # Update placeholder text in cards on System Info tab
            card_widgets = [
                self.card_general_info, self.card_os_info, self.card_cpu_info,
                self.card_ram_info, self.card_mainboard_info, self.card_disks_info,
                self.card_gpus_info, self.card_screens_info
            ]
            for card in card_widgets:
                content_label = card.findChild(QLabel)
                if content_label:
                    self._update_display_widget(content_label, html.escape("Đang tải..."))

        # Pass the refresh button to the thread
        thread = WorkerThread(get_detailed_system_information, "fetch_pc_info", needs_wmi=False,
                                button_to_manage=self.button_refresh_dashboard_qt,
                                original_button_text=self.button_refresh_dashboard_qt.text())
        thread.task_completed.connect(self._on_fetch_pc_info_completed)
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        thread.start()

    def _populate_card(self, card_groupbox, data_dict, keys_map):
        # This function is now primarily for the System Info tab
        content_label = card_groupbox.findChild(QLabel)
        if not content_label: return

        lines = []
        if isinstance(data_dict, dict):
            for data_key, display_name in keys_map:
                value = data_dict.get(data_key, NOT_AVAILABLE)
                lines.append(f"<b>{display_name}:</b> {html.escape(str(value))}")
        elif isinstance(data_dict, list): # For lists of dicts (e.g., disks, gpus)
            for i, item_dict in enumerate(data_dict):
                if isinstance(item_dict, dict):
                    if "Lỗi" in item_dict:
                        lines.append(f"<i>{card_groupbox.title()} {i+1}: {item_dict['Lỗi']}</i>")
                        continue
                    lines.append(f"<b>{card_groupbox.title()} {i+1}:</b>")
                    for data_key, display_name in keys_map: # keys_map should be for items in the list
                        value = item_dict.get(data_key, NOT_AVAILABLE)
                        lines.append(f"  <b>{display_name}:</b> {html.escape(str(value))}")
                    lines.append("") # Spacer
        else: # Single value or error string
            lines.append(html.escape(str(data_dict)))
            
        self._update_display_widget(content_label, "<br>".join(lines) if lines else "Không có thông tin.")

    def _on_fetch_pc_info_completed(self, task_name, data):
        if task_name == "fetch_pc_info":
            self.pc_info_dict = data
            sys_info_dict = self.pc_info_dict.get("SystemInformation", {})
            pc_data = sys_info_dict.get("PC", {})
            screen_data = sys_info_dict.get("Màn hình", [])

            # --- Update Dashboard Tab ---
            if hasattr(self, 'label_cpu_name'): # Check if dashboard elements exist
                # CPU
                cpu_model = pc_data.get("CPU", {}).get("Kiểu máy", NOT_AVAILABLE)
                self.label_cpu_name.setText(f"CPU: {cpu_model}")
                # Actual CPU usage % is hard to get simply, using placeholder
                self.progress_cpu.setValue(pc_data.get("CPU", {}).get("Tải CPU (%)", 50)) # Placeholder if not available

                # RAM
                ram_total_str = pc_data.get("Bộ nhớ RAM", "0 GB")
                ram_usage_percent = pc_data.get("RAM", {}).get("Phần trăm đã sử dụng", 60) # Placeholder
                self.label_ram_info.setText(f"RAM: {ram_total_str} ({ram_usage_percent}%)")
                self.progress_ram.setValue(ram_usage_percent)

                # SSD/Disk (Example: first physical disk, or C: partition if available)
                # This part needs more robust logic to find C: or primary OS disk and its usage
                disks_info_list = pc_data.get("Ổ đĩa", [])
                disk_partitions_usage = self.pc_info_dict.get("SystemCheckUtilities", {}).get("DiskPartitionsUsage", [])
                
                os_disk_info_str = "SSD/HDD: " + NOT_AVAILABLE
                os_disk_usage_percent = 0

                if disk_partitions_usage and isinstance(disk_partitions_usage, list):
                    for part in disk_partitions_usage:
                        if part.get("Tên ổ đĩa") == "C:":
                            os_disk_info_str = f"Ổ C: {part.get('Tổng dung lượng (GB)', '')}GB ({part.get('Loại File System', '')})"
                            try:
                                used_gb = float(part.get('Đã dùng (GB)', 0))
                                total_gb = float(part.get('Tổng dung lượng (GB)', 1))
                                if total_gb > 0:
                                    os_disk_usage_percent = int((used_gb / total_gb) * 100)
                            except ValueError:
                                pass
                            break 
                elif disks_info_list: # Fallback to first physical disk if C: not found
                    first_disk = disks_info_list[0]
                    os_disk_info_str = f"SSD/HDD: {first_disk.get('Kiểu máy', NOT_AVAILABLE)} ({first_disk.get('Dung lượng (GB)', 'N/A')}GB)"
                    os_disk_usage_percent = 70 # Placeholder
                
                self.label_ssd_info.setText(os_disk_info_str)
                self.progress_ssd.setValue(os_disk_usage_percent)

                # GPU
                gpus = pc_data.get("Card đồ họa (GPU)", [])
                if gpus and isinstance(gpus, list) and isinstance(gpus[0], dict):
                    first_gpu = gpus[0]
                    gpu_name = first_gpu.get("Tên", NOT_AVAILABLE)
                    self.label_gpu_info.setText(f"GPU: {gpu_name}")
                    self.progress_gpu.setValue(first_gpu.get("Tải GPU (%)", 30)) # Placeholder
                else:
                    self.label_gpu_info.setText(f"GPU: {NOT_AVAILABLE}")
                    self.progress_gpu.setValue(0)

                # System Status - Cập nhật sau cùng để không làm chậm các progress bar
                def update_dashboard_status():
                    has_errors_or_warnings = "Lỗi" in str(self.pc_info_dict) or "Error" in str(self.pc_info_dict) or "Cảnh báo" in str(self.pc_info_dict)
                    warning_count = 0
                    if pc_data.get("Trạng thái kích hoạt Windows") != "Đã kích hoạt": warning_count +=1
                    # Thêm các kiểm tra cảnh báo khác ở đây nếu cần

                    if warning_count > 0:
                        self.label_system_status.setText(f"<font color='{ACCENT_COLOR}'>⚠️ {warning_count} cảnh báo cần xử lý</font>")
                    elif has_errors_or_warnings and warning_count == 0:
                         self.label_system_status.setText(f"<font color='{BUTTON_DANGER_BG}'>❌ Có lỗi xảy ra khi lấy thông tin</font>")
                    else:
                        self.label_system_status.setText(f"<font color='{SECONDARY_COLOR}'>🟢 Hệ thống hoạt động tốt</font>")
                QTimer.singleShot(0, update_dashboard_status)

            # --- Update System Info Tab (Cards) ---
            if hasattr(self, 'card_general_info'): # Check if system info tab elements exist
                # Sử dụng QTimer.singleShot để cập nhật từng card một cách trì hoãn
                QTimer.singleShot(0, lambda d=pc_data: self._populate_card(self.card_general_info, d, [("Tên máy tính", "Tên PC"), ("Loại máy", "Loại Máy"), ("Địa chỉ IP", "IP"), ("Địa chỉ MAC", "MAC")]))
                QTimer.singleShot(0, lambda d=pc_data: self._populate_card(self.card_os_info, d, [("Hệ điều hành", "HĐH"), ("Phiên bản Windows", "Phiên Bản"), ("Trạng thái kích hoạt Windows", "Kích hoạt")]))
                QTimer.singleShot(0, lambda d=pc_data.get("CPU", {}): self._populate_card(self.card_cpu_info, d, [("Kiểu máy", "Model"), ("Số lõi", "Lõi"), ("Số luồng", "Luồng"), ("Tốc độ cơ bản", "Tốc độ")]))
                
                def update_ram_card_deferred():
                    ram_data_for_card = {"Tổng RAM": pc_data.get("Bộ nhớ RAM", NOT_AVAILABLE)}
                    if "RAM" in pc_data and "Chi tiết các thanh RAM" in pc_data["RAM"]: # Giả sử có key này
                        ram_data_for_card["Chi tiết"] = pc_data["RAM"]["Chi tiết các thanh RAM"]
                    self._populate_card(self.card_ram_info, ram_data_for_card, [("Tổng RAM", "Tổng RAM"), ("Chi tiết", "Chi tiết")])
                QTimer.singleShot(0, update_ram_card_deferred)

                QTimer.singleShot(0, lambda d=pc_data.get("Mainboard", {}): self._populate_card(self.card_mainboard_info, d, [("Nhà sản xuất", "NSX"), ("Kiểu máy", "Model"), ("Số Sê-ri", "Serial")]))
                
                disk_keys_map = [("Kiểu máy", "Model"), ("Dung lượng (GB)", "Size"), ("Giao tiếp", "Interface"), ("Loại phương tiện", "Loại"), ("Số Sê-ri", "Serial")]
                QTimer.singleShot(0, lambda d=pc_data.get("Ổ đĩa", [{"Thông tin": NOT_FOUND}]): self._populate_card(self.card_disks_info, d, disk_keys_map))

                gpu_keys_map = [("Tên", "Tên"), ("Nhà sản xuất", "NSX"), ("Tổng bộ nhớ (MB)", "VRAM"), ("Độ phân giải hiện tại", "Đ.P.Giải"), ("Phiên bản Driver", "Driver Ver"), ("Ngày Driver", "Ngày Driver")]
                QTimer.singleShot(0, lambda d=pc_data.get("Card đồ họa (GPU)", [{"Thông tin": NOT_FOUND}]): self._populate_card(self.card_gpus_info, d, gpu_keys_map))

                screen_keys_map = [("Tên", "Tên"), ("Độ phân giải (pixels)", "Đ.P.Giải (px)"), ("Tỷ lệ khung hình", "Tỷ lệ"), ("Kích thước (đường chéo)", "K.Thước"), ("Trạng thái", "Tr.Thái")]
                QTimer.singleShot(0, lambda d=screen_data: self._populate_card(self.card_screens_info, d, screen_keys_map))
            
            # Kích hoạt nút "Xuất Báo Cáo PC" nếu đang ở tab Báo cáo & Cài đặt
            if self.pages_stack.currentWidget() == self.page_report_settings:
                self.button_save_active_tab_result.setEnabled(True)
            elif self.pages_stack.currentWidget() == self.page_dashboard: # Kích hoạt nút làm mới dashboard
                self.button_refresh_dashboard_qt.setEnabled(True)
        
    def _on_task_error(self, task_name, error_message):
        logging.error(f"Error in task '{task_name}': {error_message}")
        is_fetch_pc_info = task_name == "fetch_pc_info"
        is_utility_task = task_name.startswith("utility_")
        is_fix_task = task_name.startswith("fix_")

        if is_fetch_pc_info:
            self.pc_info_dict = None
            error_text_html = html.escape(f"Lỗi: {error_message}").replace("\n", "<br>")
            if hasattr(self, 'label_cpu_name'): # Dashboard elements
                self.label_cpu_name.setText("CPU: Lỗi")
                self.progress_cpu.setValue(0)
                # ... (tương tự cho RAM, SSD, GPU)
                self.label_system_status.setText(f"<font color='{BUTTON_DANGER_BG}'>❌ Lỗi khi tải dữ liệu</font>")
            if hasattr(self, 'card_general_info'): # System Info tab elements
                card_widgets = [
                    self.card_general_info, self.card_os_info, self.card_cpu_info, 
                    self.card_ram_info, self.card_mainboard_info, self.card_disks_info, 
                    self.card_gpus_info, self.card_screens_info
                ]
                for card in card_widgets:
                    content_label = card.findChild(QLabel)
                    if content_label:
                        self._update_display_widget(content_label, error_text_html, is_error=True)
            self._update_status_bar(f"Lỗi lấy thông tin PC: {error_message[:100]}...", "error") # Thêm dòng này
            if self.pages_stack.currentWidget() == self.page_report_settings:
                self.button_save_active_tab_result.setEnabled(False)
        elif is_utility_task or is_fix_task: # Gộp logic lỗi cho các tab tiện ích/fix
            target_stacked_widget = None
            if task_name.startswith("security_") and hasattr(self, 'stacked_widget_results_security'):
                target_stacked_widget = self.stacked_widget_results_security
            elif task_name.startswith("optimize_") and hasattr(self, 'stacked_widget_results_optimize'):
                target_stacked_widget = self.stacked_widget_results_optimize
            elif task_name.startswith("network_") and hasattr(self, 'stacked_widget_results_network'):
                target_stacked_widget = self.stacked_widget_results_network
            # Add other task prefixes and their corresponding stacked_widgets here

            if target_stacked_widget:
                target_stacked_widget.setCurrentIndex(0) # Show QTextEdit for errors
                text_edit_target = target_stacked_widget.widget(0).findChild(QTextEdit)
                if text_edit_target:
                    self._update_display_widget(text_edit_target, html.escape(f"Lỗi khi thực hiện tác vụ:\n{error_message}").replace("\n", "<br>"), is_error=True)
                self._update_save_button_state_for_tab_content(target_stacked_widget)
            self._update_status_bar(f"Lỗi tác vụ: {error_message[:100]}...", "error")
    def toggle_notes_visibility(self, checked):
        """Hiện hoặc ẩn ô Ghi chú dựa vào trạng thái checkbox."""
        self.label_notes_qt.setVisible(checked)
        self.text_notes_qt.setVisible(checked)

    def on_export_info_qt(self):
        if not self.pc_info_dict:
            QMessageBox.warning(self, "Chưa có thông tin", "Thông tin Trang chủ chưa được tải. Vui lòng đợi hoặc làm mới.")
            return
        try:
            user_name = self.entry_name_qt.text().strip()
            department = self.entry_department_qt.text().strip()
            floor_selection = self.combo_floor_qt.currentText()
            custom_floor = self.entry_custom_floor_qt.text().strip() if floor_selection == "Khác" else ""
            position = self.entry_position_qt.text().strip()
            notes = self.text_notes_qt.toPlainText().strip()
            final_floor = custom_floor if floor_selection == "Khác" and custom_floor else floor_selection

            user_info = {"Name": user_name, "Department": department, "Floor": final_floor, "Position": position, "Notes": notes}
            validate_user_input(user_info)

            full_formatted_pc_info_for_file = format_pc_info_to_string(self.pc_info_dict) # Format toàn bộ dữ liệu
            formatted_user_text = format_user_info_for_display(user_info)
            full_content_to_save = f"{formatted_user_text}\n\n{full_formatted_pc_info_for_file}"
            filename_suggestion = generate_filename(user_info, self.pc_info_dict)

            save_dir_default = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Exports_Formatted_TXT")
            os.makedirs(save_dir_default, exist_ok=True)
            
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu File Thông Tin PC", os.path.join(save_dir_default, filename_suggestion), "Text Files (*.txt);;All Files (*)")

            if file_path:
                save_text_to_file(full_content_to_save, file_path)
                network_instruction = "\\\\pc-it-08\\Tools\\User"
                QMessageBox.information(self, "Thành Công", f"Thông tin đã được lưu thành công vào file:\n{file_path}\n\n"
                                          f"Vui lòng copy file này và dán vào thư mục bằng cách nhấn Win+R "
                                          f"và nhập: {network_instruction}") # type: ignore
                self._update_status_bar(f"Xuất báo cáo PC thành công: {os.path.basename(file_path)}", "success")
        
        except ValueError as ve:
            QMessageBox.critical(self, "Thiếu thông tin", str(ve))
        except (IOError, RuntimeError) as save_e:
            QMessageBox.critical(self, "Lỗi Lưu File", f"Không thể lưu file:\n{save_e}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi xuất file: {e}")
            logging.exception("Lỗi không xác định khi xuất file:")
            self._update_status_bar(f"Lỗi khi xuất báo cáo PC: {str(e)[:100]}...", "error")


    def _get_table_content_as_text(self, table_widget):
        if not table_widget: return ""
        header = [table_widget.horizontalHeaderItem(c).text() for c in range(table_widget.columnCount())]
        lines = [",".join(header)]
        for r in range(table_widget.rowCount()):
            row_data = []
            for c in range(table_widget.columnCount()):
                item = table_widget.item(r, c)
                row_data.append(item.text() if item else "")
            lines.append(",".join(row_data))
        return "\n".join(lines)

    def on_export_csv_qt(self):
        current_tab_widget = self.notebook.currentWidget()
        # This needs to be updated to reflect new tab structure and stacked widgets
        table_to_export = None
        if current_tab_widget == self.page_security and self.stacked_widget_results_security.currentIndex() == 1:
            table_to_export = self.table_security_results_qt
        elif current_tab_widget == self.page_optimize and self.stacked_widget_results_optimize.currentIndex() == 1:
            table_to_export = self.table_optimize_results_qt
        elif current_tab_widget == self.page_network and self.stacked_widget_results_network.currentIndex() == 1:
            table_to_export = self.table_network_results_qt
        # Add elif for self.page_system_info if it has tables to export
        # elif current_tab_widget == self.page_system_info and self.stacked_widget_results_system.currentIndex() == 1:
        #     table_to_export = self.table_system_results_qt
        if not table_to_export or table_to_export.rowCount() == 0:
            QMessageBox.warning(self, "Không có dữ liệu", "Không có dữ liệu bảng để xuất CSV.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_suggestion = f"TableData_{timestamp}.csv"
        save_dir_default = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Tool_Exports")
        os.makedirs(save_dir_default, exist_ok=True)
        file_path, _ = QFileDialog.getSaveFileName(self, "Xuất Bảng ra CSV", os.path.join(save_dir_default, filename_suggestion), "CSV Files (*.csv);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig for Excel compatibility
                    writer = csv.writer(csvfile)
                    header = [table_to_export.horizontalHeaderItem(c).text() for c in range(table_to_export.columnCount())]
                    writer.writerow(header)
                    for r in range(table_to_export.rowCount()):
                        row_data = [table_to_export.item(r, c).text() if table_to_export.item(r, c) else "" for c in range(table_to_export.columnCount())]
                        writer.writerow(row_data)
                QMessageBox.information(self, "Xuất CSV Thành Công", f"Dữ liệu bảng đã được xuất ra:\n{file_path}")
                self._update_status_bar(f"Xuất CSV thành công: {os.path.basename(file_path)}", "success")
            
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Xuất CSV", f"Không thể xuất CSV: {e}")
                logging.exception("Lỗi khi xuất CSV:")
                self._update_status_bar(f"Lỗi xuất CSV: {str(e)[:100]}...", "error")


    def _run_task_in_thread_qt(self, button_clicked, target_stacked_widget, task_function, task_name_prefix, needs_wmi=False, wmi_namespace="root\\CIMV2", task_args=None, result_type="text"):
        task_name = f"{task_name_prefix}_{task_function.__name__}_{datetime.now().strftime('%H%M%S%f')}" # Unique task name
        
        # Determine which QTextEdit to update for "Đang thực hiện..."
        # This assumes the QTextEdit is always at index 0 of the QGroupBox in the QStackedWidget's page 0
        text_display_for_loading = target_stacked_widget.widget(0).findChild(QTextEdit)
        if text_display_for_loading:
            self._update_display_widget(text_display_for_loading, html.escape(f"Đang thực hiện: {task_function.__name__}..."))
        self._update_status_bar(f"Đang thực hiện: {task_function.__name__}...", "info")
        
        # if task_function.__name__ == "run_disk_speed_test":
            # self.toast_notifier.show_toast("Đang kiểm tra tốc độ ổ cứng, vui lòng đợi...", parent_widget=target_stacked_widget, duration_ms=5000) # Đã được xử lý bởi _update_status_bar
        target_stacked_widget.setCurrentIndex(0) # Show text display during loading

        # Clear previous search in the target_widget before running a new task
        # Clear the global search bar
        if hasattr(self, 'global_search_input'):
            self.global_search_input.clear() # Clearing will trigger empty search/filter via _perform_global_search

        # Explicitly clear highlights. Check if text_display_for_loading is not None before using.
        # Also, ensure it's a QTextEdit.
        if text_display_for_loading and isinstance(text_display_for_loading, QTextEdit):
            self._clear_text_highlights(text_display_for_loading)

        current_page_widget = self.pages_stack.currentWidget()
        # Check if the current page is one of the new tabs that have savable results
        if current_page_widget in [self.page_security, self.page_optimize, self.page_network]:
            self.button_save_active_tab_result.setEnabled(False)
        # Add other pages here if they also have a "save result" button that needs disabling during task execution
            
        # Đảm bảo task_args là một tuple để unpack an toàn
        if task_args is None:
            actual_args_for_thread_tuple = tuple()
        elif not isinstance(task_args, (list, tuple)): # If it's a single non-list/tuple arg
            actual_args_for_thread_tuple = (task_args,)
        else: # It's already a list or tuple
            actual_args_for_thread_tuple = tuple(task_args)
        thread = WorkerThread(task_function, task_name, needs_wmi, wmi_namespace,
                                *actual_args_for_thread_tuple,
                                button_to_manage=button_clicked,
                                original_button_text=button_clicked.text())
        thread.task_completed.connect(lambda name, data: self._on_generic_task_completed(name, data, target_stacked_widget, result_type))
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        thread.start()

    def _populate_table_widget(self, table_widget, data_list):
        table_widget.clearContents()
        table_widget.setRowCount(0)
        self.current_table_data = None # Clear previous table data for CSV export

        if not data_list or not isinstance(data_list, list) or not isinstance(data_list[0], dict):
            # If data is not suitable for table, show message in text view
            # This case should ideally be handled by result_type="text"
            table_widget.setColumnCount(1)
            table_widget.setHorizontalHeaderLabels(["Thông báo"])
            table_widget.setRowCount(1)
            table_widget.setItem(0,0, QTableWidgetItem("Dữ liệu không phù hợp cho bảng hoặc không có dữ liệu."))
            return

        headers = list(data_list[0].keys())
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.setRowCount(len(data_list))

        for row_idx, row_data in enumerate(data_list):
            for col_idx, header in enumerate(headers):
                item_value = str(row_data.get(header, ""))
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(item_value))
        
        table_widget.resizeColumnsToContents()
        self.current_table_data = data_list # Store for CSV export

    def _on_generic_task_completed(self, task_name, data, target_stacked_widget, result_type="text"):
        if result_type == "table" and isinstance(data, list) and data and isinstance(data[0], dict):
            table_widget_target = target_stacked_widget.widget(1) # Assuming table is at index 1
            if isinstance(table_widget_target, QTableWidget):
                self._populate_table_widget(table_widget_target, data)
                target_stacked_widget.setCurrentIndex(1) # Switch to table view
                # self.button_export_csv.setVisible(True) # Button removed
            else: # Fallback to text if widget at index 1 is not a table
                result_type = "text" # Force text display
        
        if result_type == "text":
            if task_name.startswith("utility_disk_speed_test_run_disk_speed_test"):
                self.toast_notifier.show_toast("Kiểm tra tốc độ ổ cứng hoàn tất.", parent_widget=self, toast_type='success')
            
            text_edit_target = target_stacked_widget.widget(0).findChild(QTextEdit) # TextEdit is in a QGroupBox
            display_text = self._format_task_result_for_display_generic(data)
            self._update_display_widget(text_edit_target, display_text)
            target_stacked_widget.setCurrentIndex(0) # Switch to text view
            # self.button_export_csv.setVisible(False) # Button removed
        self._update_status_bar(f"Hoàn thành tác vụ: {task_name.split('_')[1] if '_' in task_name else task_name}", "success")
        self._update_save_button_state_for_tab_content(target_stacked_widget)
    
    # Removed redundant _on_task_error definition. The one at line 1014 is used.

    def _is_value_unavailable(self, val):
        """Kiểm tra xem một giá trị có được coi là không khả dụng hoặc trống để hiển thị không."""
        if val is None:
            return True
        # Kiểm tra xem biểu diễn chuỗi, sau khi loại bỏ khoảng trắng, có trống hoặc là một hằng số không khả dụng không
        s_val = str(val).strip() # Điều này xử lý nếu val đã là một chuỗi
        if not s_val or s_val in self.UNAVAILABLE_STR_CONSTANTS: # Sử dụng hằng số của lớp
            return True
        return False

    def _format_details_content_html(self, details_content):
        """Hàm trợ giúp để định dạng phần 'details' của một từ điển trạng thái thành HTML."""
        if self._is_value_unavailable(details_content):
            return ""

        temp_details_accumulator = []
        has_any_detail_content = False

        if isinstance(details_content, dict):
            for k_detail, v_detail_raw in details_content.items():
                if not self._is_value_unavailable(v_detail_raw):
                    has_any_detail_content = True
                    if k_detail == 'errors_list' and isinstance(v_detail_raw, list) and v_detail_raw:
                        temp_details_accumulator.append(f"  <b>Lỗi chi tiết:</b>")
                        valid_errors = [e_item for e_item in v_detail_raw if not self._is_value_unavailable(e_item)]
                        for err_item in valid_errors[:5]:
                            temp_details_accumulator.append(f"    - {html.escape(str(err_item))}")
                        if len(valid_errors) > 5:
                            temp_details_accumulator.append("    ...")
                    elif k_detail in ['deleted_files_count', 'deleted_folders_count', 'total_size_freed_mb', 
                                      'files_found', 'folders_found', 'total_size_mb', 'bytes_freed']: # Thêm các khóa đã biết
                        display_key = html.escape(str(k_detail).replace('_', ' ').title())
                        temp_details_accumulator.append(f"  <b>{display_key}:</b> {html.escape(str(v_detail_raw))}")
                    else: # Khóa-giá trị chung cho các chi tiết khác
                        temp_details_accumulator.append(f"  <b>{html.escape(str(k_detail))}:</b> {html.escape(str(v_detail_raw))}")
        elif isinstance(details_content, list):
            processed_list_items = [f"  - {html.escape(str(d_item))}" for d_item in details_content if not self._is_value_unavailable(d_item)]
            if processed_list_items:
                temp_details_accumulator.extend(processed_list_items)
                has_any_detail_content = True
        else: # Chuỗi chi tiết chung
            if not self._is_value_unavailable(details_content): # Kiểm tra lại nếu là chuỗi đơn giản
                temp_details_accumulator.append(f"  {html.escape(str(details_content))}")
                has_any_detail_content = True

        if has_any_detail_content:
            return "<br><b>Chi tiết:</b><br>" + "<br>".join(temp_details_accumulator)
        return ""
    def _format_task_result_for_display_generic(self, result_data):
        """Định dạng kết quả tác vụ thành chuỗi, sử dụng ** cho bold.
           Bỏ qua các giá trị không khả dụng hoặc rỗng. Output is HTML."""
        if self._is_value_unavailable(result_data):
            return html.escape(str(NOT_AVAILABLE))

        html_lines = []
        if isinstance(result_data, list):
            if not result_data:
                return html.escape("Tác vụ hoàn thành, không có mục nào được trả về.")
            for item in result_data:
                if self._is_value_unavailable(item):
                    continue # Skip unavailable items in a list
                elif isinstance(item, dict):
                    item_lines = []
                    for k, v_raw in item.items():
                        if not self._is_value_unavailable(v_raw): # Corrected call
                            item_lines.append(f"  <b>{html.escape(str(k))}:</b> {html.escape(str(v_raw))}")
                    if item_lines: # Only add if there's something to show for this item
                        html_lines.append("<br>".join(item_lines))
                else:
                    html_lines.append(html.escape(str(item)))
            if not html_lines:
                return html.escape(str(NOT_AVAILABLE)) # Or "Không có thông tin khả dụng."
            return "<br>---<br>".join(html_lines)

        elif isinstance(result_data, dict):
            if not result_data:
                return html.escape("Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng).")
            
            if "message" in result_data and "status" in result_data: # Special status dict
                status_val = result_data.get('status', 'N/A')
                message_val = result_data['message']

                if not self._is_value_unavailable(status_val):
                    html_lines.append(f"<b>Trạng thái:</b> {html.escape(str(status_val))}")
                if not self._is_value_unavailable(message_val):
                    html_lines.append(f"<b>Thông điệp:</b> {html.escape(str(message_val))}")
                
                if "details" in result_data:
                    formatted_details = self._format_details_content_html(result_data['details'])
                    if formatted_details:
                        html_lines.append(formatted_details)

                if "path" in result_data and not self._is_value_unavailable(result_data['path']):    html_lines.append(f"<br><b>Đường dẫn file:</b> {html.escape(str(result_data['path']))}")
                if not html_lines: return html.escape(str(NOT_AVAILABLE))
                return "<br>".join(html_lines)
            else:
                for k, v_raw in result_data.items():
                    if not self._is_value_unavailable(v_raw):
                        html_lines.append(f"<b>{html.escape(str(k))}:</b> {html.escape(str(v_raw))}")
                if not html_lines: return html.escape(str(NOT_AVAILABLE))
                return "<br>".join(html_lines)
        else:
            # This case should have been caught by the initial is_value_unavailable(result_data)
            # but as a fallback, ensure we don't return the unavailable constant itself.            
            return html.escape(str(result_data)) if not self._is_value_unavailable(result_data) else html.escape(NOT_AVAILABLE)

    def enable_firewall_qt(self):
        if QMessageBox.question(self, "Xác nhận Bật Tường lửa", "Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            # Determine the correct stacked_widget based on the sender's parent tab or current tab
            # Assuming this button is on the security tab:
            self._run_task_in_thread_qt(self.sender(), self.stacked_widget_results_security, toggle_firewall, "security_firewall_enable", needs_wmi=False, task_args=[True])

    def disable_firewall_qt(self):
        if QMessageBox.question(self, "XÁC NHẬN TẮT TƯỜNG LỬA", "CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            # Assuming this button is on the security tab:
            self._run_task_in_thread_qt(self.sender(), self.stacked_widget_results_security, toggle_firewall, "security_firewall_disable", needs_wmi=False, task_args=[False])

    def run_domain_ip_resolution_qt(self, button_clicked): # Added button_clicked
        """Mở hộp thoại yêu cầu người dùng nhập tên miền, sau đó chạy tra cứu DNS."""
        domain_name, ok = QInputDialog.getText(self, "Phân giải IP tên miền", "Nhập tên miền (ví dụ: google.com):")
        
        if ok and domain_name.strip():
            # Assuming this button is on the network tab:
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_network, 
                                        lookup_dns_address, "network_resolve_domain_ip", 
                                        needs_wmi=False, task_args=[domain_name.strip()])
        elif ok: # Người dùng nhấn OK nhưng không nhập gì
            QMessageBox.warning(self, "Đầu vào trống", "Bạn chưa nhập tên miền.")

    def run_set_dns_config_qt(self, button_clicked): # Added button_clicked
        """Mở hộp thoại cấu hình DNS và thực thi."""
        dialog = SetDnsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            primary_dns, secondary_dns = dialog.get_dns_values()
            if not primary_dns: # Should not happen if placeholder is used
                QMessageBox.warning(self, "Thiếu DNS chính", "Vui lòng nhập địa chỉ DNS chính.")
                return
            
            # Kiểm tra sơ bộ định dạng IP (đơn giản)
            import re
            ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
            if not re.match(ip_pattern, primary_dns) or (secondary_dns and not re.match(ip_pattern, secondary_dns)):
                QMessageBox.warning(self, "Định dạng IP không hợp lệ", "Vui lòng nhập địa chỉ DNS đúng định dạng IP (ví dụ: 8.8.8.8).")
                return
            # Assuming this button is on the network tab:
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_network, set_dns_servers, "network_set_dns", needs_wmi=True, task_args=[primary_dns, secondary_dns])

    def run_domain_ip_resolution_qt(self, button_clicked):
        """Mở hộp thoại yêu cầu người dùng nhập tên miền, sau đó chạy tra cứu DNS."""
        domain_name, ok = QInputDialog.getText(self, "Phân giải IP tên miền", "Nhập tên miền (ví dụ: google.com):")
        
        if ok and domain_name.strip():
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_utilities, 
                                        lookup_dns_address, "utility_resolve_domain_ip", # This task_name_prefix needs to match the tab
                                        needs_wmi=False, task_args=[domain_name.strip()])
        elif ok: # Người dùng nhấn OK nhưng không nhập gì
            QMessageBox.warning(self, "Đầu vào trống", "Bạn chưa nhập tên miền.")

    def run_set_dns_config_qt(self, button_clicked):
        """Mở hộp thoại cấu hình DNS và thực thi."""
        dialog = SetDnsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            primary_dns, secondary_dns = dialog.get_dns_values()
            if not primary_dns: # Should not happen if placeholder is used
                QMessageBox.warning(self, "Thiếu DNS chính", "Vui lòng nhập địa chỉ DNS chính.")
                return
            
            # Kiểm tra sơ bộ định dạng IP (đơn giản)
            import re
            ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
            if not re.match(ip_pattern, primary_dns) or (secondary_dns and not re.match(ip_pattern, secondary_dns)):
                QMessageBox.warning(self, "Định dạng IP không hợp lệ", "Vui lòng nhập địa chỉ DNS đúng định dạng IP (ví dụ: 8.8.8.8).")
                return
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_utilities, set_dns_servers, "utility_set_dns", needs_wmi=True, task_args=[primary_dns, secondary_dns]) # This task_name_prefix needs to match the tab

    def closeEvent(self, event): # type: ignore
        # Dọn dẹp luồng khi đóng ứng dụng
        active_threads = [t for t in self.threads if t.isRunning()]
        if active_threads:
            reply = QMessageBox.question(self, 'Thoát Ứng Dụng',
                                         f"Có {len(active_threads)} tác vụ đang chạy. Bạn có chắc muốn thoát?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for thread in active_threads:
                    logging.info(f"Requesting thread {thread.task_name} to quit...")
                    thread.quit() # Yêu cầu luồng dừng một cách nhẹ nhàng
                    if not thread.wait(1000): # Đợi tối đa 1 giây
                        logging.warning(f"Thread {thread.task_name} did not finish gracefully, terminating.")
                        thread.terminate() # Buộc dừng nếu không phản hồi
                event.accept()
            else:
                event.ignore()
        elif event.isAccepted(): # Ensure super is called if event is accepted by this path too
             super().closeEvent(event)
        # If event was not accepted by this logic, it might be handled by base class or ignored.
 
    def _on_navigation_changed(self, index):
        """Clears search inputs and highlights when tab changes."""
        self.pages_stack.setCurrentIndex(index) # Ensure stack is synchronized
        current_page_widget = self.pages_stack.widget(index)

        # Show/hide global search bar based on the current tab
        # Tabs that benefit from search: Security, Optimize, Network, System Info (if it has searchable content)
        if current_page_widget in [self.page_security, self.page_optimize, self.page_network, self.page_system_info]:
            self.search_bar_container.setVisible(True)
            self.global_search_input.clear() # Clear search when tab changes
        else:
            self.search_bar_container.setVisible(False)

        # Clear highlights in text display areas
        if hasattr(self, 'stacked_widget_results_security'):
            text_edit_sec = self.stacked_widget_results_security.widget(0).findChild(QTextEdit)
            if text_edit_sec: self._clear_text_highlights(text_edit_sec)
        if hasattr(self, 'stacked_widget_results_optimize'):
            text_edit_opt = self.stacked_widget_results_optimize.widget(0).findChild(QTextEdit)
            if text_edit_opt: self._clear_text_highlights(text_edit_opt)
        if hasattr(self, 'stacked_widget_results_network'):
            text_edit_net = self.stacked_widget_results_network.widget(0).findChild(QTextEdit)
            if text_edit_net: self._clear_text_highlights(text_edit_net)
        
        # If System Info tab has searchable text areas, clear their highlights too
        # if current_page_widget == self.page_system_info:
        #     # Example: if cards on system_info tab are QLabels and search highlights them
        #     card_widgets = [self.card_general_info, self.card_os_info, ...] 
        #     for card in card_widgets:
        #         content_label = card.findChild(QLabel)
        #         if content_label:
        #             # Re-populate card to clear highlights (if search modified them)
        #             # This requires storing original data or re-fetching, which might be complex.
        #             # A simpler approach is if search on labels doesn't use persistent background changes.
        #             pass

        self._update_active_save_button_state()

    def _setup_results_table(self, table_widget):
        """Helper function to setup common properties for results QTableWidget."""
        table_widget.setFont(self.body_font)
        table_widget.setAlternatingRowColors(True)
        table_widget.setSortingEnabled(True)
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only
        table_widget.setObjectName("ResultTableWidget") # For QSS styling




    def _update_toggle_nav_button_state(self):
        if self.nav_panel_is_collapsed:
            if hasattr(self, 'icon_expand_nav') and hasattr(self, 'button_toggle_nav_header'):
                self.button_toggle_nav_header.setIcon(self.icon_expand_nav)
                self.button_toggle_nav_header.setText("") # Icon only
                self.button_toggle_nav_header.setToolTip("Mở rộng menu")
        else:
            if hasattr(self, 'icon_collapse_nav') and hasattr(self, 'button_toggle_nav_header'):
                self.button_toggle_nav_header.setIcon(self.icon_collapse_nav)
                self.button_toggle_nav_header.setText("") # Icon only
                self.button_toggle_nav_header.setToolTip("Thu gọn menu")

    def _toggle_nav_panel_visibility(self):
        self.nav_panel_is_collapsed = not self.nav_panel_is_collapsed
        
        current_sizes = self.main_content_splitter.sizes()
        current_total_width = sum(current_sizes)
        target_nav_width = 0

        if self.nav_panel_is_collapsed:
            target_nav_width = self.NAV_COLLAPSED_WIDTH
            for i in range(self.nav_list_widget.count()):
                item = self.nav_list_widget.item(i)
                if item:
                    # Store original text if not already stored or if it's different
                    if item.data(Qt.UserRole) is None or item.data(Qt.UserRole) != item.text():
                         item.setData(Qt.UserRole, item.text())
                    item.setText("") # Clear text to show only icon for list items
            # Button text/icon for header toggle is handled by _update_toggle_nav_button_state
        else:
            target_nav_width = self.NAV_EXPANDED_WIDTH
            for i in range(self.nav_list_widget.count()):
                item = self.nav_list_widget.item(i)
                if item:
                    original_text = item.data(Qt.UserRole)
                    if original_text is not None:
                        item.setText(original_text) # Restore text

        content_pane_width = current_total_width - target_nav_width
        self.main_content_splitter.setSizes([target_nav_width, content_pane_width if content_pane_width > 0 else 0])
        self._update_toggle_nav_button_state()

    def _style_save_button(self, button, on_click_action):
        button.setCursor(Qt.PointingHandCursor)
        button.setFont(self.body_font)
        button.setEnabled(False) # Initially disabled
        button.setObjectName("SaveResultButton") # For QSS styling
        button.clicked.connect(on_click_action)

    def _can_save_current_tab_content(self, stacked_widget_results):
        current_widget_on_stack = stacked_widget_results.currentWidget()
        content_to_check = ""

        if isinstance(current_widget_on_stack, QGroupBox): # QTextEdit page
            text_edit = current_widget_on_stack.findChild(QTextEdit)
            if text_edit:
                content_to_check = text_edit.toPlainText().strip()
        elif isinstance(current_widget_on_stack, QTableWidget): # QTableWidget page
            table_widget = current_widget_on_stack
            if table_widget.rowCount() > 0:
                content_to_check = "has_table_data" # Chỉ cần một giá trị không rỗng

        if not content_to_check or \
           "Đang thực hiện:" in content_to_check or \
           "Kết quả của tiện ích sẽ hiển thị ở đây." in content_to_check or \
           "Chọn một tác vụ để thực hiện." in content_to_check:
            return False
        return True

    def _update_save_button_state_for_tab_content(self, stacked_widget):
        """Cập nhật trạng thái nút Lưu/Xuất cho tab Tiện ích/Fixes."""
        # This function needs to be aware of which tab is active to enable/disable the correct save button
        current_page_widget = self.pages_stack.currentWidget()
        # Check if the current page is one of the tabs that has a stacked_widget for results
        if current_page_widget not in [self.page_security, 
                                       self.page_optimize, 
                                       self.page_network,
                                       self.page_system_info]: # Add other tabs if they have savable content
            return # Chỉ xử lý cho tab Tiện ích và Fixes

        can_save = self._can_save_current_tab_content(stacked_widget)
        self.button_save_active_tab_result.setVisible(True) # Luôn hiển thị ở các tab này
        self.button_save_active_tab_result.setEnabled(can_save)

    def _update_active_save_button_state(self):
        """Cập nhật text, visibility và enabled state của nút Lưu/Xuất chính."""
        current_page_widget = self.pages_stack.currentWidget()

        # Handle Refresh Dashboard button visibility
        self.button_refresh_dashboard_qt.setVisible(current_page_widget == self.page_dashboard)

        if current_page_widget == self.page_dashboard:
            self.button_save_active_tab_result.setVisible(False) # No direct save/export from dashboard view
        elif current_page_widget == self.page_system_info:
            # For System Info, the main save button could trigger the full PC report export
            # Or, if System Info tab has its own specific "save details" it would be handled here.
            # For now, let's assume it doesn't have a dedicated save button in global footer.
            self.button_save_active_tab_result.setVisible(False) 
        elif current_page_widget == self.page_security:
            self.button_save_active_tab_result.setText("Lưu Kết Quả Bảo Mật")
            self._update_save_button_state_for_tab_content(self.stacked_widget_results_security)
        elif current_page_widget == self.page_optimize:
            self.button_save_active_tab_result.setText("Lưu Kết Quả Tối Ưu")
            self._update_save_button_state_for_tab_content(self.stacked_widget_results_optimize)
        elif current_page_widget == self.page_network:
            self.button_save_active_tab_result.setText("Lưu Kết Quả Mạng")
            self._update_save_button_state_for_tab_content(self.stacked_widget_results_network)
        elif current_page_widget == self.page_report_settings:
            self.button_save_active_tab_result.setText("Xuất Báo Cáo PC")
            self.button_save_active_tab_result.setVisible(True)
            self.button_save_active_tab_result.setEnabled(self.pc_info_dict is not None)
        else:
            self.button_save_active_tab_result.setVisible(False)

    def on_save_active_tab_result_qt(self):
        current_page_widget = self.pages_stack.currentWidget()
        if current_page_widget == self.page_report_settings: # Export PC Report from this tab
            self.on_export_info_qt()
        elif current_page_widget == self.page_utilities: # Added condition for utilities tab
            self._save_generic_tab_result(self.stacked_widget_results_utilities, "KetQua_TienIch")
        elif current_page_widget == self.page_fixes:
            self._save_generic_tab_result(self.stacked_widget_results_fixes, "KetQua_SuaLoi")
        else:
            QMessageBox.information(self, "Thông báo", "Không có kết quả nào để lưu từ tab hiện tại.")
    def _save_generic_tab_result(self, stacked_widget_results, default_prefix="KetQua"):
        current_widget = stacked_widget_results.currentWidget()
        content_to_save = ""

        if isinstance(current_widget, QGroupBox): # It's the QTextEdit page
            text_edit = current_widget.findChild(QTextEdit)
            if text_edit:
                content_to_save = text_edit.toPlainText().strip()
        elif isinstance(current_widget, QTableWidget): # It's the QTableWidget page
            table_widget = current_widget
            content_to_save = self._get_table_content_as_text(table_widget)

        if not self._can_save_current_tab_content(stacked_widget_results): # Sử dụng hàm kiểm tra chung
            QMessageBox.warning(self, "Không có kết quả", "Không có kết quả hợp lệ để lưu hoặc tác vụ đang chạy.")
            return
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_suggestion = f"{default_prefix}_{timestamp}.txt"
            save_dir_default = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Tool_Results")
            os.makedirs(save_dir_default, exist_ok=True)

            file_path, _ = QFileDialog.getSaveFileName(self, f"Lưu Kết Quả {default_prefix}", os.path.join(save_dir_default, filename_suggestion), "Text Files (*.txt);;All Files (*)")

            if file_path:
                save_text_to_file(content_to_save, file_path)
                QMessageBox.information(self, "Lưu Thành Công", f"Kết quả đã được lưu vào:\n{file_path}")
                self._update_status_bar(f"Lưu kết quả tab thành công: {os.path.basename(file_path)}", "success")
        except (IOError, RuntimeError) as save_e:
            QMessageBox.critical(self, "Lỗi Lưu File", f"Không thể lưu file kết quả:\n{save_e}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi lưu kết quả: {e}")
            logging.exception("Lỗi không xác định khi lưu kết quả tab:")
            self._update_status_bar(f"Lỗi lưu kết quả tab: {str(e)[:100]}...", "error")

# Khối main để chạy thử trực tiếp file này (nếu cần)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = PcInfoAppQt()
#     main_window.show()
#     sys.exit(app.exec_())