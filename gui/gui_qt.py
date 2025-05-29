## gui/gui_qt.py
# Tạo giao diện chính với PyQt5
import sys
import os
import logging
import html # Thêm import html để escape nội dung
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QTabWidget,
    QGroupBox, QScrollArea, QMessageBox, QFileDialog, QGridLayout, QFrame
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
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 10
MONOSPACE_FONT_FAMILY = "Consolas"
MONOSPACE_FONT_SIZE = 9
HIGHLIGHT_COLOR = QColor("yellow")
DEFAULT_TEXT_COLOR_HTML = "#333333"
ERROR_TEXT_COLOR_HTML = "red"

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
        self.wmi_namespace = wmi_namespace # Namespace WMI cần thiết cho tác vụ
        self.args = args
        self.kwargs = kwargs
        self.wmi_service_local = None
        self.com_initialized_local = False

    def run(self):
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
        self.formatted_pc_info_string_home = "Chưa lấy thông tin."

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
        self.search_home_results_timer = QTimer(self)
        self.search_home_results_timer.setSingleShot(True)
        self.search_home_results_timer.timeout.connect(lambda: self._perform_text_search(self.text_home_info_qt, self.search_home_results_input.text()))

        self.search_utilities_results_timer = QTimer(self)
        self.search_utilities_results_timer.setSingleShot(True)
        self.search_utilities_results_timer.timeout.connect(lambda: self._perform_text_search(self.text_utilities_results_qt, self.search_utilities_results_input.text()))

        self.search_fixes_results_timer = QTimer(self)
        self.search_fixes_results_timer.setSingleShot(True)
        self.search_fixes_results_timer.timeout.connect(lambda: self._perform_text_search(self.text_fixes_results_qt, self.search_fixes_results_input.text()))
        
        # Timer cho lọc actions sẽ được tạo trong các hàm _create_utilities_tab và _create_fixes_tab

    def _create_widgets(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Top Frame for Logo and Title ---
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0,0,0,0)

        self.app_title_label = QLabel("Công Cụ Hỗ Trợ PC")
        font_title = QFont(DEFAULT_FONT_FAMILY, 16, QFont.Bold)
        self.app_title_label.setFont(font_title)
        top_layout.addWidget(self.app_title_label)
        top_layout.addStretch(1)

        if self.logo_pixmap:
            self.logo_label = QLabel()
            self.logo_label.setPixmap(self.logo_pixmap)
            top_layout.addWidget(self.logo_label)

        self.main_layout.addWidget(top_frame)

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

        # --- Global Buttons Frame ---
        global_buttons_frame = QFrame()
        global_buttons_layout = QHBoxLayout(global_buttons_frame)

        self.button_export_home = QPushButton("Xuất Dữ liệu PC")
        self.button_export_home.setFont(self.default_font)
        self.button_export_home.setFixedWidth(200)
        self.button_export_home.setCursor(Qt.PointingHandCursor)
        self.button_export_home.clicked.connect(self.on_export_info_qt)
        self.button_export_home.setEnabled(False)
        global_buttons_layout.addWidget(self.button_export_home)
        global_buttons_layout.addStretch(1)

        self.button_exit = QPushButton("Thoát Ứng Dụng")
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
        group_user_info = QGroupBox("Thông tin người dùng (cho file xuất)")
        group_user_info.setFont(self.bold_font)
        layout.addWidget(group_user_info)
        user_info_form_layout = QGridLayout(group_user_info) # Sử dụng QGridLayout

        # Tên
        user_info_form_layout.addWidget(QLabel("Tên:"), 0, 0)
        self.entry_name_qt = QLineEdit()
        self.entry_name_qt.setFont(self.default_font)
        user_info_form_layout.addWidget(self.entry_name_qt, 0, 1, 1, 3) # row, col, rowspan, colspan

        # Phòng Ban
        user_info_form_layout.addWidget(QLabel("Phòng Ban:"), 1, 0)
        self.entry_department_qt = QLineEdit()
        self.entry_department_qt.setFont(self.default_font)
        user_info_form_layout.addWidget(self.entry_department_qt, 1, 1, 1, 3)

        # Vị Trí Tầng
        user_info_form_layout.addWidget(QLabel("Vị Trí Tầng:"), 2, 0)
        self.combo_floor_qt = QComboBox()
        self.combo_floor_qt.setFont(self.default_font)
        self.combo_floor_qt.addItems(["Tầng G", "Lầu 1", "Lầu 2", "Khác"])
        self.combo_floor_qt.currentIndexChanged.connect(self.on_floor_change_qt)
        user_info_form_layout.addWidget(self.combo_floor_qt, 2, 1)

        self.entry_custom_floor_label_qt = QLabel("Nhập vị trí hiện tại:")
        self.entry_custom_floor_qt = QLineEdit()
        self.entry_custom_floor_qt.setFont(self.default_font)
        user_info_form_layout.addWidget(self.entry_custom_floor_label_qt, 2, 2)
        user_info_form_layout.addWidget(self.entry_custom_floor_qt, 2, 3)
        self.on_floor_change_qt() # Initial state

        # Chức Vụ
        user_info_form_layout.addWidget(QLabel("Chức Vụ:"), 3, 0)
        self.entry_position_qt = QLineEdit()
        self.entry_position_qt.setFont(self.default_font)
        user_info_form_layout.addWidget(self.entry_position_qt, 3, 1, 1, 3)

        # Ghi chú
        user_info_form_layout.addWidget(QLabel("Ghi chú:"), 4, 0, Qt.AlignTop)
        self.text_notes_qt = QTextEdit()
        self.text_notes_qt.setFont(self.default_font)
        self.text_notes_qt.setFixedHeight(60) # Giới hạn chiều cao
        user_info_form_layout.addWidget(self.text_notes_qt, 4, 1, 1, 3)

        user_info_form_layout.setColumnStretch(1, 1) # Cho cột input mở rộng
        user_info_form_layout.setColumnStretch(3, 1)

        # --- Search bar for Home results ---
        search_home_layout = QHBoxLayout()
        # search_home_layout.addWidget(QLabel("Tìm trong kết quả:")) # Bỏ label
        self.search_home_results_input = QLineEdit()
        self.search_home_results_input.setFont(self.default_font)
        self.search_home_results_input.setPlaceholderText("Nhập từ khóa...")
        self.search_home_results_input.textChanged.connect(lambda: self.search_home_results_timer.start(300)) # Debounce 300ms
        search_home_layout.addWidget(self.search_home_results_input)
        layout.addLayout(search_home_layout)

        # --- System Info Display (QGroupBox + QTextEdit) ---
        group_system_info = QGroupBox("Thông tin hệ thống")
        group_system_info.setFont(self.bold_font)
        layout.addWidget(group_system_info, 1) # Cho phép mở rộng
        system_info_layout = QVBoxLayout(group_system_info)
        self.text_home_info_qt = QTextEdit()
        self.text_home_info_qt.setReadOnly(True)
        self.text_home_info_qt.setFont(self.monospace_font)
        self.text_home_info_qt.setWordWrapMode(QTextOption.NoWrap) # Tắt word wrap để giữ định dạng
        system_info_layout.addWidget(self.text_home_info_qt)
        self._update_display_widget(self.text_home_info_qt, "Đang tải thông tin ban đầu...")

        # --- Button to refresh Home tab info ---
        self.button_refresh_home_qt = QPushButton("Làm mới Dữ liệu PC")
        self.button_refresh_home_qt.setFont(self.default_font)
        self.button_refresh_home_qt.setCursor(Qt.PointingHandCursor)
        self.button_refresh_home_qt.clicked.connect(self.fetch_pc_info_threaded)
        layout.addWidget(self.button_refresh_home_qt, 0, Qt.AlignCenter)

    def on_floor_change_qt(self):
        is_custom = self.combo_floor_qt.currentText() == "Khác"
        self.entry_custom_floor_label_qt.setVisible(is_custom)
        self.entry_custom_floor_qt.setVisible(is_custom)
        if not is_custom:
            self.entry_custom_floor_qt.clear()

    def _create_utilities_tab(self, parent_tab_widget):
        main_layout = QHBoxLayout(parent_tab_widget)

        # --- Left Column: Search Bar and Action Buttons ---
        left_column_widget = QWidget()
        left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setContentsMargins(0,0,0,0) # Remove margins for tighter fit
        left_column_layout.setSpacing(5) # Spacing between search and scroll area

        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        actions_widget_container = QWidget() # Container cho layout các groupbox
        self.utilities_actions_layout = QVBoxLayout(actions_widget_container) # Store as instance member

        self.search_utilities_actions_timer = QTimer(self) # Timer riêng cho tab này
        self.search_utilities_actions_timer.setSingleShot(True)
        self.search_utilities_actions_timer.timeout.connect(lambda: self._filter_action_buttons(self.search_utilities_actions_input.text(), self.utilities_actions_layout))

        # --- Search bar for Utility actions ---
        search_actions_layout = QHBoxLayout()
        self.search_utilities_actions_input = QLineEdit()
        self.search_utilities_actions_input.setFont(self.default_font)
        self.search_utilities_actions_input.setPlaceholderText("Nhập tên tiện ích...")
        self.search_utilities_actions_input.textChanged.connect(lambda: self.search_utilities_actions_timer.start(300))
        search_actions_layout.addWidget(self.search_utilities_actions_input)
        
        left_column_layout.addLayout(search_actions_layout) # Add search bar to the top of the left column

        self.utilities_actions_layout.setSpacing(10) # Tăng khoảng cách giữa các GroupBox
        self.utilities_actions_layout.setAlignment(Qt.AlignTop) # Giữ các groupbox ở trên cùng


        # Group: Bảo mật & Virus
        group_security = QGroupBox("Bảo mật & Virus")
        group_security.setFont(self.bold_font)
        sec_layout = QVBoxLayout(group_security)
        self._add_utility_button(sec_layout, "Quét Virus Nhanh", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, run_windows_defender_scan, "utility_defender_quick_scan", needs_wmi=False, task_args=["QuickScan"]))
        self._add_utility_button(sec_layout, "Quét Virus Toàn Bộ", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, run_windows_defender_scan, "utility_defender_full_scan", needs_wmi=False, task_args=["FullScan"]))
        self._add_utility_button(sec_layout, "Cập Nhật Định Nghĩa Virus", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, update_windows_defender_definitions, "utility_defender_update", needs_wmi=False))
        
        self._add_utility_button(sec_layout, "Kiểm Tra Trạng Thái Tường Lửa", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_firewall_status, "utility_firewall_status", needs_wmi=False))
        self._add_utility_button(sec_layout, "Bật Tường Lửa (Tất cả Profile)", self.enable_firewall_qt)
        self._add_utility_button(sec_layout, "Tắt Tường Lửa (Tất cả Profile)", self.disable_firewall_qt)
        self.utilities_actions_layout.addWidget(group_security)

        # Group: Thông tin & Chẩn đoán
        group_diag = QGroupBox("Thông tin & Chẩn đoán")
        group_diag.setFont(self.bold_font)
        diag_layout = QVBoxLayout(group_diag)
        self._add_utility_button(diag_layout, "Xem Dung Lượng Ổ Đĩa", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_disk_partitions_usage, "utility_disk_usage", needs_wmi=True))
        self._add_utility_button(diag_layout, "Tạo Báo Cáo Pin (Laptop)", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, generate_battery_report, "utility_battery_report", needs_wmi=False))
        self._add_utility_button(diag_layout, "Kiểm tra kích hoạt Windows", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, check_windows_activation_status, "utility_win_activation", needs_wmi=False))
        self._add_utility_button(diag_layout, "Xem Event Log Gần Đây (24h)", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_recent_event_logs, "utility_event_logs", needs_wmi=True, wmi_namespace="root\\CIMV2", task_args=[24, 25])) # hours, max_events
        self._add_utility_button(diag_layout, "Kiểm Tra Phiên Bản Phần Mềm", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_installed_software_versions, "utility_software_versions_wmi", needs_wmi=True)) # Assumes function can use WMI
        self._add_utility_button(diag_layout, "Ứng Dụng Người Dùng Đã Cài", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_installed_software_versions, "utility_software_versions_reg", needs_wmi=False)) # Assumes function uses winreg
        # Nút "Kiểm Tra Kết Nối Wifi" đã được chuyển hoàn toàn vào group "Mạng".
        self.utilities_actions_layout.addWidget(group_diag)

        # Group: Mạng
        group_network = QGroupBox("Mạng")
        group_network.setFont(self.bold_font)
        net_layout = QVBoxLayout(group_network)
        self._add_utility_button(net_layout, "Kiểm Tra Kết Nối Wifi", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_wifi_connection_info, "utility_wifi_info", needs_wmi=False))
        self._add_utility_button(net_layout, "Xem Cấu Hình Mạng Chi Tiết", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_network_configuration_details, "utility_network_config", needs_wmi=True))
        self._add_utility_button(net_layout, "Ping Google", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, run_ping_test, "utility_ping_google", needs_wmi=False, task_args=["google.com", 4]))
        self._add_utility_button(net_layout, "Tra Cứu DNS Google", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, lookup_dns_address, "utility_dns_lookup", needs_wmi=False, task_args=["google.com"]))
        self._add_utility_button(net_layout, "Kết Nối Mạng Đang Hoạt Động", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_active_network_connections, "utility_active_connections", needs_wmi=False))
        self._add_utility_button(net_layout, "Xóa Cache DNS", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, flush_dns_cache, "utility_flush_dns", needs_wmi=False))
        self.utilities_actions_layout.addWidget(group_network)

        # Các group khác có thể được thêm vào đây
        self._add_utility_button(diag_layout, "Kiểm Tra Nhiệt Độ Hệ Thống", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_system_temperatures, "utility_temps", needs_wmi=True, wmi_namespace="root\\WMI"))
        self._add_utility_button(diag_layout, "Liệt Kê Tiến Trình Đang Chạy", lambda: self._run_task_in_thread_qt(self.text_utilities_results_qt, get_running_processes, "utility_processes", needs_wmi=False))
        
        self.utilities_actions_layout.addStretch(1) # Đẩy các group lên trên

        scroll_area_actions.setWidget(actions_widget_container)
        left_column_layout.addWidget(scroll_area_actions) # Add scroll area below search bar
        main_layout.addWidget(left_column_widget, 2) # Tỷ lệ 2 cho cột trái

        # --- Right Column: Utilities Results Display ---
        results_container_widget = QWidget()
        results_main_layout = QVBoxLayout(results_container_widget)

        # --- Search bar for Utilities results ---
        search_results_layout = QHBoxLayout()
        self.search_utilities_results_input = QLineEdit()
        self.search_utilities_results_input.setFont(self.default_font)
        self.search_utilities_results_input.setPlaceholderText("Nhập từ khóa...")
        self.search_utilities_results_input.textChanged.connect(lambda: self.search_utilities_results_timer.start(300))
        search_results_layout.addWidget(self.search_utilities_results_input)
        results_main_layout.addLayout(search_results_layout)

        results_group = QGroupBox("Kết quả Tiện ích")
        results_group.setFont(self.bold_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_utilities_results_qt = QTextEdit()
        self.text_utilities_results_qt.setReadOnly(True)
        self.text_utilities_results_qt.setFont(self.monospace_font)
        self.text_utilities_results_qt.setWordWrapMode(QTextOption.NoWrap)
        results_layout_inner.addWidget(self.text_utilities_results_qt)
        self._update_display_widget(self.text_utilities_results_qt, "Kết quả của tiện ích sẽ hiển thị ở đây.")
        results_main_layout.addWidget(results_group, 1) # Cho phép mở rộng

        # Buttons dưới ô kết quả
        utils_buttons_frame = QFrame()
        utils_buttons_layout = QHBoxLayout(utils_buttons_frame)
        utils_buttons_layout.addStretch(1) # Đẩy nút Lưu sang phải
        self.button_save_utility_result_qt = QPushButton("Lưu Kết Quả")
        self.button_save_utility_result_qt.setCursor(Qt.PointingHandCursor)
        self.button_save_utility_result_qt.setFont(self.default_font)
        self.button_save_utility_result_qt.setEnabled(False)
        self.button_save_utility_result_qt.clicked.connect(lambda: self.save_tab_result_qt(self.text_utilities_results_qt.toPlainText(), "KetQua_TienIch"))
        utils_buttons_layout.addWidget(self.button_save_utility_result_qt)
        results_main_layout.addWidget(utils_buttons_frame)

        main_layout.addWidget(results_container_widget, 5) # Tỷ lệ 5

    def _add_utility_button(self, layout, text, on_click_action):
        button = QPushButton(text)
        button.setFont(self.default_font)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(on_click_action)
        layout.addWidget(button)

    def _create_fixes_tab(self, parent_tab_widget):
        # Tương tự _create_utilities_tab, nhưng với các nút và logic khác
        main_layout = QHBoxLayout(parent_tab_widget)

        # --- Left Column: Search Bar and Action Buttons ---
        left_column_widget_fixes = QWidget()
        left_column_layout_fixes = QVBoxLayout(left_column_widget_fixes)
        left_column_layout_fixes.setContentsMargins(0,0,0,0)
        left_column_layout_fixes.setSpacing(5)

        scroll_area_actions = QScrollArea()
        scroll_area_actions.setWidgetResizable(True)
        actions_widget_container = QWidget()
        self.fixes_actions_layout = QVBoxLayout(actions_widget_container) # Store as instance member

        self.search_fixes_actions_timer = QTimer(self) # Timer riêng cho tab này
        self.search_fixes_actions_timer.setSingleShot(True)
        self.search_fixes_actions_timer.timeout.connect(lambda: self._filter_action_buttons(self.search_fixes_actions_input.text(), self.fixes_actions_layout))

        # --- Search bar for Fix actions ---
        search_actions_fixes_layout = QHBoxLayout()
        self.search_fixes_actions_input = QLineEdit()
        self.search_fixes_actions_input.setFont(self.default_font)
        self.search_fixes_actions_input.setPlaceholderText("Nhập tên chức năng...")
        self.search_fixes_actions_input.textChanged.connect(lambda: self.search_fixes_actions_timer.start(300))
        search_actions_fixes_layout.addWidget(self.search_fixes_actions_input)
        left_column_layout_fixes.addLayout(search_actions_fixes_layout) # Add search bar to the top of the left column

        self.fixes_actions_layout.setSpacing(10) # Tăng khoảng cách giữa các GroupBox
        self.fixes_actions_layout.setAlignment(Qt.AlignTop)

        # Group: Dọn dẹp & Tối ưu
        group_cleanup = QGroupBox("Dọn dẹp & Tối ưu")
        group_cleanup.setFont(self.bold_font)
        cleanup_layout = QVBoxLayout(group_cleanup)
        self._add_utility_button(cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, clear_temporary_files, "fix_clear_temp", needs_wmi=False))
        self._add_utility_button(cleanup_layout, "Mở Resource Monitor", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, open_resource_monitor, "fix_resmon", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_cleanup)

        # Group: Sửa lỗi Hệ thống
        group_sys_fix = QGroupBox("Sửa lỗi Hệ thống")
        group_sys_fix.setFont(self.bold_font)
        sys_fix_layout = QVBoxLayout(group_sys_fix)
        self._add_utility_button(sys_fix_layout, "Reset Kết Nối Internet", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, reset_internet_connection, "fix_reset_net", needs_wmi=False))
        self._add_utility_button(sys_fix_layout, "Chạy SFC Scan", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, run_sfc_scan, "fix_sfc_scan", needs_wmi=False))
        self._add_utility_button(sys_fix_layout, "Tạo Điểm Khôi Phục Hệ Thống", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, create_system_restore_point, "fix_create_restore_point", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_sys_fix)

        # Group: Cập nhật & Khởi động
        group_updates = QGroupBox("Cập nhật & Khởi động")
        group_updates.setFont(self.bold_font)
        updates_layout = QVBoxLayout(group_updates)
        self._add_utility_button(updates_layout, "Quản Lý Khởi Động Cùng Windows", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, get_startup_programs, "fix_startup_programs", needs_wmi=True))
        self._add_utility_button(updates_layout, "Cập Nhật Phần Mềm (Winget)", lambda: self._run_task_in_thread_qt(self.text_fixes_results_qt, update_all_winget_packages, "fix_winget_update", needs_wmi=False))
        self.fixes_actions_layout.addWidget(group_updates)

        self.fixes_actions_layout.addStretch(1)
        scroll_area_actions.setWidget(actions_widget_container)
        left_column_layout_fixes.addWidget(scroll_area_actions) # Add scroll area below search bar
        main_layout.addWidget(left_column_widget_fixes, 2) # Tỷ lệ 2 cho cột trái

        # Right Column: Fixes Results Display
        results_container_widget = QWidget()
        results_main_layout = QVBoxLayout(results_container_widget)
        # --- Search bar for Fixes results ---
        search_results_fixes_layout = QHBoxLayout()
        # search_results_fixes_layout.addWidget(QLabel("Tìm trong kết quả:")) # Bỏ label
        self.search_fixes_results_input = QLineEdit()
        self.search_fixes_results_input.setFont(self.default_font)
        self.search_fixes_results_input.setPlaceholderText("Nhập từ khóa...")
        self.search_fixes_results_input.textChanged.connect(lambda: self.search_fixes_results_timer.start(300))
        search_results_fixes_layout.addWidget(self.search_fixes_results_input)
        results_main_layout.addLayout(search_results_fixes_layout)

        results_group = QGroupBox("Kết quả Tác vụ Sửa lỗi")
        results_group.setFont(self.bold_font)
        results_layout_inner = QVBoxLayout(results_group)
        self.text_fixes_results_qt = QTextEdit()
        self.text_fixes_results_qt.setReadOnly(True)
        self.text_fixes_results_qt.setFont(self.monospace_font)
        self.text_fixes_results_qt.setWordWrapMode(QTextOption.NoWrap)
        results_layout_inner.addWidget(self.text_fixes_results_qt)
        self._update_display_widget(self.text_fixes_results_qt, "Chọn một tác vụ để thực hiện.")
        results_main_layout.addWidget(results_group, 1)

        self.button_save_fix_result_qt = QPushButton("Lưu Kết Quả Sửa Lỗi")
        self.button_save_fix_result_qt.setCursor(Qt.PointingHandCursor)
        self.button_save_fix_result_qt.setFont(self.default_font)
        self.button_save_fix_result_qt.setEnabled(False)
        self.button_save_fix_result_qt.clicked.connect(lambda: self.save_tab_result_qt(self.text_fixes_results_qt.toPlainText(), "KetQua_SuaLoi"))
        results_main_layout.addWidget(self.button_save_fix_result_qt, 0, Qt.AlignRight)

        main_layout.addWidget(results_container_widget, 5)

    def _apply_styles(self):
        # Áp dụng QSS (Qt Style Sheets)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
            }
            QGroupBox {
                border: 1px solid #C0C0C0;
                border-radius: 5px;
                margin-top: 10px; /* Platz für den Titel */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px 0 5px;
                background-color: #F0F0F0; /* Gleiche Farbe wie Fensterhintergrund */
            }
            QLabel {
                font-family: """ + DEFAULT_FONT_FAMILY + """;
                font-size: """ + str(DEFAULT_FONT_SIZE) + """pt;
                padding: 2px;
            }
            QPushButton {
                font-family: """ + DEFAULT_FONT_FAMILY + """;
                font-size: """ + str(DEFAULT_FONT_SIZE) + """pt;
                padding: 5px 10px;
                background-color: #E1E1E1;
                border: 1px solid #ADADAD;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #CACACA;
            }
            QPushButton:pressed {
                background-color: #B0B0B0;
            }
            QPushButton:disabled {
                background-color: #D3D3D3;
                color: #A0A0A0;
            }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QTextEdit {
                 font-family: """ + MONOSPACE_FONT_FAMILY + """;
                 font-size: """ + str(MONOSPACE_FONT_SIZE) + """pt;
            }
            QTabWidget::pane { /* The tab widget frame */
                border-top: 1px solid #C0C0C0;
                background: white;
            }
            QTabBar::tab {
                background: #E0E0E0;
                border: 1px solid #C0C0C0;
                border-bottom-color: #C0C0C0; /* Same as pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #C0C0C0;
                border-bottom-color: white; /* Make it seamless with pane */
            }
            QTabBar::tab:!selected:hover {
                background: #D0D0D0;
            }
            QScrollArea {
                border: none;
            }
        """)
        self.button_export_home.setStyleSheet("background-color: #A9D18E;") # Green
        self.button_exit.setStyleSheet("background-color: #FFB6C1;") # Pink

    def _update_display_widget(self, text_widget, content, is_error=False):
        text_widget.clear()
        
        processed_lines = []
        for line in content.splitlines():
            stripped_line = line.strip()
            # Chỉ in đậm nếu dòng BẮT ĐẦU và KẾT THÚC bằng ** (và có nội dung ở giữa)
            if stripped_line.startswith("**") and stripped_line.endswith("**") and len(stripped_line) > 4:
                # Lấy phần nội dung giữa dấu ** để escape riêng
                inner_content = stripped_line[2:-2]
                # Giữ nguyên phần thụt lề gốc (nếu có) bằng cách lấy khoảng trắng ở đầu line gốc
                leading_spaces = line[:len(line) - len(line.lstrip())]
                processed_lines.append(f"{leading_spaces}<b>{html.escape(inner_content)}</b>")
            else:
                # Nếu không, escape toàn bộ dòng
                processed_lines.append(html.escape(line))

        final_html_content = "<br>".join(processed_lines)

        if is_error or "Lỗi" in content or "Error" in content or "Không thể" in content:
            text_widget.setHtml(f"<font color='{ERROR_TEXT_COLOR_HTML}'><pre>{final_html_content}</pre></font>")
        else:
            text_widget.setHtml(f"<font color='{DEFAULT_TEXT_COLOR_HTML}'><pre>{final_html_content}</pre></font>")

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
        self.button_save_utility_result_qt.setEnabled(enable_save_utility)
        self.button_save_fix_result_qt.setEnabled(enable_save_fix)

    def fetch_pc_info_threaded(self):
        self._update_display_widget(self.text_home_info_qt, "Đang lấy thông tin, vui lòng chờ...")
        self._toggle_buttons_qt(enable_refresh_home=False, enable_export_home=False)

        # Clear previous search in home results when refreshing
        if hasattr(self, 'search_home_results_input'):
            self.search_home_results_input.clear()

        thread = WorkerThread(get_detailed_system_information, "fetch_pc_info", needs_wmi=False) # function handles its own WMI
        thread.task_completed.connect(self._on_fetch_pc_info_completed)
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        thread.start()

    def _on_fetch_pc_info_completed(self, task_name, data):
        if task_name == "fetch_pc_info":
            self.pc_info_dict = data
            home_info_data = self.pc_info_dict.get("SystemInformation", {"PC": {"Lỗi": "Không có dữ liệu SystemInformation"}})
            self.formatted_pc_info_string_home = format_system_details_to_string(home_info_data) # Chỉ format phần system details
            self._update_display_widget(self.text_home_info_qt, self.formatted_pc_info_string_home)
            self._toggle_buttons_qt(enable_refresh_home=True, enable_export_home=True)

    def _on_task_error(self, task_name, error_message):
        logging.error(f"Error in task '{task_name}': {error_message}")
        is_fetch_pc_info = task_name == "fetch_pc_info"
        is_utility_task = task_name.startswith("utility_")
        is_fix_task = task_name.startswith("fix_")

        if is_fetch_pc_info:
            self.pc_info_dict = None
            self.formatted_pc_info_string_home = f"Lỗi khi lấy thông tin:\n{error_message}"
            self._update_display_widget(self.text_home_info_qt, self.formatted_pc_info_string_home, is_error=True)
            self._toggle_buttons_qt(enable_refresh_home=True, enable_export_home=False)
        elif is_utility_task:
            self._update_display_widget(self.text_utilities_results_qt, f"Lỗi khi thực hiện tác vụ:\n{error_message}", is_error=True)
            self._toggle_buttons_qt(enable_save_utility=True) # Vẫn cho phép lưu lỗi nếu muốn
        elif is_fix_task:
            self._update_display_widget(self.text_fixes_results_qt, f"Lỗi khi thực hiện tác vụ:\n{error_message}", is_error=True)
            self._toggle_buttons_qt(enable_save_fix=True)

        QMessageBox.warning(self, "Lỗi Tác Vụ", f"Lỗi khi thực hiện '{task_name}':\n{error_message}")

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

    def save_tab_result_qt(self, content_to_save, default_prefix="KetQua"):
        if not content_to_save or content_to_save == "Kết quả của tiện ích sẽ hiển thị ở đây." or content_to_save == "Chọn một tác vụ để thực hiện." or "Đang thực hiện:" in content_to_save:
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

    def _run_task_in_thread_qt(self, target_widget, task_function, task_name_prefix, needs_wmi=False, wmi_namespace="root\\CIMV2", task_args=None):
        task_name = f"{task_name_prefix}_{task_function.__name__}_{datetime.now().strftime('%H%M%S%f')}" # Unique task name
        self._update_display_widget(target_widget, f"Đang thực hiện: {task_function.__name__}...")
        
        is_utility_task = target_widget == self.text_utilities_results_qt
        is_fix_task = target_widget == self.text_fixes_results_qt

        # Clear previous search in the target_widget before running a new task
        if is_utility_task and hasattr(self, 'search_utilities_results_input'): self.search_utilities_results_input.clear()
        elif is_fix_task and hasattr(self, 'search_fixes_results_input'): self.search_fixes_results_input.clear()
        self._clear_text_highlights(target_widget) # Clear highlights as well

        if is_utility_task: self._toggle_buttons_qt(enable_save_utility=False)
        elif is_fix_task: self._toggle_buttons_qt(enable_save_fix=False)

        # Đảm bảo task_args là một tuple để unpack an toàn
        if task_args is None:
            actual_args_for_thread_tuple = tuple()
        elif isinstance(task_args, (list, tuple)):
            actual_args_for_thread_tuple = tuple(task_args)
        else: # Nếu task_args là một giá trị đơn lẻ, coi nó là một tuple một phần tử
            actual_args_for_thread_tuple = (task_args,)
            
        thread = WorkerThread(task_function, task_name, needs_wmi, wmi_namespace, *actual_args_for_thread_tuple)
        thread.task_completed.connect(lambda name, data: self._on_generic_task_completed(name, data, target_widget))
        thread.task_error.connect(self._on_task_error)
        self.threads.append(thread)
        thread.start()

    def _on_generic_task_completed(self, task_name, data, target_widget):
        # Sử dụng lại hàm format_task_result_for_display từ Tkinter version (nó trả về string)
        # Lấy lại hàm _format_task_result_for_display từ file pc_info_gui.py (Tkinter)
        # và điều chỉnh nếu cần. Vì mục đích demo, ta sẽ dùng một bản rút gọn.
        display_text = self._format_task_result_for_display_generic(data)
        self._update_display_widget(target_widget, display_text)

        is_utility_task = target_widget == self.text_utilities_results_qt
        is_fix_task = target_widget == self.text_fixes_results_qt
        if is_utility_task: self._toggle_buttons_qt(enable_save_utility=True)
        elif is_fix_task: self._toggle_buttons_qt(enable_save_fix=True)

    def _format_task_result_for_display_generic(self, result_data):
        """Định dạng kết quả tác vụ thành chuỗi, sử dụng ** cho bold."""
        if result_data is None:
            return "Tác vụ hoàn thành, không có dữ liệu trả về."
        if isinstance(result_data, str) and (result_data == NOT_AVAILABLE or result_data == NOT_FOUND or result_data == ERROR_WMI_CONNECTION):
             return result_data

        lines = []
        if isinstance(result_data, list):
            if not result_data:
                return "Tác vụ hoàn thành, không có mục nào được trả về."
            for item in result_data:
                if isinstance(item, dict):
                    item_lines = []
                    for k, v in item.items():
                        item_lines.append(f"  **{k}:** {v}")
                    lines.append("\n".join(item_lines))
                else:
                    lines.append(str(item))
            return "\n---\n".join(lines)
        elif isinstance(result_data, dict):
            if not result_data:
                return "Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng)."
            
            if "message" in result_data and "status" in result_data:
                lines.append(f"**Trạng thái:** {result_data.get('status', 'N/A')}")
                lines.append(f"**Thông điệp:** {result_data['message']}")
                
                if "details" in result_data and result_data['details']:
                    details_content = result_data['details']
                    details_str_list = ["\n**Chi tiết:**"]
                    if isinstance(details_content, dict):
                        for k_detail, v_detail in details_content.items():
                            if k_detail == 'errors_list' and isinstance(v_detail, list) and v_detail:
                                details_str_list.append(f"  **Lỗi chi tiết:**")
                                for i, err_item in enumerate(v_detail[:5]): # Show first 5 errors
                                    details_str_list.append(f"    - {err_item}")
                                if len(v_detail) > 5:
                                    details_str_list.append("    ...")
                            elif k_detail == 'deleted_files_count' or k_detail == 'deleted_folders_count' or k_detail == 'total_size_freed_mb':
                                details_str_list.append(f"  **{k_detail.replace('_', ' ').capitalize()}:** {v_detail}")
                            else: # General key-value in details
                                details_str_list.append(f"  **{k_detail}:** {v_detail}")
                    elif isinstance(details_content, list): # if details is a list of strings
                         for detail_item in details_content:
                            details_str_list.append(f"  {detail_item}")
                    else: # Generic details string
                        details_str_list.append(f"  {details_content}")
                    lines.append("\n".join(details_str_list))
                
                if "path" in result_data and result_data['path']:
                    lines.append(f"\n**Đường dẫn file:** {result_data['path']}")
                return "\n".join(lines)
            else:
                for k, v in result_data.items():
                    lines.append(f"**{k}:** {v}")
                return "\n".join(lines)
        else:
            return str(result_data)

    def enable_firewall_qt(self):
        if QMessageBox.question(self, "Xác nhận Bật Tường lửa", "Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._run_task_in_thread_qt(self.text_utilities_results_qt, toggle_firewall, "utility_firewall_enable", needs_wmi=False, task_args=[True])

    def disable_firewall_qt(self):
        if QMessageBox.question(self, "XÁC NHẬN TẮT TƯỜNG LỬA", "CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._run_task_in_thread_qt(self.text_utilities_results_qt, toggle_firewall, "utility_firewall_disable", needs_wmi=False, task_args=[False])

    def closeEvent(self, event):
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
        super().closeEvent(event)

# Khối main để chạy thử trực tiếp file này (nếu cần)
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = PcInfoAppQt()
#     main_window.show()
#     sys.exit(app.exec_())