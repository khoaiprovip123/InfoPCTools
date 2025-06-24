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
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QStackedWidget, QListWidget, QListWidgetItem, QSplitter, QDialog, QFormLayout, QDialogButtonBox, QProgressBar, QSizePolicy,
    QGroupBox, QScrollArea, QMessageBox, QFileDialog, QGridLayout, QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog,
    QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextOption, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QSize # Import QSize, QThread, pyqtSignal removed

import psutil # Import psutil for real-time usage
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
    lookup_dns_address,
    list_upgradable_winget_packages, # Cho Update Center
    get_active_network_connections, # Ví dụ: netstat    
    # Các hàm cho tính năng (một số sẽ bị loại bỏ khỏi GUI)
    run_cpu_benchmark, run_gpu_benchmark, run_memory_speed_test, run_disk_speed_test, # Cho tab Hiệu năng
    optimize_windows_services, clean_registry_with_backup, # Cho tab Fix Hệ Thống
    get_disk_health_status,   # Hàm mới cho tình trạng ổ cứng
    get_battery_details,      # Hàm mới cho chi tiết pin
    set_dns_servers,          # Hàm mới để cấu hình DNS
    flush_dns_cache,          # Ví dụ: ipconfig /flushdns
    calculate_system_health_score, # Cho System Health Score
    apply_gaming_mode,             # Cho Gaming Mode
    set_high_performance_power_plan, # Cho Tăng Tốc PC
    manage_startup_item,           # Cho Startup Manager (enable/disable/delete)
    get_windows_update_status,     # Cho Update Center (placeholder)
    list_printers, remove_printer, clear_print_queue, restart_print_spooler_service # Printer utilities
)
from core.pc_info_manager import (
    validate_user_input, generate_filename, save_text_to_file,
    format_pc_info_to_string, format_system_details_to_string,
    format_user_info_for_display # Import hàm này
)
# Import WorkerThread từ file mới
from core.pc_info_functions import get_gpu_realtime_usage # Import hàm lấy GPU real-time
from .gui_worker import WorkerThread
# Import các hàm tạo giao diện tab từ các file riêng
from .gui_dashboard_tab import create_dashboard_tab_content # type: ignore
# Thêm import cho các file tab khác khi bạn tạo chúng:
from .gui_system_info_tab import create_system_info_tab_content # type: ignore #Đã có
from .gui_security_tab import create_security_tab_content # type: ignore #Đã có
# from .gui_optimize_tab import create_optimize_tab_content
# from .gui_network_tab import create_network_tab_content #Đã có
# from .gui_update_center_tab import create_update_center_tab_content
# from .gui_report_settings_tab import create_report_settings_tab_content
from .gui_optimize_tab import create_optimize_tab_content # type: ignore
from .gui_network_tab import create_network_tab_content # type: ignore
# --- Cấu hình Logging ---
# from .gui_update_center_tab import create_update_center_tab_content # Thêm dòng này khi bạn tạo file
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Logging nên được cấu hình ở main.py để tránh ghi đè hoặc xung đột
from .gui_report_settings_tab import create_report_settings_tab_content # type: ignore #Đã có
from .gui_constants import * # Import tất cả hằng số từ file mới


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
            # Lấy tọa độ toàn cục của cửa sổ chính (QMainWindow)
            main_window = self.parentWidget() # Assuming ToastNotification's parent is the QMainWindow
            if not isinstance(main_window, QMainWindow): # Fallback if parent is not QMainWindow
                main_window = QApplication.instance().activeWindow()
                if not isinstance(main_window, QMainWindow):
                    main_window = parent_widget # Use parent_widget as fallback if no QMainWindow found

            main_window_rect = main_window.geometry()
            
            # Tính toán vị trí ở giữa phía dưới của cửa sổ chính
            toast_x = main_window_rect.x() + (main_window_rect.width() - self.width()) // 2
            toast_y = main_window_rect.y() + main_window_rect.height() - self.height() - 30 # 30px từ dưới lên

            
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
        self.setWindowTitle("PC Pro - System Optimizer") # New app title
        self.setGeometry(100, 100, 1200, 800) # Adjusted size for new layout

        self.h1_font = QFont(DEFAULT_FONT_FAMILY, H1_FONT_SIZE, QFont.Bold)
        self.h2_font = QFont(DEFAULT_FONT_FAMILY, H2_FONT_SIZE, QFont.Bold)
        self.body_font = QFont(DEFAULT_FONT_FAMILY, BODY_FONT_SIZE)
        self.bold_body_font = QFont(DEFAULT_FONT_FAMILY, BODY_FONT_SIZE, QFont.Bold) # Font mới
        self.monospace_font = QFont(MONOSPACE_FONT_FAMILY, MONOSPACE_FONT_SIZE)

        # --- State Variables ---
        self.pc_info_dict = None
        # self.formatted_pc_info_string_home = "Chưa lấy thông tin." # No longer needed as we populate cards
        self.current_table_data = None # To store data for CSV export

        self.NAV_EXPANDED_WIDTH = 280 # From HTML
        self.NAV_COLLAPSED_WIDTH = 70 # Icon + padding
        self.nav_panel_is_collapsed = False
        self.nav_is_collapsed = False # State for navigation panel

        self.threads = [] # List để giữ các QThread đang chạy

        self._load_logo()
        self._init_timers() # Khởi tạo các QTimer cho debouncing
        self._create_widgets()
        self._apply_styles()
        self.toast_notifier = ToastNotification(self) # Khởi tạo toast notifier
        self._start_realtime_update_timer() # Bắt đầu timer cập nhật liên tục
        self.fetch_pc_info_threaded()

    def _load_logo(self):
        self.logo_pixmap = None
        try:
            logo_relative_path = os.path.join("assets", "logo", "hpc-logo.png")
            logo_path = resource_path(logo_relative_path)
            if os.path.exists(logo_path):
                raw_pixmap = QPixmap(logo_path)
                if not raw_pixmap.isNull():
                    self.logo_pixmap = raw_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Smaller logo for sidebar
                else:
                    logging.warning(f"Could not load QPixmap from: {logo_path}")
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
        # Timer cho cập nhật phần trăm sử dụng liên tục
        self.realtime_update_timer = QTimer(self)
        self.realtime_update_timer.timeout.connect(self._update_realtime_usage)


    def _create_widgets(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        # Main layout is now QHBoxLayout for sidebar + main_content_container
        self.main_app_layout = QHBoxLayout(self.central_widget)
        self.main_app_layout.setContentsMargins(0,0,0,0) # Container fills window
        self.main_app_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setFixedWidth(self.NAV_EXPANDED_WIDTH)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 20, 0, 20) # Top/bottom padding
        sidebar_layout.setSpacing(10)

        # Sidebar: Logo Area
        logo_area_widget = QWidget()
        logo_area_layout = QVBoxLayout(logo_area_widget)
        logo_area_layout.setContentsMargins(20,0,20,20) # Padding for logo area
        logo_area_layout.setAlignment(Qt.AlignCenter)

        if self.logo_pixmap:
            self.app_logo_label = QLabel()
            self.app_logo_label.setPixmap(self.logo_pixmap)
            self.app_logo_label.setAlignment(Qt.AlignCenter)
            logo_area_layout.addWidget(self.app_logo_label)

        self.app_title_label_sidebar = QLabel("PC Pro")
        self.app_title_label_sidebar.setObjectName("SidebarAppTitle")
        self.app_title_label_sidebar.setAlignment(Qt.AlignCenter)
        logo_area_layout.addWidget(self.app_title_label_sidebar)

        self.app_subtitle_label_sidebar = QLabel("System Optimizer")
        self.app_subtitle_label_sidebar.setObjectName("SidebarAppSubtitle")
        self.app_subtitle_label_sidebar.setAlignment(Qt.AlignCenter)
        logo_area_layout.addWidget(self.app_subtitle_label_sidebar)
        sidebar_layout.addWidget(logo_area_widget)

        # Sidebar: Navigation List
        self.nav_list_widget = QListWidget()
        self.nav_list_widget.setObjectName("NavList")
        sidebar_layout.addWidget(self.nav_list_widget, 1) # Takes available space

        # Sidebar: Navigation Toggle Button (at the bottom or top of sidebar)
        self.button_toggle_nav_sidebar = QPushButton() # Renamed
        self.button_toggle_nav_sidebar.setCursor(Qt.PointingHandCursor)
        self.button_toggle_nav_sidebar.setObjectName("NavToggleSidebarButton")
        self.button_toggle_nav_sidebar.clicked.connect(self._toggle_nav_panel_visibility)
        self.button_toggle_nav_sidebar.setFixedHeight(40)
        sidebar_layout.addWidget(self.button_toggle_nav_sidebar)

        try:
            self.icon_collapse_nav = QIcon(resource_path(os.path.join("assets", "icons", "menu_collapse.png"))) # e.g. left arrow or hamburger
            self.icon_expand_nav = QIcon(resource_path(os.path.join("assets", "icons", "menu_expand.png")))     # e.g. right arrow
        except Exception as e:
            logging.warning(f"Không thể tải icon cho nút thu/gọn thanh điều hướng: {e}")

        self.main_app_layout.addWidget(self.sidebar_widget)

        # --- Main Content Container ---
        main_content_container = QWidget()
        main_content_container.setObjectName("MainContentContainer")
        self.main_content_layout = QVBoxLayout(main_content_container) # QVBoxLayout for header + stacked_widget + global_buttons
        self.main_content_layout.setContentsMargins(20, 20, 20, 20) # Padding for main content area
        self.main_content_layout.setSpacing(20)

        # Main Content: Page Header
        self.page_header_widget = QWidget()
        self.page_header_widget.setObjectName("PageHeader")
        page_header_layout = QHBoxLayout(self.page_header_widget)
        page_header_layout.setContentsMargins(15, 10, 15, 10) # Padding inside header

        self.page_title_label = QLabel("Dashboard") # Will be updated
        self.page_title_label.setObjectName("PageTitleLabel")
        page_header_layout.addWidget(self.page_title_label, 1, Qt.AlignLeft) # Stretch factor

        # Global Search Input (moved to page header)
        self.global_search_input = QLineEdit()
        self.global_search_input.setFont(self.body_font)
        self.global_search_input.setPlaceholderText("Tìm kiếm...")
        self.global_search_input.textChanged.connect(lambda: self.global_search_timer.start(300))
        self.global_search_input.setFixedWidth(250)
        self.global_search_input.setVisible(False) # Initially hidden
        page_header_layout.addWidget(self.global_search_input, 0, Qt.AlignCenter) # No stretch

        self.health_score_label = QLabel("🎯 Điểm Sức Khỏe: --/100")
        self.health_score_label.setObjectName("HealthScoreLabel")
        page_header_layout.addWidget(self.health_score_label, 1, Qt.AlignRight) # Stretch factor
        self.main_content_layout.addWidget(self.page_header_widget)

        self.pages_stack = QStackedWidget()
        self.main_content_layout.addWidget(self.pages_stack, 1) # StackedWidget takes most space

        self.main_app_layout.addWidget(main_content_container, 1) # Main content takes remaining space

        # --- Global Buttons Frame ---
        global_buttons_frame = QFrame()
        global_buttons_frame.setObjectName("GlobalButtonsFrame")
        global_buttons_layout = QHBoxLayout(global_buttons_frame)
        global_buttons_layout.setContentsMargins(0, 5, 0, 0) # No horizontal margins, top margin

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
        create_dashboard_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Dashboard", self.page_dashboard, icon_path=resource_path(os.path.join("assets", "icons", "dashboard.png")))

        self.page_system_info = QWidget()
        create_system_info_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Hệ Thống", self.page_system_info, icon_path=resource_path(os.path.join("assets", "icons", "system.png")))

        self.page_security = QWidget()
        create_security_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Bảo Mật", self.page_security, icon_path=resource_path(os.path.join("assets", "icons", "security.png")))

        self.page_optimize = QWidget()
        create_optimize_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Tối Ưu", self.page_optimize, icon_path=resource_path(os.path.join("assets", "icons", "optimize.png")))

        self.page_network = QWidget() # Khởi tạo trang Mạng
        create_network_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Mạng", self.page_network, icon_path=resource_path(os.path.join("assets", "icons", "network.png")))

        self.page_update_center = QWidget() # Trang mới: Trung tâm Cập nhật
        # create_update_center_tab_content(self) # Gọi hàm từ module mới khi bạn tạo file
        self._create_update_center_tab(self.page_update_center) # Tạm thời giữ lại
        self._add_navigation_item("Cập nhật", self.page_update_center, icon_path=resource_path(os.path.join("assets", "icons", "update.png"))) # Cần icon update.png

        self.page_report_settings = QWidget() # Was page_about
        create_report_settings_tab_content(self) # Gọi hàm từ module mới
        self._add_navigation_item("Báo Cáo & Cài đặt", self.page_report_settings, icon_path=resource_path(os.path.join("assets", "icons", "report.png")))

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

        self.main_content_layout.addWidget(global_buttons_frame) # Add to main content layout

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
        # Set icon size for the list widget items
        icon_dimension = int(self.nav_list_widget.fontMetrics().height() * 1.2) # Calculate dimension as integer
        self.nav_list_widget.setIconSize(QSize(icon_dimension, icon_dimension)) # Create QSize object

    # def _create_dashboard_tab(self, parent_tab_widget): # Đã chuyển sang gui_dashboard_tab.py
    #     pass # Nội dung đã được chuyển

    # def _create_system_info_tab(self, parent_tab_widget): # Đã chuyển sang gui_system_info_tab.py
    #     pass

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

        # --- Content Splitter (Actions and Results side-by-side) ---
        content_splitter = QSplitter(Qt.Horizontal) # Sử dụng QSplitter
        tab_main_layout.addWidget(content_splitter)
        # content_layout = QHBoxLayout() # Layout ngang cho 2 cột nội dung # Bỏ QHBoxLayout
        # tab_main_layout.addLayout(content_layout) # Thêm content_layout vào tab_main_layout # Bỏ QHBoxLayout



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
        left_column_layout.addWidget(scroll_area_actions)
        # content_layout.addWidget(left_column_widget, 2) # Bỏ QHBoxLayout
        content_splitter.addWidget(left_column_widget) # Thêm vào QSplitter

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
        # content_layout.addWidget(results_container_widget, 3) # Bỏ QHBoxLayout
        content_splitter.addWidget(results_container_widget) # Thêm vào QSplitter
        content_splitter.setSizes([320, 430]) # Tăng kích thước cột trái

    def _create_optimize_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget)
        content_splitter_optimize = QSplitter(Qt.Horizontal) # Sử dụng QSplitter
        tab_main_layout.addWidget(content_splitter_optimize)


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

        # One-click Optimization Button
        self.button_one_click_optimize = QPushButton("🚀 Tối Ưu Hóa Toàn Diện (1-Click)")
        self.button_one_click_optimize.setFont(self.h2_font) # Font lớn hơn
        self.button_one_click_optimize.setObjectName("OneClickOptimizeButton") # Để styling riêng
        self.button_one_click_optimize.setToolTip("Chạy các tác vụ dọn dẹp, tối ưu cơ bản và sửa lỗi được đề xuất.")
        self.button_one_click_optimize.clicked.connect(self.on_one_click_optimize_clicked)
        self.optimize_actions_layout.addWidget(self.button_one_click_optimize)

        # Gaming Mode Button
        self.button_toggle_gaming_mode = QPushButton("🎮 Chế Độ Gaming: TẮT")
        self.button_toggle_gaming_mode.setCheckable(True)
        self.button_toggle_gaming_mode.setFont(self.h2_font)
        self.button_toggle_gaming_mode.setObjectName("GamingModeButton")
        self.button_toggle_gaming_mode.toggled.connect(self.on_toggle_gaming_mode_clicked)
        self.optimize_actions_layout.addWidget(self.button_toggle_gaming_mode)

        # Separator
        line_sep = QFrame()
        line_sep.setFrameShape(QFrame.HLine)
        line_sep.setFrameShadow(QFrame.Sunken)
        self.optimize_actions_layout.addWidget(line_sep)

        # Group: Dọn dẹp & Tối ưu
        group_cleanup = QGroupBox("Dọn dẹp & Tối ưu Cơ Bản")
        group_cleanup.setFont(self.h2_font)
        cleanup_layout = QVBoxLayout(group_cleanup)
        self._add_utility_button(cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, clear_temporary_files, "optimize_clear_temp"))
        self._add_utility_button(cleanup_layout, "Mở Resource Monitor", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, open_resource_monitor, "optimize_resmon"))
        self._add_utility_button(cleanup_layout, "Quản Lý Ứng Dụng Khởi Động", self.on_manage_startup_programs_clicked) # Sửa lại để gọi hàm riêng
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

        # Group: Quản lý Máy In
        group_printer_management = QGroupBox("Quản lý Máy In")
        group_printer_management.setFont(self.h2_font)
        printer_mgmt_layout = QVBoxLayout(group_printer_management)
        self._add_utility_button(printer_mgmt_layout, "Liệt kê Máy In", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, list_printers, "optimize_list_printers", needs_wmi=True, result_type="table"))
        self._add_utility_button(printer_mgmt_layout, "Gỡ Máy In Lỗi", self.run_remove_printer_qt)
        self._add_utility_button(printer_mgmt_layout, "Xóa Lệnh In (Tất cả)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, clear_print_queue, "optimize_clear_all_print_queues", needs_wmi=False)) # False for WMI as it restarts spooler
        self._add_utility_button(printer_mgmt_layout, "Xóa Lệnh In (Chọn Máy In)", self.run_clear_specific_print_queue_qt)
        self._add_utility_button(printer_mgmt_layout, "Fix Lỗi Máy In (Khởi động lại Spooler)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_optimize, restart_print_spooler_service, "optimize_restart_spooler", needs_wmi=False))
        self.optimize_actions_layout.addWidget(group_printer_management)

        self.optimize_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(optimize_actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions)
        # content_layout.addWidget(left_column_widget, 2) # Bỏ QHBoxLayout
        content_splitter_optimize.addWidget(left_column_widget) # Thêm vào QSplitter

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

        # Thêm các nút quản lý Startup (sẽ được ẩn/hiện)
        self.startup_manager_buttons_frame = QFrame()
        startup_buttons_layout = QHBoxLayout(self.startup_manager_buttons_frame)
        self.button_enable_startup_item = QPushButton("Bật mục chọn")
        self.button_enable_startup_item.clicked.connect(lambda: self.on_manage_selected_startup_item("enable"))
        self.button_disable_startup_item = QPushButton("Tắt mục chọn")
        self.button_disable_startup_item.clicked.connect(lambda: self.on_manage_selected_startup_item("disable"))
        startup_buttons_layout.addWidget(self.button_enable_startup_item)
        startup_buttons_layout.addWidget(self.button_disable_startup_item)
        # self.button_delete_startup_item = QPushButton("Xóa mục chọn") # Cân nhắc thêm nút xóa
        # startup_buttons_layout.addWidget(self.button_delete_startup_item)
        self.startup_manager_buttons_frame.setVisible(False) # Ban đầu ẩn
        self.optimize_results_main_layout.addWidget(self.startup_manager_buttons_frame)

        self.optimize_results_main_layout.addWidget(self.stacked_widget_results_optimize, 1)
        # content_layout.addWidget(results_container_widget, 3) # Bỏ QHBoxLayout
        content_splitter_optimize.addWidget(results_container_widget) # Thêm vào QSplitter
        content_splitter_optimize.setSizes([320, 430]) # Tăng kích thước cột trái

    def _create_network_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget)
        content_splitter_network = QSplitter(Qt.Horizontal) # Sử dụng QSplitter
        tab_main_layout.addWidget(content_splitter_network)

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
        # content_layout.addWidget(left_column_widget, 2) # Bỏ QHBoxLayout
        content_splitter_network.addWidget(left_column_widget) # Thêm vào QSplitter

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
        # content_layout.addWidget(results_container_widget, 3) # Bỏ QHBoxLayout
        content_splitter_network.addWidget(results_container_widget) # Thêm vào QSplitter
        content_splitter_network.setSizes([320, 430]) # Tăng kích thước cột trái

    # def _create_utilities_tab(self, parent_tab_widget): # Đã không còn sử dụng, có thể xóa
    #     pass

    def _create_update_center_tab(self, parent_tab_widget):
        tab_main_layout = QVBoxLayout(parent_tab_widget)
        tab_main_layout.setSpacing(15)
        tab_main_layout.setAlignment(Qt.AlignTop)

        # --- Windows Update Section ---
        group_windows_update = QGroupBox("Windows Update")
        group_windows_update.setFont(self.h2_font)
        wu_layout = QVBoxLayout(group_windows_update)
        
        self.label_windows_update_status = QLabel("Trạng thái Windows Update: Đang kiểm tra...")
        self.label_windows_update_status.setFont(self.body_font)
        wu_layout.addWidget(self.label_windows_update_status)

        btn_check_wu = QPushButton("Kiểm tra & Mở Windows Update")
        btn_check_wu.clicked.connect(self.on_check_windows_update_clicked)
        wu_layout.addWidget(btn_check_wu)
        tab_main_layout.addWidget(group_windows_update)

        # --- Winget Updates Section ---
        group_winget = QGroupBox("Cập nhật ứng dụng (Winget)")
        group_winget.setFont(self.h2_font)
        winget_layout = QVBoxLayout(group_winget)

        btn_list_winget = QPushButton("Liệt kê ứng dụng có thể cập nhật")
        btn_list_winget.clicked.connect(lambda: self._run_task_in_thread_qt(btn_list_winget, self.stacked_widget_results_update_center, list_upgradable_winget_packages, "update_winget_list", result_type="text")) # Hiển thị kết quả ở text_update_results_qt
        winget_layout.addWidget(btn_list_winget)

        btn_update_all_winget = QPushButton("Cập nhật tất cả ứng dụng qua Winget")
        btn_update_all_winget.clicked.connect(lambda: self._run_task_in_thread_qt(btn_update_all_winget, self.stacked_widget_results_update_center, update_all_winget_packages, "update_winget_all"))
        winget_layout.addWidget(btn_update_all_winget)
        tab_main_layout.addWidget(group_winget)

        # --- Defender Definitions Section ---
        group_defender = QGroupBox("Định nghĩa Virus (Windows Defender)")
        group_defender.setFont(self.h2_font)
        defender_layout = QVBoxLayout(group_defender)
        btn_update_defender = QPushButton("Cập nhật định nghĩa Virus")
        btn_update_defender.clicked.connect(lambda: self._run_task_in_thread_qt(btn_update_defender, self.stacked_widget_results_update_center, update_windows_defender_definitions, "update_defender_defs"))
        defender_layout.addWidget(btn_update_defender)
        tab_main_layout.addWidget(group_defender)

        # --- Results Display for Update Center ---
        self.stacked_widget_results_update_center = self._create_results_display_area("Kết quả Cập nhật", "text_update_results_qt", "table_update_results_qt")
        tab_main_layout.addWidget(self.stacked_widget_results_update_center, 1) # Cho phép mở rộng
    def _add_utility_button(self, layout, text, on_click_action, object_name=None):
        button = QPushButton(text)
        if object_name:
            button.setObjectName(object_name) # Use provided object_name for specific styling
        else:
            button.setObjectName("UtilityButton") # Default object_name for general utility button styling
        button.setFont(self.bold_body_font) # Sử dụng font bold_body_font
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, btn=button: on_click_action(btn)) # Pass button to action
        
        # Cho phép nút tự động xuống dòng nếu text quá dài
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # Cho phép mở rộng ngang, giữ chiều cao ưu tiên
        button.setStyleSheet("QPushButton { white-space: normal; text-align: left; padding-left: 10px; padding-right: 10px; }") # CSS để text wrap và căn trái
        layout.addWidget(button)
        return button
    # def _create_fixes_tab(self, parent_tab_widget): # Đã không còn sử dụng hoặc chức năng đã được tích hợp vào tab Tối Ưu, có thể xóa
    #     pass

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
        elif current_page_widget == self.page_update_center: # Search for Update Center
            self._filter_action_buttons(search_term, self.page_update_center.layout()) # Assuming buttons are directly in layout or in groups
            
            # Example: if system_info tab has a QTextEdit for detailed logs or similar
            # text_edit_system = self.page_system_info.findChild(QTextEdit, "SystemInfoTextDisplay")
            # if text_edit_system:
            #     self._perform_text_search(text_edit_system, search_term)

        # Add other pages if they need search functionality
    # def _create_report_settings_tab(self, parent_tab_widget): # Đã chuyển sang gui_report_settings_tab.py
    #     pass

    def _create_results_display_area(self, group_title, text_edit_object_name, table_widget_object_name):
        """Helper to create a QStackedWidget with a QTextEdit and QTableWidget for results."""
        stacked_widget = QStackedWidget()

        # Page 0: QTextEdit for general results
        results_group_text = QGroupBox(group_title)
        results_group_text.setFont(self.body_font)
        results_layout_inner_text = QVBoxLayout(results_group_text)
        text_edit_results = QTextEdit()
        text_edit_results.setReadOnly(True)
        text_edit_results.setFont(self.monospace_font)
        text_edit_results.setWordWrapMode(QTextOption.NoWrap)
        text_edit_results.setObjectName(text_edit_object_name)
        results_layout_inner_text.addWidget(text_edit_results)
        self._update_display_widget(text_edit_results, "Kết quả sẽ hiển thị ở đây.")
        stacked_widget.addWidget(results_group_text)

        # Page 1: QTableWidget for table results
        table_results = QTableWidget()
        self._setup_results_table(table_results) # Use common setup
        table_results.setObjectName(table_widget_object_name)
        stacked_widget.addWidget(table_results)

        return stacked_widget

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
            QMainWindow, QWidget#CentralWidget {{
                background-color: {WINDOW_BG};
                font-family: "{DEFAULT_FONT_FAMILY}"; /* Default font for the whole window */
                font-size: {BODY_FONT_SIZE}pt; /* Base font size for the application */
            }}
            QWidget {{ /* Apply default font to all child widgets */
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {BODY_FONT_SIZE}pt;
                color: {TEXT_COLOR_PRIMARY}; 
            }}
            QWidget#Sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {SIDEBAR_BG_START}, stop:1 {SIDEBAR_BG_END});
            }}
            QLabel#SidebarAppTitle {{
                color: white;
                font-size: {H1_FONT_SIZE + 2}pt; /* 24px in HTML */
                font-weight: bold;
                margin-bottom: 2px;
            }}
            QLabel#SidebarAppSubtitle {{
                color: {SIDEBAR_LOGO_SUBTITLE_COLOR};
                font-size: {BODY_FONT_SIZE -1}pt; /* 14px in HTML */
            }}
            QWidget#MainContentContainer {{
                background-color: {MAIN_CONTENT_BG};
            }}
            QWidget#PageHeader {{
                background-color: {HEADER_BG};
                border-radius: 16px;
                /* Add box-shadow effect here if possible, or use QGraphicsDropShadowEffect */
            }}
            QGroupBox {{
                background-color: {GROUPBOX_BG}; /* Background for groupbox */
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Giữ lại viền nhẹ cho GroupBox để phân tách */
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
                border-radius: 4px; /* Bo góc cho tiêu đề GroupBox */
                color: {ACCENT_COLOR}; /* Color for groupbox title */
                /* font-family, font-size, font-weight for GroupBox titles are set by self.h2_font in Python */
                /* e.g., group_user_info.setFont(self.h2_font) */
            }}
            QLabel {{
                padding: 3px;
                background-color: transparent; /* Ensure labels don't have own background unless intended */
            }}
            QLabel#PageTitleLabel {{
                font-size: {H1_FONT_SIZE + 6}pt; /* 28px in HTML */
                font-weight: bold;
                color: {HEADER_TEXT_COLOR};
            }}
            QLabel#HealthScoreLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SECONDARY_COLOR}, stop:1 #059669); /* Green gradient */
                color: white;
                padding: 8px 15px; /* 12px 20px in HTML */
                border-radius: 15px; /* 25px in HTML, adjust for Qt */
                font-weight: bold;
            }}
            QPushButton {{
                /* Default button style - will be overridden by specific objectNames or classes */
                background-color: {BUTTON_SECONDARY_BG}; 
                color: {TEXT_COLOR_PRIMARY};
                border: 1px solid transparent; /* Viền trong suốt để giữ kích thước, nhưng không hiển thị */
                border-radius: 6px; /* Increased border radius */
                padding: 8px 15px; /* Increased padding */
                min-height: 20px; /* Minimum height */
                /* font-family and font-size are inherited from QWidget or set by self.default_font */
            }} 
            QPushButton:hover {{
                background-color: {BUTTON_SECONDARY_HOVER};
                /* border-color: {ACCENT_COLOR_HOVER}; */ /* Bỏ thay đổi màu viền khi hover nếu không muốn */
            }} # type: ignore
            QPushButton:pressed {{
                background-color: {BUTTON_SECONDARY_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: #E0E0E0; /* Lighter grey for disabled */
                color: #A0A0A0; /* Lighter text for disabled */ 
                border: 1px solid transparent; /* Viền trong suốt */
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {INPUT_BG};
                border: 1px solid {INPUT_BORDER_COLOR}; /* Viền nhẹ cho input fields để dễ nhìn */
                border-radius: 5px; /* Moderate border radius */
                padding: 6px; /* Increased padding */
                color: {TEXT_COLOR_PRIMARY};
                /* font-family and font-size are inherited or set by specific QFont in code */
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 1px solid {ACCENT_COLOR}; /* Viền cam khi focus */
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
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho pane */
                background: {FRAME_BG};
                border-radius: 8px; /* Bo góc cho toàn bộ pane */
                /* border-top: none; */ /* Nếu muốn tab liền với pane */
            }}
            QTabBar::tab {{
                background: {TAB_BG_INACTIVE};
                color: {TAB_TEXT_INACTIVE}; 
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho tab */
                border-bottom: none; /* Bỏ viền dưới của tab không được chọn */
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 15px; /* Adjusted padding for tabs */
                margin-right: 2px; /* Spacing between tabs */
                /* font is set by self.notebook.setFont(self.bold_font) */
            }} 
            QTabBar::tab:selected {{
                background: {TAB_BG_ACTIVE}; /* Active tab background same as pane */
                color: {TAB_TEXT_ACTIVE};
                border-color: {BORDER_COLOR_LIGHT}; /* Màu viền giống pane */
                /* border-bottom: 1px solid {TAB_BG_ACTIVE}; */ /* Bỏ viền dưới của tab được chọn để liền với pane */
            }}
            QListWidget#NavList {{
                background-color: {WINDOW_BG}; /* Match window background or a slightly different shade */
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho NavList */
                padding: 0px 10px; /* Horizontal padding for items within list */
                outline: 0; /* Remove focus outline if not desired */
                border: none; /* No border for the list widget itself, sidebar handles bg */
                background-color: transparent;
            }}
            QListWidget#NavList::item {{
                padding: 12px 15px; /* 15px 20px in HTML */
                border-radius: 10px; /* 12px in HTML */
                color: {SIDEBAR_TEXT_COLOR};
                font-weight: 500; /* medium */
                margin: 5px 0; /* Vertical margin between items */

            }}
            QListWidget#NavList::item:selected {{
                background-color: {SIDEBAR_TEXT_ACTIVE_BG};
                color: {SIDEBAR_TEXT_ACTIVE_COLOR};
                /* transform: translateX(5px); -> Not directly possible in QSS, might need custom delegate or item widget */
            }}
            QListWidget#NavList::item:hover {{
                background-color: {SIDEBAR_TEXT_HOVER_BG};
                color: {SIDEBAR_TEXT_ACTIVE_COLOR};
            }}
            QListWidget#NavList::item:selected:hover {{
                background-color: {SIDEBAR_TEXT_ACTIVE_BG}; /* Keep active style on hover */
            }}
            /* Icon styling for NavList items */
            QListWidget#NavList::item QLabel {{ /* If icons are QLabels inside items */
                /* color: {SIDEBAR_TEXT_COLOR}; */ /* Or specific icon color */
            }}
            QListWidget#NavList::item:selected QLabel {{
                /* color: {SIDEBAR_TEXT_ACTIVE_COLOR}; */

            }}
            QTabBar::tab:!selected:hover {{
                background: {ACCENT_COLOR_HOVER}; /* Use accent color for hover on inactive tabs */
                color: white;
            }}
            QScrollArea {{
                background-color: transparent; /* Scroll area background should be transparent */
            }}
            QScrollArea#DashboardScrollArea {{
                 border: none;
            }}
            QSplitter::handle {{
                background-color: {BORDER_COLOR_LIGHT}; /* Make it a line */
                width: 1px; /* For vertical splitter */
                height: 1px; /* For horizontal splitter (if any) */
                border: none; /* No extra border on the handle itself */
            }}
            QSplitter::handle:hover {{ background-color: {BORDER_COLOR_DARK}; }}
            QScrollBar:vertical {{
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho scrollbar */
                background: {WINDOW_BG};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR_DARK};
                min-height: 20px;
                border-radius: 6px; /* Bo góc cho tay cầm scrollbar */
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
            /* Performance Card Styling */
            QFrame[cardType] {{ 
                background-color: {STAT_CARD_BG};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }}
            QFrame[cardType="cpu"] {{ border-top: 4px solid {PRIMARY_COLOR}; }}
            QFrame[cardType="ram"] {{ border-top: 4px solid {SECONDARY_COLOR}; }}
            QFrame[cardType="ssd"] {{ border-top: 4px solid {ACCENT_COLOR}; }}
            QFrame[cardType="gpu"] {{ border-top: 4px solid {PURPLE_COLOR}; }}

            QLabel[objectName$="Icon"] {{ 
                font-size: 20pt;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
                border-radius: 24px; /* Circle */
                color: white;
                qproperty-alignment: 'AlignCenter';
            }}
            QLabel#cpuIcon {{ background-color: {PRIMARY_COLOR}; }}
            QLabel#ramIcon {{ background-color: {SECONDARY_COLOR}; }}
            QLabel#ssdIcon {{ background-color: {ACCENT_COLOR}; }}
            QLabel#gpuIcon {{ background-color: {PURPLE_COLOR}; }}

            QLabel[objectName$="Title"] {{ 
                font-size: {BODY_FONT_SIZE + 2}pt;
                
                font-weight: 600;
                color: {TEXT_COLOR_PRIMARY};
            }} 
            QLabel[objectName$="Value"] {{ 
                font-size: {H1_FONT_SIZE + 12}pt; /* Large value */
                font-weight: bold;
                color: {TEXT_COLOR_PRIMARY};
                margin-top: 5px;
                margin-bottom: 0px;
            }} 
            QProgressBar[objectName$="Progress"] {{ 
                border: none;
                background-color: {INPUT_BG};
                height: 10px;
                border-radius: 5px;
                margin-top: 5px;
            }}
            QProgressBar[objectName$="Progress"]::chunk {{
                border-radius: 5px;
            }}
            QProgressBar#cpuProgress::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY_COLOR}, stop:1 #60a5fa); }}
            QProgressBar#ramProgress::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SECONDARY_COLOR}, stop:1 #34d399); }}
            QProgressBar#ssdProgress::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_COLOR}, stop:1 #fbbf24); }}
            QProgressBar#gpuProgress::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PURPLE_COLOR}, stop:1 #a78bfa); }}

            /* QuickActionButton Styling */
            QPushButton#ActionBtn {{
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                text-align: left;
                font-weight: 600;
            }}
            /* Dynamic background color for QuickActionButton based on btnColor property */
            QPushButton#ActionBtn[btnColor="#ff6b35"] {{ background-color: #ff6b35; }}
            QPushButton#ActionBtn[btnColor="#ff6b35"]:hover {{ background-color: #e55a2b; }}
            QPushButton#ActionBtn[btnColor="#e74c3c"] {{ background-color: #e74c3c; }}
            QPushButton#ActionBtn[btnColor="#e74c3c"]:hover {{ background-color: #d32f2f; }}
            QPushButton#ActionBtn[btnColor="#3498db"] {{ background-color: #3498db; }}
            QPushButton#ActionBtn[btnColor="#3498db"]:hover {{ background-color: #2980b9; }}
            QPushButton#ActionBtn[btnColor="#1abc9c"] {{ background-color: #1abc9c; }}
            QPushButton#ActionBtn[btnColor="#1abc9c"]:hover {{ background-color: #16a085; }}

            QLabel[objectName$="Details"] {{
                font-size: {BODY_FONT_SIZE -1}pt; /* 14px in HTML */
                color: {STAT_CARD_DETAILS_COLOR};
                margin-top: 8px;
            }}
            /* Styles for result display QTextEdit and QTableWidget widgets */
            QTextEdit#ResultTextEdit, QTextEdit#SecurityResultTextEdit, QTextEdit#OptimizeResultTextEdit, QTextEdit#NetworkResultTextEdit, QTextEdit#FixesResultTextEdit, QTextEdit#text_update_results_qt {{ 
                 font-family: "{MONOSPACE_FONT_FAMILY}";
                 font-size: {MONOSPACE_FONT_SIZE}pt;
                 background-color: #FAFAFA; /* Slightly different background for readability */
                 border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho ô text kết quả */
                 border-radius: 5px; /* Bo góc */
            }} 
            QTableWidget#ResultTableWidget {{ 
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {BODY_FONT_SIZE-1}pt; /* Slightly smaller for table data */
                alternate-background-color: #F5F5F5; /* Light grey for alternate rows */
                gridline-color: {BORDER_COLOR_LIGHT}; /* Đường lưới mờ */
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho bảng */
                border-radius: 5px; /* Bo góc */
            }}
            QTableWidget#ResultTableWidget::item:hover {{
                background-color: {ACCENT_COLOR_HOVER};
                color: white; 
            }}
            QHeaderView::section {{
                background-color: {FRAME_BG}; /* Nền header giống nền frame */
                padding: 4px;
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho header */
                font-weight: bold;
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
                color: {TEXT_COLOR_PRIMARY}; 
                border: 1px solid transparent; /* Viền trong suốt */
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
                border: 1px solid {INPUT_BORDER_COLOR}; /* Viền cho QLineEdit trong dialog DNS */
                border-radius: 4px;
                padding: 5px;
                color: {TEXT_COLOR_PRIMARY};
            }} 
            QDialog#SetDnsDialog QLineEdit:focus {{ 
                border: 1px solid {ACCENT_COLOR}; /* Viền cam khi focus */
            }} 
            QDialog#SetDnsDialog QPushButton {{ /* Buttons inside SetDnsDialog (from QDialogButtonBox) */ 
                background-color: {BUTTON_SECONDARY_BG};
                color: {BUTTON_SECONDARY_TEXT};
                border: 1px solid transparent; /* Viền trong suốt */
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
            QPushButton#NavToggleSidebarButton {{ 
                background-color: transparent;
                border: none; /* Nút toggle nav không có viền */
                padding: 5px; /* Adjust as needed */
            color: {SIDEBAR_TEXT_COLOR}; /* Icon/text color */
            }} 
            QPushButton#NavToggleSidebarButton:hover {{ 
                background-color: {BUTTON_SECONDARY_HOVER}; /* Light hover effect */
            }} 
            QLabel#AppTitleLabel {{ 
                /* Style for app title if needed, e.g., color, padding */
            }} 
            QPushButton#OneClickOptimizeButton {{ 
                background-color: {ACCENT_COLOR};
                color: white;
                padding: 10px 18px; /* Lớn hơn một chút */
                border-radius: 6px; /* Bo góc */
                font-weight: bold;
            }} 
            QPushButton#OneClickOptimizeButton:hover {{ background-color: {ACCENT_COLOR_HOVER}; }} 
            QPushButton#GamingModeButton {{ 
                background-color: {BUTTON_SECONDARY_BG};
                color: {TEXT_COLOR_PRIMARY};
                border-radius: 6px; /* Bo góc */
            }} 
            QPushButton#GamingModeButton:checked {{ 
                background-color: {SECONDARY_COLOR}; /* Green when ON */
                color: white;
                border-radius: 6px; /* Bo góc */
                font-weight: bold;
            }} 
            QPushButton#GamingModeButton:hover {{ background-color: {BUTTON_SECONDARY_HOVER}; }} 
            QPushButton#GamingModeButton:checked:hover {{ background-color: {BUTTON_EXPORT_HOVER}; }} 
            /* Quick Actions Styling */
            QWidget#QuickActionsWidget {{ 
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }} 
            QLabel#QuickActionsTitle {{ 
                font-size: 16px;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }} 
        """) # type: ignore
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
                background-color: {FRAME_BG}; /* Nền trắng cho card */
                border: 1px solid {BORDER_COLOR_LIGHT}; /* Viền nhẹ cho card */
                border-radius: 8px; /* Giữ lại bo góc cho nền */
                margin-top: 15px; /* Điều chỉnh margin top cho card */
                padding: 5px 5px 8px 5px;    /* Điều chỉnh padding (top, right, bottom, left) */
                border-top: none; /* Remove generic top border for InfoCard if specific ones are not used */ /* This rule is for InfoCard, not DashboardStatCard */
            }}
            QGroupBox#ResultsDisplayGroup {{ /* Đã có từ yêu cầu trước, đảm bảo nó không bị ảnh hưởng */
                border: 5px;
                margin-top: 5px;
                padding: 0px; /* This rule is for ResultsDisplayGroup */
            }}
            QProgressBar, QProgressBar[objectName$="Progress"] {{
                border: 1px solid {BORDER_COLOR_DARK}; /* Viền nhẹ cho ProgressBar */
                border-radius: 5px;
                text-align: center; /* Center the percentage text */
                background-color: {INPUT_BG}; /* Background of the unfilled part */
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_COLOR}; /* Default color of the filled part */
                border-radius: 4px; /* Slightly smaller radius for the chunk */
                /* width: 10px; */ /* Optional: if you want a segmented look */
            }}
            /* QProgressBar#cpuProgress::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #1d4ed8); }} */ /* These are now handled by QFrame[cardType] */
            QProgressBar#ramProgress::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669); }}
            QProgressBar#ramProgress::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669); }}
            QProgressBar#ssdProgress::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706); }}
            QProgressBar#gpuProgress::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed); }}
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

        if target_parent_is_visible: # Chỉ hiển thị toast nếu parent dự kiến của nó đang hiển thị
            self.toast_notifier.show_toast(message, parent_widget=parent_for_toast, toast_type=status_type)


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
        if current_page == self.page_dashboard and hasattr(self, 'cpu_card'): # Ensure cards are initialized
            self.cpu_card.update_value("...")
            self.cpu_card.update_progress(0) # Reset progress bar

            self.cpu_card.update_details("Đang tải...")
            self.ram_card.update_value("...")
            self.ram_card.update_progress(0)

            self.ram_card.update_details("Đang tải...")
            self.ssd_card.update_value("...")
            self.ssd_card.update_progress(0)

            self.ssd_card.update_details("Đang tải...")
            self.gpu_card.update_value("...")
            self.gpu_card.update_progress(0)
            self.gpu_card.update_details("Đang tải...")
            # Reset health score
            self.health_score_label.setText("🎯 Điểm Sức Khỏe: --/100")
            self.health_score_label.setToolTip("")
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
        # Dừng timer cập nhật liên tục khi bắt đầu fetch thông tin mới
        if self.realtime_update_timer.isActive():
            self.realtime_update_timer.stop()

        # Pass the refresh button to the thread
        thread = WorkerThread(get_detailed_system_information, "fetch_pc_info", needs_wmi=False,
                                button_to_manage=self.button_refresh_dashboard_qt,
                                original_button_text=self.button_refresh_dashboard_qt.text())
        thread.task_completed.connect(self._on_fetch_pc_info_completed)
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        self._update_status_bar("Đang lấy thông tin hệ thống...", "info")
        
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
            screen_data = sys_info_dict.get("Màn hình", []) # This is a list of dicts
            temps_data = self.pc_info_dict.get("SystemCheckUtilities", {}).get("SystemTemperatures", {})

            # Calculate System Health Score
            health_score_info = calculate_system_health_score(self.pc_info_dict)

            # --- Cập nhật thông tin tĩnh trên Dashboard Tab ---
            if hasattr(self, 'cpu_card'):
                # CPU
                cpu_info = pc_data.get("CPU", {})
                cpu_model = cpu_info.get("Kiểu máy", NOT_AVAILABLE)
                self.cpu_card.update_details(f"{html.escape(str(cpu_model))}")
                
                # RAM
                ram_info = pc_data.get("RAM", {})
                ram_total_str = pc_data.get("Bộ nhớ RAM", NOT_AVAILABLE) # Lấy từ cấp PC cho tổng RAM
                ram_used_gb = ram_info.get("Đã sử dụng (GB)", "N/A")

                self.ram_card.update_details(f"Đã dùng: {html.escape(str(ram_used_gb))} GB / {html.escape(str(ram_total_str))}")

                # SSD
                # # SSD/Disk (Example: first physical disk, or C: partition if available)
                disks_info_list = pc_data.get("Ổ đĩa", [])
                disk_partitions_usage = self.pc_info_dict.get("SystemCheckUtilities", {}).get("Dung lượng ổ đĩa", [])
                os_disk_model = NOT_AVAILABLE
                os_disk_capacity_gb = NOT_AVAILABLE

                if disk_partitions_usage and isinstance(disk_partitions_usage, list):
                    for part in disk_partitions_usage:
                        if part.get("Tên ổ đĩa") == "C:":
                            os_disk_capacity_gb = part.get('Tổng (GB)', NOT_AVAILABLE)
                            
                            break 
                if disks_info_list and isinstance(disks_info_list, list) and isinstance(disks_info_list[0], dict):
                    first_disk = disks_info_list[0]
                    os_disk_model = first_disk.get('Kiểu máy', NOT_AVAILABLE)
                    # If C: partition data was not found, try to get total capacity from the first disk
                    if self._is_value_unavailable(os_disk_capacity_gb):
                        os_disk_capacity_gb = first_disk.get('Dung lượng (GB)', NOT_AVAILABLE)
                        self.ssd_card.update_details(f"Tổng: {html.escape(str(os_disk_capacity_gb))} GB ({html.escape(str(os_disk_model))})")
                # GPU
                gpus = pc_data.get("Card đồ họa (GPU)", [])
                if gpus and isinstance(gpus, list) and isinstance(gpus[0], dict):
                    first_gpu = gpus[0]
                    gpu_name = first_gpu.get("Tên", NOT_AVAILABLE)
                    self.gpu_card.update_details(f"{html.escape(str(gpu_name))}") # Only set the name/model here
                else:
                    self.gpu_card.update_details(f"{NOT_AVAILABLE}")
                # Update System Health Score on Dashboard
                score_val = health_score_info.get('score', 'N/A')
                self.health_score_label.setText(f"🎯 Điểm Sức Khỏe: <b>{score_val}</b>/100")
                issues_list = health_score_info.get('issues', [])
                if issues_list:
                    self.health_score_label.setToolTip("Các vấn đề ảnh hưởng điểm:\n- " + "\n- ".join(issues_list))
                else:
                    self.health_score_label.setToolTip("Không có vấn đề nghiêm trọng nào được phát hiện.")
                # Bắt đầu timer cập nhật liên tục sau khi thông tin tĩnh đã được tải
                self._start_realtime_update_timer()

            # --- Update System Info Tab (Cards) ---
            if hasattr(self, 'card_general_info'): # Check if system info tab elements exist
                # Sử dụng QTimer.singleShot để cập nhật từng card một cách trì hoãn
                QTimer.singleShot(0, lambda d=pc_data: self._populate_card(self.card_general_info, d, [("Tên máy tính", "Tên PC"), ("Loại máy", "Loại Máy"), ("Địa chỉ IP", "IP"), ("Địa chỉ MAC", "MAC")]))
                QTimer.singleShot(0, lambda d=pc_data: self._populate_card(self.card_os_info, d, [("Hệ điều hành", "HĐH"), ("Phiên bản Windows", "Phiên Bản"), ("Trạng thái kích hoạt Windows", "Kích hoạt")]))
                QTimer.singleShot(0, lambda d=pc_data.get("CPU", {}): self._populate_card(self.card_cpu_info, d, [("Kiểu máy", "Model"), ("Số lõi", "Lõi"), ("Số luồng", "Luồng")])) # Removed "Tốc độ cơ bản" as it's not always available or accurate
                
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
                # Populate Temperatures Card on System Info Tab
                def update_temps_card_deferred():
                    temp_lines_for_card = []
                    for comp_name, comp_data in temps_data.items():
                        temp_lines_for_card.append(f"<b>{html.escape(comp_name)}:</b> {html.escape(str(comp_data.get('value', 'N/A')))}{comp_data.get('unit', '°C')}")
                    self._update_display_widget(self.card_temperatures_info.findChild(QLabel), "<br>".join(temp_lines_for_card) if temp_lines_for_card else "Không có dữ liệu nhiệt độ.")
                QTimer.singleShot(0, update_temps_card_deferred)
            
            
            # Kích hoạt nút "Xuất Báo Cáo PC" nếu đang ở tab Báo cáo & Cài đặt
            if self.pages_stack.currentWidget() == self.page_report_settings:
                self.button_save_active_tab_result.setEnabled(True)
            elif self.pages_stack.currentWidget() == self.page_dashboard: # Kích hoạt nút làm mới dashboard
                self.button_refresh_dashboard_qt.setEnabled(True)
                # Update Windows Update status on Update Center tab if it's already created
            if hasattr(self, 'label_windows_update_status'):
                 # This would ideally be a separate call, but for now, piggyback on pc_info
                self.on_check_windows_update_clicked(fetch_only=True) # Call to update status

        
    def _on_task_error(self, task_name, error_message):
        logging.error(f"Error in task '{task_name}': {error_message}")
        is_fetch_pc_info = task_name == "fetch_pc_info"
        is_utility_task = task_name.startswith("utility_")
        is_fix_task = task_name.startswith("fix_")
        is_dashboard_task = task_name.startswith("dashboard_")
        if is_fetch_pc_info:
            # Dừng timer cập nhật liên tục khi có lỗi fetch thông tin chính
            if self.realtime_update_timer.isActive():
                self.realtime_update_timer.stop()
            self.pc_info_dict = None
            error_text_html = html.escape(f"Lỗi: {error_message}").replace("\n", "<br>")
            if hasattr(self, 'cpu_card'): # Dashboard elements
                self.cpu_card.update_value("Lỗi")
                self.cpu_card.update_progress(0)
                self.cpu_card.update_details("Lỗi lấy thông tin CPU")
                # ... (tương tự cho RAM, SSD, GPU)
                self.health_score_label.setText("🎯 Điểm Sức Khỏe: Lỗi")
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
        elif is_utility_task or is_fix_task or is_dashboard_task: # Gộp logic lỗi cho các tab tiện ích/fix/dashboard quick actions
            target_stacked_widget = None
            if task_name.startswith("security_") and hasattr(self, 'stacked_widget_results_security'):
                target_stacked_widget = self.stacked_widget_results_security
            elif task_name.startswith("optimize_") and hasattr(self, 'stacked_widget_results_optimize'):
                target_stacked_widget = self.stacked_widget_results_optimize
            elif task_name.startswith("network_") and hasattr(self, 'stacked_widget_results_network'):
                target_stacked_widget = self.stacked_widget_results_network
            elif task_name.startswith("update_") and hasattr(self, 'stacked_widget_results_update_center'):
                target_stacked_widget = self.stacked_widget_results_update_center
            elif is_dashboard_task: # For quick actions on dashboard, show toast only
                self._update_status_bar(f"Lỗi tác vụ nhanh: {error_message[:100]}...", "error")
                return # Don't try to update a stacked widget
            
            # Add other task prefixes and their corresponding stacked_widgets here

            if target_stacked_widget:
                target_stacked_widget.setCurrentIndex(0) # Show QTextEdit for errors
                text_edit_target = target_stacked_widget.widget(0).findChild(QTextEdit)
                # Ensure the text_edit_target is actually a QTextEdit before calling _update_display_widget
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
        
        if target_stacked_widget: # Only interact with target_stacked_widget if it's provided
            # Determine which QTextEdit to update for "Đang thực hiện..."
            # This assumes the QTextEdit is always at index 0 of the QGroupBox in the QStackedWidget's page 0
            text_display_for_loading = target_stacked_widget.widget(0).findChild(QTextEdit)
            if text_display_for_loading:
                self._update_display_widget(text_display_for_loading, html.escape(f"Đang thực hiện: {task_function.__name__}..."))
            target_stacked_widget.setCurrentIndex(0) # Show text display during loading

            # Explicitly clear highlights. Check if text_display_for_loading is not None before using.
            # Also, ensure it's a QTextEdit.
            if text_display_for_loading and isinstance(text_display_for_loading, QTextEdit):
                self._clear_text_highlights(text_display_for_loading)

            current_page_widget = self.pages_stack.currentWidget()
            # Check if the current page is one of the new tabs that have savable results
            if current_page_widget in [self.page_security, self.page_optimize, self.page_network, self.page_update_center]:
                self.button_save_active_tab_result.setEnabled(False)
        
        self._update_status_bar(f"Đang thực hiện: {task_function.__name__}...", "info")

        # Clear previous search in the target_widget before running a new task
        # Clear the global search bar
        if hasattr(self, 'global_search_input'):
            self.global_search_input.clear() # Clearing will trigger empty search/filter via _perform_global_search



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
        if target_stacked_widget: # Only if we have a target display
            if result_type == "table" and isinstance(data, list) and data and isinstance(data[0], dict):
                table_widget_target = target_stacked_widget.widget(1) # Assuming table is at index 1
                if isinstance(table_widget_target, QTableWidget):
                    self._populate_table_widget(table_widget_target, data)
                    target_stacked_widget.setCurrentIndex(1) # Switch to table view
                else: # Fallback to text if widget at index 1 is not a table
                    result_type = "text" # Force text display
            
            if result_type == "text": # This will also be the fallback if table logic fails
                if task_name.startswith("utility_disk_speed_test_run_disk_speed_test"): # Example specific toast
                    self.toast_notifier.show_toast("Kiểm tra tốc độ ổ cứng hoàn tất.", parent_widget=self, toast_type='success')
                
                text_edit_target = target_stacked_widget.widget(0).findChild(QTextEdit) # TextEdit is in a QGroupBox
                if text_edit_target:
                    display_text = self._format_task_result_for_display_generic(data)
                    self._update_display_widget(text_edit_target, display_text)
                target_stacked_widget.setCurrentIndex(0) # Switch to text view
            self._update_save_button_state_for_tab_content(target_stacked_widget)
        
        self._update_status_bar(f"Hoàn thành tác vụ: {task_name.split('_')[1] if '_' in task_name else task_name}", "success")
    
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
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_network, 
                                        lookup_dns_address, "utility_resolve_domain_ip", # This task_name_prefix needs to match the tab
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
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_network, set_dns_servers, "network_set_dns", needs_wmi=True, task_args=[primary_dns, secondary_dns])
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
        # Update page title label
        nav_item = self.nav_list_widget.item(index)
        self.page_title_label.setText(nav_item.data(Qt.UserRole) or nav_item.text()) # Use stored full text or current text


        # Show/hide global search bar based on the current tab
       
        if current_page_widget in [self.page_security, self.page_optimize, self.page_network, self.page_system_info]:
            self.global_search_input.setVisible(True)
            self.global_search_input.clear() # Clear search when tab changes
        else:
            self.global_search_input.setVisible(False)

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
        if hasattr(self, 'stacked_widget_results_update_center'):
            text_edit_update = self.stacked_widget_results_update_center.widget(0).findChild(QTextEdit)
            if text_edit_update: self._clear_text_highlights(text_edit_update)
        
        
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
            if hasattr(self, 'icon_expand_nav') and hasattr(self, 'button_toggle_nav_sidebar'):
                self.button_toggle_nav_sidebar.setIcon(self.icon_expand_nav)
                self.button_toggle_nav_sidebar.setText("") # Icon only
                self.button_toggle_nav_sidebar.setToolTip("Mở rộng menu")
                self.button_toggle_nav_sidebar.setIconSize(QSize(24,24))
        else:
            if hasattr(self, 'icon_collapse_nav') and hasattr(self, 'button_toggle_nav_sidebar'):
                self.button_toggle_nav_sidebar.setIcon(self.icon_collapse_nav)
                self.button_toggle_nav_sidebar.setText(" Thu gọn menu") # Icon and text
                self.button_toggle_nav_sidebar.setToolTip("Thu gọn menu")
                self.button_toggle_nav_sidebar.setIconSize(QSize(20,20))

    def _toggle_nav_panel_visibility(self):
        self.nav_panel_is_collapsed = not self.nav_panel_is_collapsed

        if self.nav_panel_is_collapsed:
            self.sidebar_widget.setFixedWidth(self.NAV_COLLAPSED_WIDTH)
            for i in range(self.nav_list_widget.count()):
                item = self.nav_list_widget.item(i)
                if item:
                    # Store original text if not already stored or if it's different
                    if item.data(Qt.UserRole) is None or item.data(Qt.UserRole) != item.text():
                         item.setData(Qt.UserRole, item.text())
                    item.setText("") # Clear text to show only icon for list items
            self.app_title_label_sidebar.setVisible(False)
            self.app_subtitle_label_sidebar.setVisible(False)
        else:
            self.sidebar_widget.setFixedWidth(self.NAV_EXPANDED_WIDTH)
            for i in range(self.nav_list_widget.count()):
                item = self.nav_list_widget.item(i)
                if item:
                    original_text = item.data(Qt.UserRole)
                    if original_text is not None:
                        item.setText(original_text) # Restore text

        self.app_title_label_sidebar.setVisible(True)
        self.app_subtitle_label_sidebar.setVisible(True)
        # QSplitter is no longer used for main layout, fixed width is set directly.
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
        elif current_page_widget == self.page_update_center:
            self.button_save_active_tab_result.setText("Lưu Kết Quả Cập Nhật")
            self._update_save_button_state_for_tab_content(self.stacked_widget_results_update_center)
        
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
        elif current_page_widget == self.page_security:
            self._save_generic_tab_result(self.stacked_widget_results_security, "KetQua_BaoMat")
        elif current_page_widget == self.page_optimize:
            self._save_generic_tab_result(self.stacked_widget_results_optimize, "KetQua_ToiUu")
        elif current_page_widget == self.page_network:
            self._save_generic_tab_result(self.stacked_widget_results_network, "KetQua_Mang")
        elif current_page_widget == self.page_update_center:
            self._save_generic_tab_result(self.stacked_widget_results_update_center, "KetQua_CapNhat")
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
            # --- New Slot Methods for New Features ---
    def on_one_click_optimize_clicked(self):
        reply = QMessageBox.question(self, "Xác nhận Tối ưu hóa",
                                     "Bạn có chắc muốn chạy tối ưu hóa toàn diện?\n"
                                     "Các tác vụ bao gồm: Xóa file tạm, xóa cache DNS, và có thể đề xuất tối ưu services, dọn dẹp registry (sẽ hỏi lại).",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # This will be a complex task, potentially running multiple sub-tasks
            # For now, let's assume a single core function `run_one_click_optimization` handles this
            # and reports progress/results.
            # from core.pc_info_functions import run_one_click_optimization # Placeholder
            # self._run_task_in_thread_qt(self.button_one_click_optimize, self.stacked_widget_results_optimize,
            #                             run_one_click_optimization, "optimize_one_click")
            self._update_display_widget(self.stacked_widget_results_optimize.widget(0).findChild(QTextEdit),
                                        html.escape("Chức năng Tối ưu hóa 1-Click đang được phát triển.\n"
                                                    "Nó sẽ bao gồm:\n"
                                                    "- Xóa file tạm (clear_temporary_files)\n"
                                                    "- Xóa DNS cache (flush_dns_cache)\n"
                                                    "- Tùy chọn: Tối ưu services (optimize_windows_services)\n"
                                                    "- Tùy chọn: Dọn dẹp registry (clean_registry_with_backup)"))
            self._update_status_bar("Tối ưu hóa 1-Click (Demo)", "info")

    def on_toggle_gaming_mode_clicked(self, checked):
        mode_text = "BẬT" if checked else "TẮT"
        self.button_toggle_gaming_mode.setText(f"🎮 Chế Độ Gaming: {mode_text}")
        # self._run_task_in_thread_qt(self.button_toggle_gaming_mode, self.stacked_widget_results_optimize,
        #                             apply_gaming_mode, f"optimize_gaming_mode_{mode_text.lower()}", task_args=[checked])
        self._update_display_widget(self.stacked_widget_results_optimize.widget(0).findChild(QTextEdit),
                                    html.escape(f"Chế độ Gaming đã được chuyển sang {mode_text}.\n"
                                                "Chức năng này đang được phát triển và sẽ bao gồm các tối ưu như:\n"
                                                "- Thay đổi kế hoạch nguồn (Power Plan)\n"
                                                "- Tạm dừng các dịch vụ không cần thiết (cần xác định danh sách an toàn)\n"
                                                "- Các tinh chỉnh khác để ưu tiên hiệu năng cho game."))
        self._update_status_bar(f"Chế độ Gaming: {mode_text}", "info")

    def on_manage_startup_programs_clicked(self, button_clicked):
        # Khi nhấn nút "Quản Lý Ứng Dụng Khởi Động"
        self.startup_manager_buttons_frame.setVisible(True) # Hiện các nút Bật/Tắt
        self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_optimize,
                                    get_startup_programs, "optimize_startup_list",
                                    needs_wmi=True, result_type="table")

    def on_manage_selected_startup_item(self, action): # action: "enable", "disable", "delete"
        current_table = self.stacked_widget_results_optimize.widget(1)
        if not isinstance(current_table, QTableWidget) or self.stacked_widget_results_optimize.currentIndex() != 1:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy bảng quản lý khởi động hoặc bảng không được hiển thị.")
            return

        selected_items = current_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một mục trong danh sách khởi động.")
            return

        # Giả sử cột đầu tiên (index 0) là tên chương trình hoặc một định danh duy nhất
        # Và cần thêm thông tin về 'path' hoặc 'key' để hàm core xử lý
        # Hàm get_startup_programs cần trả về đủ thông tin này.
        # Đây là ví dụ, bạn cần điều chỉnh dựa trên dữ liệu thực tế từ get_startup_programs
        selected_row = selected_items[0].row()
        item_name = current_table.item(selected_row, 0).text() # Giả sử cột 0 là tên
        # item_path_or_key = current_table.item(selected_row, X).text() # Cần cột chứa path/key

        # Placeholder: Cần hàm core `manage_startup_item(name, path_or_key, action)`
        # self._run_task_in_thread_qt(self.sender(), self.stacked_widget_results_optimize,
        #                             manage_startup_item, f"optimize_startup_{action}_{item_name}",
        #                             task_args=[item_name, item_path_or_key, action])
        QMessageBox.information(self, "Đang phát triển",
                                f"Chức năng '{action}' cho mục '{item_name}' đang được phát triển.\n"
                                "Sẽ cần quyền Administrator để thay đổi cài đặt khởi động.")
        # Sau khi hoàn thành, nên làm mới danh sách:
        # self.on_manage_startup_programs_clicked(self.sender()) # Hoặc nút gốc đã gọi

    def on_check_windows_update_clicked(self, checked=False, fetch_only=False): # Thêm fetch_only
        if not fetch_only:
            try:
                import webbrowser
                webbrowser.open("ms-settings:windowsupdate")
            except Exception as e:
                logging.error(f"Không thể mở cài đặt Windows Update: {e}")
                QMessageBox.warning(self, "Lỗi", f"Không thể mở cài đặt Windows Update tự động.\nVui lòng mở thủ công: Settings > Update & Security > Windows Update.\nLỗi: {e}")

        # Lấy và hiển thị trạng thái (ngay cả khi chỉ fetch_only)
        # Giả sử get_windows_update_status trả về một dict {'status': 'Up to date', 'last_checked': '...'}
        # Cần một WorkerThread để không block GUI nếu get_windows_update_status chậm
        thread_wu_status = WorkerThread(get_windows_update_status, "update_wu_status_check")
        def _on_wu_status_complete(task_name, data):
            if task_name == "update_wu_status_check" and hasattr(self, 'label_windows_update_status'):
                status_text = data.get('status', 'Không xác định')
                last_checked = data.get('last_checked', 'N/A')
                self.label_windows_update_status.setText(f"Trạng thái Windows Update: {status_text} (Kiểm tra lần cuối: {last_checked})")
        def _on_wu_status_error(task_name, error_msg):
             if hasattr(self, 'label_windows_update_status'):
                self.label_windows_update_status.setText(f"Trạng thái Windows Update: Lỗi khi kiểm tra ({error_msg[:50]}...)")
        thread_wu_status.task_completed.connect(_on_wu_status_complete)
        thread_wu_status.task_error.connect(_on_wu_status_error)
        self.threads.append(thread_wu_status)
        thread_wu_status.start()

    def run_remove_printer_qt(self, button_clicked):
        printer_name, ok = QInputDialog.getText(self, "Gỡ Máy In", "Nhập tên chính xác của máy in cần gỡ:")
        if ok and printer_name.strip():
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_optimize,
                                        remove_printer, "optimize_remove_printer",
                                        needs_wmi=True, task_args=[printer_name.strip()])
        elif ok:
            QMessageBox.warning(self, "Tên trống", "Bạn chưa nhập tên máy in.")

    def run_clear_specific_print_queue_qt(self, button_clicked):
        # Lấy danh sách máy in để người dùng chọn (nếu có thể)
        # Hoặc đơn giản là yêu cầu nhập tên
        printer_name, ok = QInputDialog.getText(self, "Xóa Hàng Đợi In Cụ Thể",
                                                "Nhập tên máy in để xóa hàng đợi (để trống sẽ không làm gì):")
        if ok and printer_name.strip():
            self._run_task_in_thread_qt(button_clicked, self.stacked_widget_results_optimize,
                                        clear_print_queue, "optimize_clear_specific_queue",
                                        needs_wmi=True, task_args=[printer_name.strip()])
        elif ok and not printer_name.strip():
            QMessageBox.information(self, "Thông báo", "Không có tên máy in nào được nhập.")
        # Nếu nhấn Cancel (ok=False), không làm gì cả

    # --- Dashboard Quick Action Handlers ---
    def on_dashboard_cleanup_system_clicked(self):
        # "Dọn Dẹp Hệ Thống" sẽ gọi hàm clear_temporary_files
        self._run_task_in_thread_qt(self.sender(),
                                    target_stacked_widget=self.stacked_widget_results_optimize, # Hiển thị kết quả trên tab Tối Ưu
                                    task_function=clear_temporary_files, 
                                    task_name_prefix="dashboard_cleanup", 
                                    needs_wmi=False)
    
    def on_copy_specs_clicked(self):
        # Placeholder for copy functionality
        QMessageBox.information(self, "Thông báo", "Chức năng 'Copy' thông số kỹ thuật đang được phát triển. (Dữ liệu sẽ được copy vào clipboard)")
        self._update_status_bar("Chức năng Copy đang phát triển", "info")

    def on_dashboard_boost_pc_clicked(self):
        # "Tăng Tốc PC" sẽ kích hoạt Power Plan 'High Performance'
        self._run_task_in_thread_qt(self.sender(),
                                    target_stacked_widget=self.stacked_widget_results_optimize, # Hiển thị kết quả trên tab Tối Ưu
                                    task_function=set_high_performance_power_plan, 
                                    task_name_prefix="dashboard_boost_pc", 
                                    needs_wmi=False)
    def on_dashboard_security_scan_clicked(self):
        # "Quét Bảo Mật" sẽ gọi hàm run_windows_defender_scan (QuickScan)
        self._run_task_in_thread_qt(self.sender(),
                                    target_stacked_widget=self.stacked_widget_results_security, # Hiển thị kết quả trên tab Bảo Mật
                                    task_function=run_windows_defender_scan, 
                                    task_name_prefix="dashboard_security_scan", 
                                    needs_wmi=False, task_args=["QuickScan"])

    def on_dashboard_update_drivers_clicked(self):
        # "Cập Nhật Driver" sẽ mở trang Windows Update
        try:
            import webbrowser
            webbrowser.open("ms-settings:windowsupdate")
            # Cập nhật status bar và hiển thị toast thành công
            self._update_status_bar("Đã mở cài đặt Windows Update để kiểm tra driver.", "success")
            self.toast_notifier.show_toast("Đã mở cài đặt Windows Update để kiểm tra driver.", parent_widget=self, toast_type='success')
        except Exception as e:
            logging.error(f"Không thể mở cài đặt Windows Update: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể mở cài đặt Windows Update tự động.\nVui lòng mở thủ công: Settings > Update & Security > Windows Update.\nLỗi: {e}")
            # Cập nhật status bar và hiển thị toast lỗi
            self._update_status_bar(f"Lỗi: Không thể mở cài đặt Windows Update tự động.", "error")
            self.toast_notifier.show_toast(f"Lỗi: Không thể mở cài đặt Windows Update tự động.", parent_widget=self, toast_type='error')
        # Nếu nhấn Cancel (ok=False), không làm gì cả
    def _start_realtime_update_timer(self):
        """Bắt đầu timer để cập nhật phần trăm sử dụng CPU, RAM, SSD, GPU liên tục."""
        # Đảm bảo timer không chạy nếu đã chạy
        if not self.realtime_update_timer.isActive():
            self.realtime_update_timer.start(2000) # Cập nhật mỗi 2 giây
            logging.info("Timer cập nhật phần trăm sử dụng thời gian thực đã bắt đầu.")

    def _update_realtime_usage(self):
        """Lấy và cập nhật phần trăm sử dụng CPU, RAM, SSD, GPU."""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking call
            self.cpu_card.update_value(f"{int(cpu_percent)}%")
            self.cpu_card.update_progress(int(cpu_percent))

            # RAM Usage
            ram_info = psutil.virtual_memory()
            ram_percent = ram_info.percent
            self.ram_card.update_value(f"{int(ram_percent)}%")
            self.ram_card.update_progress(int(ram_percent))

            # SSD Usage (for C: drive)
            # psutil.disk_usage('/') is for the root partition, which is C: on Windows
            disk_info = psutil.disk_usage('/')
            disk_percent = disk_info.percent
            self.ssd_card.update_value(f"{int(disk_percent)}%")
            self.ssd_card.update_progress(int(disk_percent))
            
            # GPU Usage (Real-time)
            gpu_realtime_data = get_gpu_realtime_usage()
            if gpu_realtime_data:
                gpu_load = gpu_realtime_data.get('load_percent', 0)
                mem_used = gpu_realtime_data.get('memory_used_mb', 0)
                mem_total = gpu_realtime_data.get('memory_total_mb', 0)
                
                self.gpu_card.update_value(f"{int(gpu_load)}%")
                self.gpu_card.update_progress(int(gpu_load))
                self.gpu_card.update_details(f"VRAM: {mem_used} MB / {mem_total} MB")
            else:
                # Fallback if real-time data is not available (e.g., non-NVIDIA GPU or pynvml not installed)
                self.gpu_card.update_value("N/A")
                self.gpu_card.update_progress(0)

        except Exception as e:
            logging.error(f"Lỗi khi cập nhật phần trăm sử dụng thời gian thực: {e}")
            # Dừng timer nếu có lỗi nghiêm trọng để tránh spam lỗi
            self.realtime_update_timer.stop()



# Khối main để chạy thử trực tiếp file này (nếu cần)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = PcInfoAppQt()
#     main_window.show()
#     sys.exit(app.exec_())