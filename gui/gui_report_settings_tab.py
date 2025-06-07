from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QLabel, QPushButton
)
from PyQt5.QtCore import Qt
import html
import re

# Import các hằng số từ gui_constants
from .gui_constants import APP_VERSION, APP_AUTHOR, APP_CONTACT_EMAIL, APP_DESCRIPTION

def create_report_settings_tab_content(parent_app):
    """
    Tạo nội dung cho tab Báo Cáo & Cài đặt.
    'parent_app' là instance của PcInfoAppQt.
    """
    layout = QVBoxLayout(parent_app.page_report_settings)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    layout.setAlignment(Qt.AlignTop)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_content_widget = QWidget()
    scroll_layout = QVBoxLayout(scroll_content_widget)
    scroll_layout.setAlignment(Qt.AlignTop)

    # Nút Xuất Báo Cáo PC
    parent_app.button_export_pc_report_tab = QPushButton("Xuất Báo Cáo Thông Tin PC")
    parent_app.button_export_pc_report_tab.setFont(parent_app.body_font) # Sử dụng font từ parent_app
    parent_app.button_export_pc_report_tab.setCursor(Qt.PointingHandCursor)
    parent_app.button_export_pc_report_tab.clicked.connect(parent_app.on_export_info_qt)
    parent_app.button_export_pc_report_tab.setObjectName("ExportReportButton")
    scroll_layout.addWidget(parent_app.button_export_pc_report_tab)

    title_label = QLabel("Công Cụ Hỗ Trợ PC")
    title_label.setFont(parent_app.h1_font) # Sử dụng font từ parent_app
    title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    title_label.setAlignment(Qt.AlignCenter)
    scroll_layout.addWidget(title_label)

    scroll_layout.addWidget(parent_app._create_info_section_qt(scroll_content_widget, "Phiên bản:", APP_VERSION))
    scroll_layout.addWidget(parent_app._create_info_section_qt(scroll_content_widget, "Người sáng lập:", APP_AUTHOR))
    scroll_layout.addWidget(parent_app._create_info_section_qt(scroll_content_widget, "Liên hệ:", APP_CONTACT_EMAIL))
    scroll_layout.addWidget(parent_app._create_info_section_qt(scroll_content_widget, "Giấy phép:", "Phần mềm nội bộ"))

    scroll_layout.addWidget(parent_app._create_info_section_qt(scroll_content_widget, "Mô tả & Chức năng:", APP_DESCRIPTION, is_html=True))

    scroll_area.setWidget(scroll_content_widget)
    layout.addWidget(scroll_area)