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
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QTabWidget,
    QGroupBox, QScrollArea, QMessageBox, QFileDialog, QGridLayout, QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextOption, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

import win32com.client # For CoInitialize/CoUninitialize in threads

# Import các hàm cần thiết từ core
# Đảm bảo rằng Python có thể tìm thấy các module này.
# Nếu chạy main.py từ thư mục gốc, sys.path đã được điều chỉnh.
from core.pc_info_functions import (
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
    flush_dns_cache           # Ví dụ: ipconfig /flushdns
)
from core.pc_info_manager import (
    validate_user_input, generate_filename, save_text_to_file,
    format_pc_info_to_string, format_system_details_to_string,
    format_user_info_for_display # Import hàm này
)

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants for UI Styling (Có thể dùng QSS sau) ---
DEFAULT_FONT_FAMILY = "Roboto"
DEFAULT_FONT_SIZE = 10 # Decreased font size
MONOSPACE_FONT_FAMILY = "Consolas"
MONOSPACE_FONT_SIZE = 9
HIGHLIGHT_COLOR = QColor(255, 236, 179) # Material Amber A100 (FFECB3) for text search

# New Color Palette (Material Design inspired)
WINDOW_BG = "#ECEFF1"        # Blue Grey 50 (Main background)
FRAME_BG = "#FFFFFF"         # White (For content containers like tab panes)
GROUPBOX_BG = "#FFFFFF"      # White (Background for GroupBoxes)
TEXT_COLOR_PRIMARY = "#263238" # Blue Grey 900 (Main text color)
TEXT_COLOR_SECONDARY = "#546E7A" # Blue Grey 600 (Secondary text, e.g., less important labels)
BORDER_COLOR_LIGHT = "#CFD8DC" # Blue Grey 100 (Light borders)
BORDER_COLOR_DARK = "#B0BEC5"  # Blue Grey 200 (Darker borders, scrollbar handles)
ACCENT_COLOR = "#03A9F4"     # Light Blue 500 (Primary accent for highlights, active states)
ACCENT_COLOR_HOVER = "#039BE5"  # Light Blue 600
ACCENT_COLOR_PRESSED = "#0288D1" # Light Blue 700

BUTTON_PRIMARY_BG = ACCENT_COLOR
BUTTON_PRIMARY_HOVER = ACCENT_COLOR_HOVER
BUTTON_PRIMARY_PRESSED = ACCENT_COLOR_PRESSED

BUTTON_SECONDARY_BG = "#CFD8DC" # Blue Grey 100
BUTTON_SECONDARY_HOVER = "#B0BEC5" # Blue Grey 200
BUTTON_SECONDARY_PRESSED = "#90A4AE" # Blue Grey 300
BUTTON_SECONDARY_TEXT = TEXT_COLOR_PRIMARY

BUTTON_EXPORT_BG = "#4CAF50"  # Green 500
BUTTON_EXPORT_HOVER = "#43A047" # Green 600
BUTTON_EXPORT_PRESSED = "#388E3C" # Green 700
BUTTON_DANGER_BG = "#F44336"  # Red 500
BUTTON_DANGER_HOVER = "#E53935" # Red 600

INPUT_BG = "#FFFFFF"         # Background for QLineEdit, QComboBox, etc.
INPUT_BORDER_COLOR = "#90A4AE" # Blue Grey 300 for input borders

TAB_BG_INACTIVE = "#B0BEC5" # Blue Grey 200
TAB_BG_ACTIVE = FRAME_BG    # White, same as pane
TAB_TEXT_INACTIVE = TEXT_COLOR_PRIMARY
TAB_TEXT_ACTIVE = ACCENT_COLOR

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

class PcInfoAppQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thông Tin Cấu Hình PC")
        self.setGeometry(100, 100, 950, 800) # Tăng kích thước một chút

        self.default_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
        self.bold_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, QFont.Bold)
        self.monospace_font = QFont(MONOSPACE_FONT_FAMILY, MONOSPACE_FONT_SIZE)

        # --- State Variables ---
        self.pc_info_dict = None
        # self.formatted_pc_info_string_home = "Chưa lấy thông tin." # No longer needed as we populate cards
        self.current_table_data = None # To store data for CSV export

        self.threads = [] # List để giữ các QThread đang chạy

        self._load_logo()
        self._init_timers() # Khởi tạo các QTimer cho debouncing
        self._create_widgets()
        self._apply_styles()

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

        # --- Top Frame for Logo and Title ---
        top_frame = QFrame()
        top_frame_layout = QVBoxLayout(top_frame) # This can remain QVBoxLayout if we only have one main row. Or change to QHBoxLayout if search is truly inline. Let's adjust header_row_layout.
        top_frame_layout.setContentsMargins(0,0,0,0)

        font_title = QFont(DEFAULT_FONT_FAMILY, 16, QFont.Bold)

        header_row_widget = QWidget() # Widget for the first row (greeting and logo)
        header_row_layout = QHBoxLayout(header_row_widget)
        header_row_layout.setContentsMargins(0,0,0,0)
        
        self.greeting_label = QLabel("Chào bạn!") # Default greeting
        self.greeting_label.setFont(font_title) # Sử dụng font của tiêu đề cũ
        self.greeting_label.setTextInteractionFlags(Qt.TextSelectableByMouse) # Cho phép copy
        header_row_layout.addWidget(self.greeting_label)
        header_row_layout.addStretch(1)
        # Global Search Bar will be moved to be alongside the TabWidget

        if self.logo_pixmap:
            self.logo_label = QLabel()
            self.logo_label.setPixmap(self.logo_pixmap)
            header_row_layout.addWidget(self.logo_label) # Logo is now at the end of this row
        top_frame_layout.addWidget(header_row_widget) # Add the (now populated) header row to the top frame

        self.main_layout.addWidget(top_frame) # Thêm top_frame vào main_layout

        # --- Global Search Input (khởi tạo một lần, sẽ được thêm vào layout của tab cụ thể) ---
        self.global_search_input = QLineEdit()
        self.global_search_input.setFont(self.default_font)
        self.global_search_input.setPlaceholderText("Tìm kiếm trong tab...")
        self.global_search_input.textChanged.connect(lambda: self.global_search_timer.start(300))
        self.global_search_input.hide() # Ẩn ban đầu

        # --- Notebook (QTabWidget) ---
        self.notebook = QTabWidget()
        self.notebook.setFont(self.bold_font)
        self.main_layout.addWidget(self.notebook)


        # --- Tab: Trang chủ ---
        self.tab_home = QWidget()
        self.notebook.addTab(self.tab_home, "Trang Chủ")
        self._create_home_tab(self.tab_home)

        # --- Tab: Tiện ích ---
        self.tab_utilities = QWidget()
        self.notebook.addTab(self.tab_utilities, "Tiện Ích")
        self._create_utilities_tab(self.tab_utilities)

        # --- Tab: Sửa lỗi hệ thống ---
        self.tab_fixes = QWidget()
        self.notebook.addTab(self.tab_fixes, "Fix Hệ Thống")
        self._create_fixes_tab(self.tab_fixes)

        # --- Tab: Thông tin hệ thống ---
        self.tab_about = QWidget()
        self.notebook.addTab(self.tab_about, "Thông Tin Hệ Thống")
        self._create_about_tab(self.tab_about)

        # Kết nối tín hiệu currentChanged SAU KHI tất cả các tab đã được tạo và gán thuộc tính
        self.notebook.currentChanged.connect(self._on_tab_changed_search_clear)

        # --- Global Buttons Frame ---
        global_buttons_frame = QFrame()
        global_buttons_layout = QHBoxLayout(global_buttons_frame)

        self.button_export_home = QPushButton("Xuất Báo Cáo PC")
        self.button_export_home.setFont(self.default_font)
        self.button_export_home.setFixedWidth(200)
        self.button_export_home.setCursor(Qt.PointingHandCursor)
        self.button_export_home.clicked.connect(self.on_export_info_qt)
        self.button_export_home.setEnabled(False)
        global_buttons_layout.addWidget(self.button_export_home)
        global_buttons_layout.addStretch(1)
        
        self.button_export_csv = QPushButton("Xuất CSV (Bảng)")
        self.button_export_csv.setFont(self.default_font)
        self.button_export_csv.setFixedWidth(150)
        self.button_export_csv.setCursor(Qt.PointingHandCursor)
        self.button_export_csv.clicked.connect(self.on_export_csv_qt)
        self.button_export_csv.setVisible(False) # Initially hidden
        global_buttons_layout.addWidget(self.button_export_csv)
        # global_buttons_layout.addStretch(1) # Removed to keep export buttons together

        self.button_exit = QPushButton("Thoát")
        self.button_exit.setFont(self.default_font)
        self.button_exit.setFixedWidth(150)
        self.button_exit.setCursor(Qt.PointingHandCursor)
        self.button_exit.clicked.connect(self.close)
        global_buttons_layout.addWidget(self.button_exit)

        self.main_layout.addWidget(global_buttons_frame)

    def _create_home_tab(self, parent_tab_widget):
        layout = QVBoxLayout(parent_tab_widget)
        layout.setSpacing(15)

        # --- User Info Frame (QGroupBox) ---
        group_user_info = QGroupBox("Thông tin người dùng (cho báo cáo)")
        group_user_info.setFont(self.bold_font)
        layout.addWidget(group_user_info)
        user_info_grid_layout = QGridLayout(group_user_info) # Đổi tên để rõ ràng hơn
        group_user_info.setObjectName("UserInfoGroup")

        # Dòng 1: Tên và Phòng Ban
        user_info_grid_layout.addWidget(QLabel("Tên:"), 0, 0)
        self.entry_name_qt = QLineEdit()
        self.entry_name_qt.setFont(self.default_font)
        user_info_grid_layout.addWidget(self.entry_name_qt, 0, 1)

        user_info_grid_layout.addWidget(QLabel("Phòng Ban:"), 0, 2)
        self.entry_department_qt = QLineEdit()
        self.entry_department_qt.setFont(self.default_font)
        user_info_grid_layout.addWidget(self.entry_department_qt, 0, 3) # Phòng ban ở cột 3

        # Dòng 1: Vị Trí Tầng (cột 0, 1) và ô nhập tầng tùy chỉnh (cột 2, 3 - sẽ được quản lý bởi on_floor_change_qt)
        # Đảm bảo label "Nhập vị trí hiện tại" dùng font mặc định
        user_info_grid_layout.addWidget(QLabel("Vị Trí:"), 1, 0) # Đổi tên label
        self.combo_floor_qt = QComboBox()
        self.combo_floor_qt.setFont(self.default_font)
        self.combo_floor_qt.addItems(["Tầng G", "Lầu 1", "Lầu 2", "Khác"])
        self.combo_floor_qt.currentIndexChanged.connect(self.on_floor_change_qt)
        user_info_grid_layout.addWidget(self.combo_floor_qt, 1, 1) # ComboBox ở cột 1

        self.entry_custom_floor_label_qt = QLabel("Vị trí khác:") # Đổi text 
        self.entry_custom_floor_label_qt.setFont(self.bold_font) # Đổi sang font in đậm
        self.entry_custom_floor_qt = QLineEdit()
        self.entry_custom_floor_qt.setFont(self.default_font)
        # Sẽ được thêm/xóa bởi on_floor_change_qt, không thêm vào layout cố định ở đây
        self.on_floor_change_qt() # Initial state

        # Dòng 2: Chức Vụ (cột 0,1) và Checkbox Ghi chú (cột 2)
        user_info_grid_layout.addWidget(QLabel("Chức Vụ:"), 2, 0) # Chức Vụ ở dòng 2, cột 0
        self.entry_position_qt = QLineEdit()
        self.entry_position_qt.setFont(self.default_font)
        user_info_grid_layout.addWidget(self.entry_position_qt, 2, 1) # Ô nhập Chức Vụ ở dòng 2, cột 1 (không kéo dài)

        self.checkbox_show_notes = QCheckBox("Ghi chú")
        self.checkbox_show_notes.setFont(self.default_font)
        self.checkbox_show_notes.toggled.connect(self.toggle_notes_visibility)
        user_info_grid_layout.addWidget(self.checkbox_show_notes, 2, 2, 1, 2) # Checkbox ở dòng 2, cột 2, kéo dài 2 cột còn lại


        # Dòng 3: Ghi chú (ẩn/hiện) - đã được dời xuống
        self.label_notes_qt = QLabel("Ghi chú:")
        self.label_notes_qt.setFont(self.default_font)
        self.text_notes_qt = QTextEdit()
        self.text_notes_qt.setFont(self.default_font)
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

        self.home_cards_layout.addWidget(self.card_general_info, 0, 0)
        self.home_cards_layout.addWidget(self.card_os_info, 0, 1)
        self.home_cards_layout.addWidget(self.card_cpu_info, 1, 0)
        self.home_cards_layout.addWidget(self.card_ram_info, 1, 1)
        self.home_cards_layout.addWidget(self.card_mainboard_info, 2, 0)
        self.home_cards_layout.addWidget(self.card_disks_info, 3, 0, 1, 2) # Span 2 columns for disks
        self.home_cards_layout.addWidget(self.card_gpus_info, 4, 0, 1, 2)   # Span 2 columns for GPUs
        self.home_cards_layout.addWidget(self.card_screens_info, 5, 0, 1, 2) # Span 2 columns for Screens

        cards_scroll_area.setWidget(cards_container_widget)
        layout.addWidget(cards_scroll_area, 1) # Add scroll area to the main tab layout

        # --- Button to refresh Home tab info ---
        self.button_refresh_home_qt = QPushButton("Làm mới Dữ liệu PC")
        self.button_refresh_home_qt.setFont(self.default_font)
        self.button_refresh_home_qt.setCursor(Qt.PointingHandCursor)
        self.button_refresh_home_qt.clicked.connect(self.fetch_pc_info_threaded)
        layout.addWidget(self.button_refresh_home_qt, 0, Qt.AlignCenter)

    def _create_info_card(self, title):
        card = QGroupBox(title)
        card.setFont(self.bold_font)
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

    def _create_utilities_tab(self, parent_tab_widget):
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
        actions_widget_container = QWidget() # Container cho layout các groupbox
        self.utilities_actions_layout = QVBoxLayout(actions_widget_container) # Store as instance member
        self.utilities_actions_layout.setSpacing(10) # Tăng khoảng cách giữa các GroupBox
        self.utilities_actions_layout.setAlignment(Qt.AlignTop) # Giữ các groupbox ở trên cùng

        # Group: Bảo mật & Virus
        group_security = QGroupBox("Bảo mật & Virus")
        group_security.setFont(self.bold_font)
        sec_layout = QVBoxLayout(group_security)
        self._add_utility_button(sec_layout, "Quét Virus Nhanh", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, run_windows_defender_scan, "utility_defender_quick_scan", needs_wmi=False, task_args=["QuickScan"]))
        self._add_utility_button(sec_layout, "Quét Virus Toàn Bộ", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, run_windows_defender_scan, "utility_defender_full_scan", needs_wmi=False, task_args=["FullScan"]))
        self._add_utility_button(sec_layout, "Cập Nhật Định Nghĩa Virus", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, update_windows_defender_definitions, "utility_defender_update", needs_wmi=False))
        self._add_utility_button(sec_layout, "Kiểm Tra Trạng Thái Tường Lửa", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_firewall_status, "utility_firewall_status", needs_wmi=False))
        self._add_utility_button(sec_layout, "Bật Tường Lửa (Tất cả Profile)", self.enable_firewall_qt, object_name="WarningButton") # Example of specific style
        self._add_utility_button(sec_layout, "Tắt Tường Lửa (Tất cả Profile)", self.disable_firewall_qt, object_name="DangerButton")
        self.utilities_actions_layout.addWidget(group_security)
        
        # Group: Thông tin & Chẩn đoán
        group_diag = QGroupBox("Thông tin & Chẩn đoán")
        group_diag.setFont(self.bold_font)
        diag_layout = QVBoxLayout(group_diag)
        self._add_utility_button(diag_layout, "Xem Dung Lượng Ổ Đĩa", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_disk_partitions_usage, "utility_disk_usage", needs_wmi=True, result_type="table"))
        self._add_utility_button(diag_layout, "Tạo Báo Cáo Pin (Laptop)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, generate_battery_report, "utility_battery_report", needs_wmi=False))
        self._add_utility_button(diag_layout, "Kiểm tra kích hoạt Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, check_windows_activation_status, "utility_win_activation", needs_wmi=False))
        self._add_utility_button(diag_layout, "Xem Event Log Gần Đây (24h)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_recent_event_logs, "utility_event_logs", needs_wmi=True, wmi_namespace="root\\CIMV2", task_args=[24, 25], result_type="table"))
        self._add_utility_button(diag_layout, "Kiểm Tra Phiên Bản Phần Mềm", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_installed_software_versions, "utility_software_versions_wmi", needs_wmi=True, result_type="table"))
        self._add_utility_button(diag_layout, "Ứng Dụng Người Dùng Đã Cài", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_installed_software_versions, "utility_software_versions_reg", needs_wmi=False, result_type="table"))
        self.utilities_actions_layout.addWidget(group_diag)
        
        # Group: Mạng
        group_network = QGroupBox("Mạng")
        group_network.setFont(self.bold_font)
        net_layout = QVBoxLayout(group_network)
        self._add_utility_button(net_layout, "Kiểm Tra Kết Nối Wifi", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_wifi_connection_info, "utility_wifi_info", needs_wmi=False))
        self._add_utility_button(net_layout, "Xem Cấu Hình Mạng Chi Tiết", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_network_configuration_details, "utility_network_config", needs_wmi=True, result_type="table"))
        self._add_utility_button(net_layout, "Ping Google", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, run_ping_test, "utility_ping_google", needs_wmi=False, task_args=["google.com", 4]))
        self._add_utility_button(net_layout, "Tra Cứu DNS Google", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, lookup_dns_address, "utility_dns_lookup", needs_wmi=False, task_args=["google.com"]))
        self._add_utility_button(net_layout, "Kết Nối Mạng Đang Hoạt Động", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_active_network_connections, "utility_active_connections", needs_wmi=False, result_type="table"))
        self._add_utility_button(net_layout, "Xóa Cache DNS", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, flush_dns_cache, "utility_flush_dns", needs_wmi=False))
        self.utilities_actions_layout.addWidget(group_network)
        
        self._add_utility_button(diag_layout, "Kiểm Tra Nhiệt Độ Hệ Thống", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_system_temperatures, "utility_temps", needs_wmi=True, wmi_namespace="root\\WMI", result_type="table"))
        self._add_utility_button(diag_layout, "Liệt Kê Tiến Trình Đang Chạy", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_utilities, get_running_processes, "utility_processes", needs_wmi=False, result_type="table"))
        
        self.utilities_actions_layout.addStretch(1) # Đẩy các group lên trên
        scroll_area_actions.setWidget(actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions) # Add scroll area below search bar
        content_layout.addWidget(left_column_widget, 1) # Tỷ lệ 1 cho cột trái

        # --- Right Column: Utilities Results Display ---
        results_container_widget = QWidget()
        self.utilities_results_main_layout = QVBoxLayout(results_container_widget) # Lưu layout này
        self.utilities_results_main_layout.setContentsMargins(0,0,0,0) # Remove margins for tighter fit

        # QStackedWidget for switching between QTextEdit and QTableWidget
        self.stacked_widget_results_utilities = QStackedWidget()
        
        # Page 0: QTextEdit for general results
        results_group = QGroupBox("Kết quả Tiện ích")
        results_group.setFont(self.bold_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_utilities_results_qt = QTextEdit()
        self.text_utilities_results_qt.setReadOnly(True)
        self.text_utilities_results_qt.setFont(self.monospace_font)
        self.text_utilities_results_qt.setWordWrapMode(QTextOption.NoWrap)
        self.text_utilities_results_qt.setObjectName("UtilitiesResultTextEdit")
        results_layout_inner.addWidget(self.text_utilities_results_qt)
        self._update_display_widget(self.text_utilities_results_qt, "Kết quả của tiện ích sẽ hiển thị ở đây.")
        self.stacked_widget_results_utilities.addWidget(results_group) # Add QGroupBox containing QTextEdit

        # Page 1: QTableWidget for table results
        self.table_utilities_results_qt = QTableWidget()
        self.table_utilities_results_qt.setFont(self.default_font)
        self.table_utilities_results_qt.setAlternatingRowColors(True)
        self.table_utilities_results_qt.setSortingEnabled(True)
        self.table_utilities_results_qt.horizontalHeader().setStretchLastSection(True)
        self.table_utilities_results_qt.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only
        self.table_utilities_results_qt.setObjectName("ResultTableWidget")
        self.stacked_widget_results_utilities.addWidget(self.table_utilities_results_qt)

        self.utilities_results_main_layout.addWidget(self.stacked_widget_results_utilities, 1)

        # Buttons dưới ô kết quả
        utils_buttons_frame = QFrame()
        utils_buttons_layout_inner = QHBoxLayout(utils_buttons_frame) # Layout nội bộ cho các nút
        utils_buttons_layout_inner.addStretch(1) # Đẩy nút Lưu sang phải
        self.button_save_utility_result_qt = QPushButton("Lưu Kết Quả")
        self._style_save_button(self.button_save_utility_result_qt, lambda: self.save_tab_result_qt(self.stacked_widget_results_utilities, "KetQua_TienIch"))
        utils_buttons_layout_inner.addWidget(self.button_save_utility_result_qt)
        self.utilities_results_main_layout.addWidget(utils_buttons_frame)

        content_layout.addWidget(results_container_widget, 2) # Tỷ lệ 2 cho cột phải

    def _add_utility_button(self, layout, text, on_click_action, object_name=None):
        button = QPushButton(text)
        if object_name:
            button.setObjectName(object_name) # Use provided object_name for specific styling
        else:
            button.setObjectName("UtilityButton") # Default object_name for general utility button styling
        button.setFont(self.default_font)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, btn=button: on_click_action(btn)) # Pass button to action
        layout.addWidget(button)
        return button

    def _create_fixes_tab(self, parent_tab_widget):
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
        group_optimize_cleanup.setFont(self.bold_font)
        optimize_cleanup_layout = QVBoxLayout(group_optimize_cleanup)
        self._add_utility_button(optimize_cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, clear_temporary_files, "fix_clear_temp", needs_wmi=False))
        self._add_utility_button(optimize_cleanup_layout, "Mở Resource Monitor", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, open_resource_monitor, "fix_resmon", needs_wmi=False))
        self._add_utility_button(optimize_cleanup_layout, "Quản Lý Khởi Động Cùng Windows", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, get_startup_programs, "fix_startup_programs", needs_wmi=True, result_type="table"))
        self.fixes_actions_layout.addWidget(group_optimize_cleanup)

        # Group 2: Sửa lỗi & Cập nhật Hệ thống
        group_fix_update = QGroupBox("Sửa lỗi & Cập nhật Hệ thống")
        group_fix_update.setFont(self.bold_font)
        fix_update_layout = QVBoxLayout(group_fix_update)
        self._add_utility_button(fix_update_layout, "Reset Kết Nối Internet", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, reset_internet_connection, "fix_reset_net", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Chạy SFC Scan", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, run_sfc_scan, "fix_sfc_scan", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Tạo Điểm Khôi Phục Hệ Thống", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, create_system_restore_point, "fix_create_restore_point", needs_wmi=False))
        self._add_utility_button(fix_update_layout, "Cập Nhật Phần Mềm (Winget)", lambda btn: self._run_task_in_thread_qt(btn, self.stacked_widget_results_fixes, update_all_winget_packages, "fix_winget_update", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_fix_update)

        self.fixes_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(actions_widget_container)
        left_column_layout_fixes.addWidget(scroll_area_actions) # Add scroll area below search bar
        content_layout_fixes.addWidget(left_column_widget_fixes, 1) # Tỷ lệ 1 cho cột trái


        # Right Column: Fixes Results Display
        results_container_widget = QWidget()
        self.fixes_results_main_layout = QVBoxLayout(results_container_widget) # Lưu layout này
        self.fixes_results_main_layout.setContentsMargins(0,0,0,0)

        self.stacked_widget_results_fixes = QStackedWidget()

        # Page 0 for Fixes Tab: QTextEdit
        results_group = QGroupBox("Kết quả Tác vụ Sửa lỗi")
        results_group.setFont(self.bold_font)
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
        self.table_fixes_results_qt.setFont(self.default_font)
        self.table_fixes_results_qt.setAlternatingRowColors(True)
        self.table_fixes_results_qt.setSortingEnabled(True)
        self.table_fixes_results_qt.horizontalHeader().setStretchLastSection(True)
        self.table_fixes_results_qt.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_fixes_results_qt.setObjectName("ResultTableWidget")
        self.stacked_widget_results_fixes.addWidget(self.table_fixes_results_qt)

        self.fixes_results_main_layout.addWidget(self.stacked_widget_results_fixes, 1)
        
        # Frame cho nút lưu kết quả ở tab Fixes
        fixes_buttons_frame = QFrame()
        fixes_buttons_layout_inner = QHBoxLayout(fixes_buttons_frame) # Layout nội bộ cho các nút
        fixes_buttons_layout_inner.addStretch(1) # Đẩy nút Lưu sang phải
        self.button_save_fix_result_qt = QPushButton("Lưu Kết Quả Sửa Lỗi")
        self._style_save_button(self.button_save_fix_result_qt, lambda: self.save_tab_result_qt(self.stacked_widget_results_fixes, "KetQua_SuaLoi"))
        fixes_buttons_layout_inner.addWidget(self.button_save_fix_result_qt)
        self.fixes_results_main_layout.addWidget(fixes_buttons_frame)

        content_layout_fixes.addWidget(results_container_widget, 2) # Tỷ lệ 2 cho cột phải

    def _perform_global_search(self):
        """Thực hiện tìm kiếm/lọc dựa trên tab hiện tại và nội dung của global_search_input."""
        if not hasattr(self, 'global_search_input'):
            return
        search_term = self.global_search_input.text()
        current_widget = self.notebook.currentWidget()

        if current_widget == self.tab_utilities:
            if hasattr(self, 'utilities_actions_layout'):
                self._filter_action_buttons(search_term, self.utilities_actions_layout)
            if hasattr(self, 'stacked_widget_results_utilities') and self.stacked_widget_results_utilities.widget(0).findChild(QTextEdit):
                self._perform_text_search(self.stacked_widget_results_utilities.widget(0).findChild(QTextEdit), search_term)
        elif current_widget == self.tab_fixes:
            if hasattr(self, 'fixes_actions_layout'):
                self._filter_action_buttons(search_term, self.fixes_actions_layout)
            if hasattr(self, 'stacked_widget_results_fixes') and self.stacked_widget_results_fixes.widget(0).findChild(QTextEdit):
                self._perform_text_search(self.stacked_widget_results_fixes.widget(0).findChild(QTextEdit), search_term)
        # Thêm các tab khác nếu cần tìm kiếm


    def _create_about_tab(self, parent_tab_widget):
        layout = QVBoxLayout(parent_tab_widget)
        layout.setContentsMargins(20, 20, 20, 20) # Thêm padding cho dễ nhìn
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_content_widget)
        scroll_layout.setAlignment(Qt.AlignTop)

        # --- Tiêu đề ứng dụng ---
        title_label = QLabel("Công Cụ Hỗ Trợ PC")
        title_font = QFont(DEFAULT_FONT_FAMILY, 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse) # Cho phép copy
        title_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title_label)

        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Phiên bản:", "1.0.0 (Qt)"))
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Người sáng lập:", "HPC"))
        scroll_layout.addWidget(self._create_info_section_qt(scroll_content_widget, "Liên hệ:", "support@hpc.vn"))
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
        section_group.setFont(self.bold_font)
        section_layout = QVBoxLayout(section_group)

        content_label = QLabel()
        content_label.setFont(self.default_font)
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
                font-size: {DEFAULT_FONT_SIZE}pt;
            }}
            QWidget {{ /* Apply default font to all child widgets */
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {DEFAULT_FONT_SIZE}pt;
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
                /* font-weight: bold; -- Will be set by self.bold_font in Python for specific QGroupBox titles */
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
            QTabBar::tab:!selected:hover {{
                background: {ACCENT_COLOR_HOVER}; /* Use accent color for hover on inactive tabs */
                color: white;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent; /* Scroll area background should be transparent */
            }}
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
            QTextEdit#ResultTextEdit, QTextEdit#UtilitiesResultTextEdit, QTextEdit#FixesResultTextEdit {{
                 font-family: "{MONOSPACE_FONT_FAMILY}";
                 font-size: {MONOSPACE_FONT_SIZE}pt;
                 background-color: #FAFAFA; /* Slightly different background for readability */
                 border: 1px solid {BORDER_COLOR_LIGHT};
            }}
            QTableWidget#ResultTableWidget {{
                font-family: "{DEFAULT_FONT_FAMILY}";
                font-size: {DEFAULT_FONT_SIZE-1}pt; /* Slightly smaller for table data */
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
                font-weight: bold;
            }}
        """)

        # Specific button styles (override general QPushButton style)
        self.button_export_home.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_EXPORT_BG};
                color: white;
                border: none;
            }}
            QPushButton:hover {{ background-color: {BUTTON_EXPORT_HOVER}; }}
            QPushButton:pressed {{ background-color: {BUTTON_EXPORT_PRESSED}; }}
        """)
        self.button_exit.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_DANGER_BG};
                color: white;
                border: none;
            }}
            QPushButton:hover {{ background-color: {BUTTON_DANGER_HOVER}; }}
            QPushButton:pressed {{ background-color: {BUTTON_DANGER_BG}; }}
        """)
        self.button_export_csv.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_EXPORT_BG};
                color: white;
                border: none;
            }}
            QPushButton:hover {{ background-color: {BUTTON_EXPORT_HOVER}; }}
            QPushButton:pressed {{ background-color: {BUTTON_EXPORT_PRESSED}; }}
        """)

        # Style for "Refresh" button on Home tab
        if hasattr(self, 'button_refresh_home_qt'):
            self.button_refresh_home_qt.setStyleSheet(f"""
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
                background-color: #B0BEC5; /* Blue Grey 200 for disabled save */
                color: #CFD8DC; /* Blue Grey 100 for disabled text */
                border: none;
            }}
        """
        if hasattr(self, 'button_save_utility_result_qt'):
            self.button_save_utility_result_qt.setStyleSheet(common_save_button_style)
        if hasattr(self, 'button_save_fix_result_qt'):
            self.button_save_fix_result_qt.setStyleSheet(common_save_button_style)
        
        # Style for InfoCards on Home tab
        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#InfoCard {{
                border: 1px solid {BORDER_COLOR_DARK}; /* Darker border for cards */
            }}""")

    def _update_display_widget(self, text_widget, content, is_error=False):
        # content is now assumed to be an HTML string, or plain text that needs escaping by the caller.
        # For plain text messages passed directly (e.g. "Đang tải..."), they should be escaped by the caller.
        # For content generated by _format_task_result_for_display_generic or _populate_card, it's already HTML.
        text_widget.clear()

        final_html_content = content # Assume content is already HTML or properly escaped plain text formatted as HTML

        # Determine text color based on is_error flag or keywords in the content.
        # The keyword check should be cautious if 'Lỗi' can be part of a non-error label.
        # The is_error flag is the most reliable way to indicate an error.
        text_color_to_use = DEFAULT_TEXT_COLOR_HTML
        if is_error:
            text_color_to_use = ERROR_TEXT_COLOR_HTML
        elif isinstance(content, str) and any(err_keyword in content for err_keyword in ["Lỗi", "Error", "Không thể"]):
             # Check if it's not part of a bold tag like "<b>Lỗi:</b>"
            if not any(f"<b>{err_keyword}</b>" in content for err_keyword in ["Lỗi", "Error", "Không thể"]):
                text_color_to_use = ERROR_TEXT_COLOR_HTML

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
                group_box.setVisible(group_should_be_visible)

    def _toggle_buttons_qt(self, enable_refresh_home=True, enable_export_home=False,
                        enable_save_utility=False, enable_save_fix=False):
        self.button_refresh_home_qt.setEnabled(enable_refresh_home)
        self.button_export_home.setEnabled(enable_export_home and self.pc_info_dict is not None)
        if hasattr(self, 'button_save_utility_result_qt'):
            self.button_save_utility_result_qt.setEnabled(enable_save_utility)
        if hasattr(self, 'button_save_fix_result_qt'):
            self.button_save_fix_result_qt.setEnabled(enable_save_fix)

    def fetch_pc_info_threaded(self):
        # Update placeholder text in cards
        card_widgets = [
            self.card_general_info, self.card_os_info, self.card_cpu_info,
            self.card_ram_info, self.card_mainboard_info, self.card_disks_info,
            self.card_gpus_info, self.card_screens_info
        ]
        for card in card_widgets:
            content_label = card.findChild(QLabel)
            if content_label:
                self._update_display_widget(content_label, html.escape("Đang tải..."))

        self._toggle_buttons_qt(enable_refresh_home=False, enable_export_home=False)

        # Pass the refresh button to the thread
        thread = WorkerThread(get_detailed_system_information, "fetch_pc_info", needs_wmi=False,
                                button_to_manage=self.button_refresh_home_qt,
                                original_button_text=self.button_refresh_home_qt.text())
        thread.task_completed.connect(self._on_fetch_pc_info_completed)
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        thread.start()

    def _populate_card(self, card_groupbox, data_dict, keys_map):
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
            sys_info = self.pc_info_dict.get("SystemInformation", {})
            pc_data = sys_info.get("PC", {})
            screen_data = sys_info.get("Màn hình", [])

            self._populate_card(self.card_general_info, pc_data, [("Tên máy tính", "Tên PC"), ("Loại máy", "Loại Máy"), ("Địa chỉ IP", "IP"), ("Địa chỉ MAC", "MAC")])
            self._populate_card(self.card_os_info, pc_data, [("Hệ điều hành", "HĐH"), ("Phiên bản Windows", "Phiên Bản")])
            self._populate_card(self.card_cpu_info, pc_data.get("CPU", {}), [("Kiểu máy", "Model"), ("Số lõi", "Lõi"), ("Số luồng", "Luồng")])
            self._populate_card(self.card_ram_info, {"Tổng RAM": pc_data.get("Bộ nhớ RAM", NOT_AVAILABLE)}, [("Tổng RAM", "Tổng RAM")])
            self._populate_card(self.card_mainboard_info, pc_data.get("Mainboard", {}), [("Nhà sản xuất", "NSX"), ("Kiểu máy", "Model"), ("Số Sê-ri", "Serial")])
            
            # For lists like disks, gpus, screens
            disk_keys_map = [("Kiểu máy", "Model"), ("Dung lượng (GB)", "Size"), ("Giao tiếp", "Interface"), ("Loại phương tiện", "Type")]
            self._populate_card(self.card_disks_info, pc_data.get("Ổ đĩa", []), disk_keys_map)
            gpu_keys_map = [("Tên", "Tên"), ("Nhà sản xuất", "NSX"), ("Tổng bộ nhớ (MB)", "VRAM"), ("Độ phân giải hiện tại", "Res")]
            self._populate_card(self.card_gpus_info, pc_data.get("Card đồ họa (GPU)", []), gpu_keys_map)
            screen_keys_map = [("Tên", "Tên"), ("Độ phân giải", "Res"), ("Trạng thái", "Status")]
            self._populate_card(self.card_screens_info, screen_data, screen_keys_map)
            
            # Update greeting label with user name
            user_name = pc_data.get("User Name", NOT_AVAILABLE) # Corrected: use pc_data
            if user_name == NOT_AVAILABLE and "Tên máy tính" in pc_data: # Fallback for greeting
                user_name = pc_data.get("Tên máy tính", "Người dùng")
            self.greeting_label.setText(f"Chào bạn, {user_name}!")
            self._toggle_buttons_qt(enable_refresh_home=True, enable_export_home=True)
    def _on_task_error(self, task_name, error_message):
        logging.error(f"Error in task '{task_name}': {error_message}")
        is_fetch_pc_info = task_name == "fetch_pc_info"
        is_utility_task = task_name.startswith("utility_")
        is_fix_task = task_name.startswith("fix_")

        if is_fetch_pc_info:
            self.pc_info_dict = None
            error_text_for_cards = f"Lỗi: {error_message}"
            card_widgets = [self.card_general_info, self.card_os_info, self.card_cpu_info, self.card_ram_info, self.card_mainboard_info, self.card_disks_info, self.card_gpus_info, self.card_screens_info]
            for card in card_widgets:
                content_label = card.findChild(QLabel)
                if content_label:
                    self._update_display_widget(content_label, html.escape(error_text_for_cards).replace("\n", "<br>"), is_error=True)
            self._toggle_buttons_qt(enable_refresh_home=True, enable_export_home=False)
        elif is_utility_task:
            # Determine if the error should go to QTextEdit or QTableWidget (or just show in QTextEdit)
            self.stacked_widget_results_utilities.setCurrentIndex(0) # Show QTextEdit for errors
            text_edit_target = self.stacked_widget_results_utilities.widget(0).findChild(QTextEdit)
            self._update_display_widget(text_edit_target, html.escape(f"Lỗi khi thực hiện tác vụ:\n{error_message}").replace("\n", "<br>"), is_error=True)
            self._toggle_buttons_qt(enable_save_utility=True) # Vẫn cho phép lưu lỗi nếu muốn
        elif is_fix_task:
            self.stacked_widget_results_fixes.setCurrentIndex(0)
            text_edit_target = self.stacked_widget_results_fixes.widget(0).findChild(QTextEdit)
            self._update_display_widget(text_edit_target, html.escape(f"Lỗi khi thực hiện tác vụ:\n{error_message}").replace("\n", "<br>"), is_error=True)
            self._toggle_buttons_qt(enable_save_fix=True)
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
                                          f"và nhập: {network_instruction}")
        except ValueError as ve:
            QMessageBox.critical(self, "Thiếu thông tin", str(ve))
        except (IOError, RuntimeError) as save_e:
            QMessageBox.critical(self, "Lỗi Lưu File", f"Không thể lưu file:\n{save_e}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi xuất file: {e}")
            logging.exception("Lỗi không xác định khi xuất file:")

    def save_tab_result_qt(self, stacked_widget_results, default_prefix="KetQua"):
        current_widget = stacked_widget_results.currentWidget()
        content_to_save = ""

        if isinstance(current_widget, QGroupBox): # It's the QTextEdit page
            text_edit = current_widget.findChild(QTextEdit)
            if text_edit:
                content_to_save = text_edit.toPlainText().strip()
        elif isinstance(current_widget, QTableWidget): # It's the QTableWidget page
            # For now, let user know CSV export is separate or implement simple text dump
            # QMessageBox.information(self, "Lưu Kết Quả Bảng", "Để lưu dữ liệu bảng, vui lòng sử dụng nút 'Xuất CSV (Bảng)'.")
            # return
            # Or, create a simple text representation of the table:
            table_widget = current_widget
            content_to_save = self._get_table_content_as_text(table_widget)

        if not content_to_save or "Đang thực hiện:" in content_to_save or "Kết quả của tiện ích sẽ hiển thị ở đây." in content_to_save or "Chọn một tác vụ để thực hiện." in content_to_save :
            QMessageBox.warning(self, "Không có kết quả", "Không có kết quả để lưu hoặc tác vụ đang chạy.")
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
        except (IOError, RuntimeError) as save_e:
            QMessageBox.critical(self, "Lỗi Lưu File", f"Không thể lưu file kết quả:\n{save_e}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi Không Xác Định", f"Đã xảy ra lỗi không mong muốn khi lưu kết quả: {e}")
            logging.exception("Lỗi không xác định khi lưu kết quả tab:")

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
        table_to_export = None
        if current_tab_widget == self.tab_utilities and self.stacked_widget_results_utilities.currentIndex() == 1:
            table_to_export = self.table_utilities_results_qt
        elif current_tab_widget == self.tab_fixes and self.stacked_widget_results_fixes.currentIndex() == 1:
            table_to_export = self.table_fixes_results_qt

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
            except Exception as e:
                QMessageBox.critical(self, "Lỗi Xuất CSV", f"Không thể xuất CSV: {e}")
                logging.exception("Lỗi khi xuất CSV:")

    def _run_task_in_thread_qt(self, button_clicked, target_stacked_widget, task_function, task_name_prefix, needs_wmi=False, wmi_namespace="root\\CIMV2", task_args=None, result_type="text"):
        task_name = f"{task_name_prefix}_{task_function.__name__}_{datetime.now().strftime('%H%M%S%f')}" # Unique task name
        
        # Determine which QTextEdit to update for "Đang thực hiện..."
        # This assumes the QTextEdit is always at index 0 of the QGroupBox in the QStackedWidget's page 0
        text_display_for_loading = target_stacked_widget.widget(0).findChild(QTextEdit)
        if text_display_for_loading:
            self._update_display_widget(text_display_for_loading, html.escape(f"Đang thực hiện: {task_function.__name__}..."))
        target_stacked_widget.setCurrentIndex(0) # Show text display during loading

        # Clear previous search in the target_widget before running a new task
        # Clear the global search bar
        if hasattr(self, 'global_search_input'):
            self.global_search_input.clear() # Clearing will trigger empty search/filter via _perform_global_search

        # Explicitly clear highlights as clearing the search bar might not be enough if it was already empty
        if text_display_for_loading:
            self._clear_text_highlights(text_display_for_loading)

        is_utility_task = target_stacked_widget == self.stacked_widget_results_utilities
        is_fix_task = target_stacked_widget == self.stacked_widget_results_fixes

        if is_utility_task: self._toggle_buttons_qt(enable_save_utility=False); self.button_export_csv.setVisible(False)
        elif is_fix_task: self._toggle_buttons_qt(enable_save_fix=False); self.button_export_csv.setVisible(False)

        # Đảm bảo task_args là một tuple để unpack an toàn
        if task_args is None:
            actual_args_for_thread_tuple = tuple()
        elif isinstance(task_args, (list, tuple)):
            actual_args_for_thread_tuple = tuple(task_args)
        else: # Nếu task_args là một giá trị đơn lẻ, coi nó là một tuple một phần tử
            actual_args_for_thread_tuple = (task_args,)
            
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
                self.button_export_csv.setVisible(True)
            else: # Fallback to text if widget at index 1 is not a table
                result_type = "text" # Force text display
        
        if result_type == "text":
            text_edit_target = target_stacked_widget.widget(0).findChild(QTextEdit) # TextEdit is in a QGroupBox
            display_text = self._format_task_result_for_display_generic(data)
            self._update_display_widget(text_edit_target, display_text)
            target_stacked_widget.setCurrentIndex(0) # Switch to text view
            self.button_export_csv.setVisible(False)

        is_utility_task = target_stacked_widget == self.stacked_widget_results_utilities
        is_fix_task = target_stacked_widget == self.stacked_widget_results_fixes
        if is_utility_task: self._toggle_buttons_qt(enable_save_utility=True)
        elif is_fix_task: self._toggle_buttons_qt(enable_save_fix=True)

    def _format_task_result_for_display_generic(self, result_data):
        """Định dạng kết quả tác vụ thành chuỗi, sử dụng ** cho bold."""
        """Định dạng kết quả tác vụ thành chuỗi, sử dụng ** cho bold.
           Bỏ qua các giá trị không khả dụng hoặc rỗng. Output is HTML."""
        UNAVAILABLE_STR_CONSTANTS = [NOT_AVAILABLE, NOT_FOUND, ERROR_WMI_CONNECTION]

        def is_value_unavailable(val):
            if val is None:
                return True
            # Check if the value itself is one of the string constants
            if isinstance(val, str) and val in UNAVAILABLE_STR_CONSTANTS:
                return True
            # Check if the string representation, when stripped, is empty or an unavailable constant
            s_val = str(val).strip()
            if s_val == "" or s_val in UNAVAILABLE_STR_CONSTANTS:
                return True
            return False

        if is_value_unavailable(result_data):
            return html.escape(NOT_AVAILABLE) # Return escaped "Không khả dụng"

        html_lines = []
        if isinstance(result_data, list):
            if not result_data:
                return html.escape("Tác vụ hoàn thành, không có mục nào được trả về.")
            for item in result_data:
                if is_value_unavailable(item):
                    continue # Skip unavailable items in a list
                elif isinstance(item, dict):
                    item_lines = []
                    for k, v_raw in item.items():
                        if not is_value_unavailable(v_raw):
                            item_lines.append(f"  <b>{html.escape(str(k))}:</b> {html.escape(str(v_raw))}")
                    if item_lines: # Only add if there's something to show for this item
                        html_lines.append("<br>".join(item_lines))
                else:
                    html_lines.append(html.escape(str(item)))
            if not html_lines:
                return html.escape("Không có thông tin khả dụng.")
            return "<br>---<br>".join(html_lines)

        elif isinstance(result_data, dict):
            if not result_data:
                return html.escape("Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng).")
            
            if "message" in result_data and "status" in result_data: # Special status dict
                status_val = result_data.get('status', 'N/A')
                message_val = result_data['message']

                if not is_value_unavailable(status_val):
                    html_lines.append(f"<b>Trạng thái:</b> {html.escape(str(status_val))}")
                if not is_value_unavailable(message_val):
                    html_lines.append(f"<b>Thông điệp:</b> {html.escape(str(message_val))}")
                
                if "details" in result_data and not is_value_unavailable(result_data['details']):
                    details_content = result_data['details']
                    details_html_parts = ["<br><b>Chi tiết:</b>"] # Start with a line break if there are previous lines
                    has_details_to_show = False
                    if isinstance(details_content, dict):
                        for k_detail, v_detail_raw in details_content.items():
                            if not is_value_unavailable(v_detail_raw):
                                has_details_to_show = True
                                if k_detail == 'errors_list' and isinstance(v_detail_raw, list) and v_detail_raw:
                                    details_html_parts.append(f"  <b>Lỗi chi tiết:</b>")
                                    errors_shown_count = 0
                                    for err_item in v_detail_raw:
                                        if not is_value_unavailable(err_item) and errors_shown_count < 5:
                                            details_html_parts.append(f"    - {html.escape(str(err_item))}")
                                            errors_shown_count += 1
                                    if sum(1 for e_item in v_detail_raw if not is_value_unavailable(e_item)) > 5:
                                        details_html_parts.append("    ...")
                                elif k_detail in ['deleted_files_count', 'deleted_folders_count', 'total_size_freed_mb']:
                                    details_html_parts.append(f"  <b>{html.escape(str(k_detail.replace('_', ' ').capitalize()))}:</b> {html.escape(str(v_detail_raw))}")
                                else:
                                    details_html_parts.append(f"  <b>{html.escape(str(k_detail))}:</b> {html.escape(str(v_detail_raw))}")
                        if has_details_to_show: html_lines.append("<br>".join(details_html_parts))
                    elif isinstance(details_content, list): # if details is a list of strings
                        list_details_to_show = [f"  {d_item}" for d_item in details_content if not is_value_unavailable(d_item)]
                        if list_details_to_show:
                            details_str_list.extend(list_details_to_show)
                            lines.append("\n".join(details_str_list))
                    else: # Generic details string
                        details_str_list.append(f"  {details_content}")
                        html_lines.append("<br>".join(details_html_parts)) # Corrected variable
                
                if "path" in result_data and not is_value_unavailable(result_data['path']):
                    html_lines.append(f"<br><b>Đường dẫn file:</b> {html.escape(str(result_data['path']))}")
                if not html_lines: return html.escape(NOT_AVAILABLE)
                return "<br>".join(html_lines)
            else:
                for k, v_raw in result_data.items():
                    if not is_value_unavailable(v_raw):
                        html_lines.append(f"<b>{html.escape(str(k))}:</b> {html.escape(str(v_raw))}")
                if not html_lines: return html.escape(NOT_AVAILABLE)
                return "<br>".join(html_lines)
        else:
            # This case should have been caught by the initial is_value_unavailable(result_data)
            # but as a fallback, ensure we don't return the unavailable constant itself.
            return html.escape(str(result_data)) if not is_value_unavailable(result_data) else html.escape(NOT_AVAILABLE)

    def enable_firewall_qt(self):
        if QMessageBox.question(self, "Xác nhận Bật Tường lửa", "Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._run_task_in_thread_qt(self.sender(), self.stacked_widget_results_utilities, toggle_firewall, "utility_firewall_enable", needs_wmi=False, task_args=[True])

    def disable_firewall_qt(self):
        if QMessageBox.question(self, "XÁC NHẬN TẮT TƯỜNG LỬA", "CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._run_task_in_thread_qt(self.sender(), self.stacked_widget_results_utilities, toggle_firewall, "utility_firewall_disable", needs_wmi=False, task_args=[False])

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
        else:
            event.accept()
        # super().closeEvent(event) # Call super at the end if event is accepted.

    def _on_tab_changed_search_clear(self, index):
        """Clears search inputs and highlights when tab changes."""
        # Clear the global search input text
        self.global_search_input.clear() # Xóa text trước khi ẩn/hiện hoặc reparent

        # Detach search input from its current parent layout
        # This ensures it can be re-parented correctly.
        # Check if it has a parent and that parent has a layout
        current_search_parent = self.global_search_input.parentWidget()
        if current_search_parent and current_search_parent.layout():
            current_search_parent.layout().removeWidget(self.global_search_input)
        self.global_search_input.setParent(None) # Quan trọng để reparent đúng cách
        self.global_search_input.hide() # Ẩn theo mặc định khi chuyển tab

        current_tab_widget = self.notebook.widget(index)

        if current_tab_widget == self.tab_utilities and hasattr(self, 'utilities_results_main_layout'):
            # Insert search bar before the QStackedWidget in the results column
            self.utilities_results_main_layout.insertWidget(0, self.global_search_input)
            self.global_search_input.show()
        elif current_tab_widget == self.tab_fixes and hasattr(self, 'fixes_results_main_layout'):
            self.fixes_results_main_layout.insertWidget(0, self.global_search_input)
            self.global_search_input.show()
        # Add other tabs if they need the global search bar

        # Clear highlights in text display areas
        if hasattr(self, 'stacked_widget_results_utilities'):
            text_edit_utils = self.stacked_widget_results_utilities.widget(0).findChild(QTextEdit)
            if text_edit_utils: self._clear_text_highlights(text_edit_utils)
        if hasattr(self, 'stacked_widget_results_fixes'):
            text_edit_fixes = self.stacked_widget_results_fixes.widget(0).findChild(QTextEdit)
            if text_edit_fixes: self._clear_text_highlights(text_edit_fixes)
        card_widgets = [self.card_general_info, self.card_os_info, self.card_cpu_info, self.card_ram_info, self.card_mainboard_info, self.card_disks_info, self.card_gpus_info, self.card_screens_info]
        for card in card_widgets:
            content_label = card.findChild(QLabel)
            if content_label: # Assuming QLabel is used for card content
                # For QLabels, re-setting the HTML content without search term effectively clears highlights
                # This needs the original content to be stored or re-fetched if search was applied.
                # For simplicity, we assume search on home tab is not implemented yet or handled differently.
                pass # Placeholder for home tab card highlight clearing

        # Hide/Show CSV export button based on current view in the active tab
        self.button_export_csv.setVisible(False) # Default to hidden
        if current_tab_widget == self.tab_utilities and self.stacked_widget_results_utilities.currentIndex() == 1:
            self.button_export_csv.setVisible(True)
        elif current_tab_widget == self.tab_fixes and self.stacked_widget_results_fixes.currentIndex() == 1:
            self.button_export_csv.setVisible(True)

    def _style_save_button(self, button, on_click_action):
        button.setCursor(Qt.PointingHandCursor)
        button.setFont(self.default_font)
        button.setEnabled(False) # Initially disabled
        button.setObjectName("SaveResultButton") # For QSS styling
        button.clicked.connect(on_click_action)

# Khối main để chạy thử trực tiếp file này (nếu cần)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = PcInfoAppQt()
#     main_window.show()
#     sys.exit(app.exec_())