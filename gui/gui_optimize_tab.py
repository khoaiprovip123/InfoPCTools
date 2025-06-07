from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QScrollArea, QGroupBox, QPushButton,
    QStackedWidget, QTextEdit, QTableWidget, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption

# Giả sử các hàm core và hằng số cần thiết sẽ được truy cập qua parent_app
# hoặc được import trực tiếp nếu chúng là hằng số toàn cục.
from core.pc_info_functions import ( # type: ignore
    clear_temporary_files, open_resource_monitor, get_startup_programs,
    run_sfc_scan, create_system_restore_point, update_all_winget_packages,
    optimize_windows_services, clean_registry_with_backup, list_printers,
    remove_printer, clear_print_queue, restart_print_spooler_service
)

def create_optimize_tab_content(parent_app):
    """
    Tạo nội dung cho tab Tối Ưu.
    'parent_app' là instance của PcInfoAppQt.
    """
    tab_main_layout = QVBoxLayout(parent_app.page_optimize)
    content_splitter_optimize = QSplitter(Qt.Horizontal)
    tab_main_layout.addWidget(content_splitter_optimize)

    left_column_widget = QWidget()
    left_column_layout = QVBoxLayout(left_column_widget)
    left_column_layout.setContentsMargins(0,0,0,0)
    left_column_layout.setSpacing(5)
    scroll_area_actions = QScrollArea()
    scroll_area_actions.setWidgetResizable(True)
    optimize_actions_widget_container = QWidget()
    parent_app.optimize_actions_layout = QVBoxLayout(optimize_actions_widget_container)
    parent_app.optimize_actions_layout.setSpacing(10)
    parent_app.optimize_actions_layout.setAlignment(Qt.AlignTop)

    parent_app.button_one_click_optimize = QPushButton("🚀 Tối Ưu Hóa Toàn Diện (1-Click)")
    parent_app.button_one_click_optimize.setFont(parent_app.h2_font)
    parent_app.button_one_click_optimize.setObjectName("OneClickOptimizeButton")
    parent_app.button_one_click_optimize.setToolTip("Chạy các tác vụ dọn dẹp, tối ưu cơ bản và sửa lỗi được đề xuất.")
    parent_app.button_one_click_optimize.clicked.connect(parent_app.on_one_click_optimize_clicked)
    parent_app.optimize_actions_layout.addWidget(parent_app.button_one_click_optimize)

    parent_app.button_toggle_gaming_mode = QPushButton("🎮 Chế Độ Gaming: TẮT")
    parent_app.button_toggle_gaming_mode.setCheckable(True)
    parent_app.button_toggle_gaming_mode.setFont(parent_app.h2_font)
    parent_app.button_toggle_gaming_mode.setObjectName("GamingModeButton")
    parent_app.button_toggle_gaming_mode.toggled.connect(parent_app.on_toggle_gaming_mode_clicked)
    parent_app.optimize_actions_layout.addWidget(parent_app.button_toggle_gaming_mode)

    line_sep = QFrame()
    line_sep.setFrameShape(QFrame.HLine)
    line_sep.setFrameShadow(QFrame.Sunken)
    parent_app.optimize_actions_layout.addWidget(line_sep)

    group_cleanup = QGroupBox("Dọn dẹp & Tối ưu Cơ Bản")
    group_cleanup.setFont(parent_app.h2_font)
    cleanup_layout = QVBoxLayout(group_cleanup)
    parent_app._add_utility_button(cleanup_layout, "Xóa File Tạm & Dọn Dẹp", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, clear_temporary_files, "optimize_clear_temp"))
    parent_app._add_utility_button(cleanup_layout, "Mở Resource Monitor", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, open_resource_monitor, "optimize_resmon"))
    parent_app._add_utility_button(cleanup_layout, "Quản Lý Ứng Dụng Khởi Động", parent_app.on_manage_startup_programs_clicked)
    parent_app.optimize_actions_layout.addWidget(group_cleanup)

    group_fix_update = QGroupBox("Sửa lỗi & Cập nhật")
    group_fix_update.setFont(parent_app.h2_font)
    fix_update_layout = QVBoxLayout(group_fix_update)
    parent_app._add_utility_button(fix_update_layout, "Chạy SFC Scan", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, run_sfc_scan, "optimize_sfc_scan"))
    parent_app._add_utility_button(fix_update_layout, "Tạo Điểm Khôi Phục Hệ Thống", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, create_system_restore_point, "optimize_create_restore_point"))
    parent_app._add_utility_button(fix_update_layout, "Cập Nhật Phần Mềm (Winget)", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, update_all_winget_packages, "optimize_winget_update"))
    parent_app.optimize_actions_layout.addWidget(group_fix_update)
    
    group_advanced_optimization = QGroupBox("Tối ưu Nâng Cao")
    group_advanced_optimization.setFont(parent_app.h2_font)
    advanced_opt_layout = QVBoxLayout(group_advanced_optimization)        
    parent_app._add_utility_button(advanced_opt_layout, "Tối ưu Dịch Vụ Windows", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, optimize_windows_services, "optimize_optimize_services"))
    parent_app._add_utility_button(advanced_opt_layout, "Dọn Dẹp Registry (Có Sao Lưu)", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, clean_registry_with_backup, "optimize_clean_registry"))
    parent_app.optimize_actions_layout.addWidget(group_advanced_optimization)

    group_printer_management = QGroupBox("Quản lý Máy In")
    group_printer_management.setFont(parent_app.h2_font)
    printer_mgmt_layout = QVBoxLayout(group_printer_management)
    parent_app._add_utility_button(printer_mgmt_layout, "Liệt kê Máy In", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, list_printers, "optimize_list_printers", needs_wmi=True, result_type="table"))
    parent_app._add_utility_button(printer_mgmt_layout, "Gỡ Máy In Lỗi", parent_app.run_remove_printer_qt)
    parent_app._add_utility_button(printer_mgmt_layout, "Xóa Lệnh In (Tất cả)", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, clear_print_queue, "optimize_clear_all_print_queues", needs_wmi=False))
    parent_app._add_utility_button(printer_mgmt_layout, "Xóa Lệnh In (Chọn Máy In)", parent_app.run_clear_specific_print_queue_qt)
    parent_app._add_utility_button(printer_mgmt_layout, "Fix Lỗi Máy In (Khởi động lại Spooler)", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_optimize, restart_print_spooler_service, "optimize_restart_spooler", needs_wmi=False))
    parent_app.optimize_actions_layout.addWidget(group_printer_management)

    parent_app.optimize_actions_layout.addStretch(1)
    scroll_area_actions.setWidget(optimize_actions_widget_container)
    left_column_layout.addWidget(scroll_area_actions)
    content_splitter_optimize.addWidget(left_column_widget)

    results_container_widget = QWidget()
    parent_app.optimize_results_main_layout = QVBoxLayout(results_container_widget)
    parent_app.optimize_results_main_layout.setContentsMargins(0,0,0,0)
    parent_app.stacked_widget_results_optimize = parent_app._create_results_display_area(
        "Kết quả Tối Ưu", "OptimizeResultTextEdit", "OptimizeResultTable" # Đặt tên objectName khác nhau
    )

    parent_app.startup_manager_buttons_frame = QFrame()
    startup_buttons_layout = QHBoxLayout(parent_app.startup_manager_buttons_frame)
    parent_app.button_enable_startup_item = QPushButton("Bật mục chọn")
    parent_app.button_enable_startup_item.clicked.connect(lambda: parent_app.on_manage_selected_startup_item("enable"))
    parent_app.button_disable_startup_item = QPushButton("Tắt mục chọn")
    parent_app.button_disable_startup_item.clicked.connect(lambda: parent_app.on_manage_selected_startup_item("disable"))
    startup_buttons_layout.addWidget(parent_app.button_enable_startup_item)
    startup_buttons_layout.addWidget(parent_app.button_disable_startup_item)
    parent_app.startup_manager_buttons_frame.setVisible(False)
    parent_app.optimize_results_main_layout.addWidget(parent_app.startup_manager_buttons_frame)

    parent_app.optimize_results_main_layout.addWidget(parent_app.stacked_widget_results_optimize, 1)
    content_splitter_optimize.addWidget(results_container_widget)
    content_splitter_optimize.setSizes([320, 430])