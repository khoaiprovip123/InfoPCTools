from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QScrollArea, QGroupBox,
    QStackedWidget, QTextEdit, QTableWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption

# Giả sử các hàm core và hằng số cần thiết sẽ được truy cập qua parent_app
# hoặc được import trực tiếp nếu chúng là hằng số toàn cục.
# Ví dụ: from core.pc_info_functions import run_windows_defender_scan, update_windows_defender_definitions, get_firewall_status, toggle_firewall

def create_security_tab_content(parent_app):
    """
    Tạo nội dung cho tab Bảo Mật.
    'parent_app' là instance của PcInfoAppQt.
    """
    tab_main_layout = QVBoxLayout(parent_app.page_security)

    content_splitter = QSplitter(Qt.Horizontal)
    tab_main_layout.addWidget(content_splitter)

    # --- Left Column: Action Buttons ---
    left_column_widget = QWidget()
    left_column_layout = QVBoxLayout(left_column_widget)
    left_column_layout.setContentsMargins(0,0,0,0)
    left_column_layout.setSpacing(5)
    
    scroll_area_actions = QScrollArea()
    scroll_area_actions.setWidgetResizable(True)
    security_actions_widget_container = QWidget() 
    parent_app.security_actions_layout = QVBoxLayout(security_actions_widget_container) 
    parent_app.security_actions_layout.setSpacing(10) 
    parent_app.security_actions_layout.setAlignment(Qt.AlignTop) 

    group_security = QGroupBox("Bảo mật & Virus")
    group_security.setFont(parent_app.h2_font)
    sec_layout = QVBoxLayout(group_security)
    # Sử dụng parent_app để gọi _add_utility_button và _run_task_in_thread_qt
    # và các hàm core được import trong parent_app
    from core.pc_info_functions import run_windows_defender_scan, update_windows_defender_definitions, get_firewall_status, toggle_firewall # Import tại đây hoặc đảm bảo parent_app có thể gọi
    parent_app._add_utility_button(sec_layout, "Quét Virus Nhanh", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_security, run_windows_defender_scan, "security_defender_quick_scan", needs_wmi=False, task_args=["QuickScan"]))
    parent_app._add_utility_button(sec_layout, "Quét Virus Toàn Bộ", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_security, run_windows_defender_scan, "security_defender_full_scan", needs_wmi=False, task_args=["FullScan"]))
    parent_app._add_utility_button(sec_layout, "Cập Nhật Định Nghĩa Virus", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_security, update_windows_defender_definitions, "security_defender_update", needs_wmi=False))
    parent_app._add_utility_button(sec_layout, "Kiểm Tra Trạng Thái Tường Lửa", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_security, get_firewall_status, "security_firewall_status", needs_wmi=False))
    parent_app._add_utility_button(sec_layout, "Bật Tường Lửa (Tất cả Profile)", parent_app.enable_firewall_qt, object_name="WarningButton")
    parent_app._add_utility_button(sec_layout, "Tắt Tường Lửa (Tất cả Profile)", parent_app.disable_firewall_qt, object_name="DangerButton")
    parent_app.security_actions_layout.addWidget(group_security)

    parent_app.security_actions_layout.addStretch(1) 
    scroll_area_actions.setWidget(security_actions_widget_container)
    left_column_layout.addWidget(scroll_area_actions)
    content_splitter.addWidget(left_column_widget)

    # --- Right Column: Results Display ---
    results_container_widget = QWidget()
    parent_app.utilities_results_main_layout = QVBoxLayout(results_container_widget) 
    parent_app.utilities_results_main_layout.setContentsMargins(0,0,0,0)

    # Sử dụng _create_results_display_area từ parent_app
    parent_app.stacked_widget_results_security = parent_app._create_results_display_area(
        "Kết quả Bảo Mật", "SecurityResultTextEdit", "SecurityResultTable" # Đặt tên objectName khác nhau
    )
        
    parent_app.utilities_results_main_layout.addWidget(parent_app.stacked_widget_results_security, 1)
    content_splitter.addWidget(results_container_widget)
    content_splitter.setSizes([320, 430])