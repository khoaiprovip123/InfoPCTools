from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QScrollArea, QGroupBox,
    QStackedWidget, QTextEdit, QTableWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption

# Giả sử các hàm core và hằng số cần thiết sẽ được truy cập qua parent_app
from core.pc_info_functions import ( # type: ignore
    get_wifi_connection_info, get_network_configuration_details,
    run_ping_test, get_active_network_connections, flush_dns_cache,
    reset_internet_connection
)

def create_network_tab_content(parent_app):
    """
    Tạo nội dung cho tab Mạng.
    'parent_app' là instance của PcInfoAppQt.
    """
    tab_main_layout = QVBoxLayout(parent_app.page_network)
    content_splitter_network = QSplitter(Qt.Horizontal)
    tab_main_layout.addWidget(content_splitter_network)

    left_column_widget = QWidget()
    left_column_layout = QVBoxLayout(left_column_widget)
    left_column_layout.setContentsMargins(0,0,0,0)
    left_column_layout.setSpacing(5)
    scroll_area_actions = QScrollArea()
    scroll_area_actions.setWidgetResizable(True)
    network_actions_widget_container = QWidget()
    parent_app.network_actions_layout = QVBoxLayout(network_actions_widget_container)
    parent_app.network_actions_layout.setSpacing(10)
    parent_app.network_actions_layout.setAlignment(Qt.AlignTop)

    group_network = QGroupBox("Công cụ Mạng")
    group_network.setFont(parent_app.h2_font)
    net_layout = QVBoxLayout(group_network)
    parent_app._add_utility_button(net_layout, "Kiểm Tra Kết Nối Wifi", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, get_wifi_connection_info, "network_wifi_info"))
    parent_app._add_utility_button(net_layout, "Xem Cấu Hình Mạng Chi Tiết", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, get_network_configuration_details, "network_config", needs_wmi=True, result_type="table"))
    parent_app._add_utility_button(net_layout, "Ping Google", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, run_ping_test, "network_ping_google", task_args=["google.com", 4]))
    parent_app._add_utility_button(net_layout, "Phân giải IP tên miền", parent_app.run_domain_ip_resolution_qt)
    parent_app._add_utility_button(net_layout, "Kết Nối Mạng Đang Hoạt Động", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, get_active_network_connections, "network_active_connections", result_type="table"))
    parent_app._add_utility_button(net_layout, "Cấu hình DNS", parent_app.run_set_dns_config_qt)
    parent_app._add_utility_button(net_layout, "Xóa Cache DNS", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, flush_dns_cache, "network_flush_dns"))
    parent_app._add_utility_button(net_layout, "Reset Kết Nối Internet", lambda btn: parent_app._run_task_in_thread_qt(btn, parent_app.stacked_widget_results_network, reset_internet_connection, "network_reset_net"))
    parent_app.network_actions_layout.addWidget(group_network)

    parent_app.network_actions_layout.addStretch(1)
    scroll_area_actions.setWidget(network_actions_widget_container)
    left_column_layout.addWidget(scroll_area_actions)
    content_splitter_network.addWidget(left_column_widget)

    results_container_widget = QWidget()
    parent_app.network_results_main_layout = QVBoxLayout(results_container_widget)
    parent_app.network_results_main_layout.setContentsMargins(0,0,0,0)
    parent_app.stacked_widget_results_network = parent_app._create_results_display_area(
        "Kết quả Mạng", "NetworkResultTextEdit", "NetworkResultTable" # Đặt tên objectName khác nhau
    )
    parent_app.network_results_main_layout.addWidget(parent_app.stacked_widget_results_network, 1)
    content_splitter_network.addWidget(results_container_widget)
    content_splitter_network.setSizes([320, 430])