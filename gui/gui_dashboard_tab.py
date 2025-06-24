from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout, QLabel, QProgressBar, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
# Bạn có thể cần import thêm các hằng số hoặc hàm helper nếu chúng được sử dụng trực tiếp
# trong việc tạo UI của tab này và không được truyền từ PcInfoAppQt.
# Ví dụ: from .gui_qt import DEFAULT_FONT_FAMILY, H1_FONT_SIZE, BODY_FONT_SIZE (nếu cần)
from PyQt5.QtGui import QFont, QColor, QIcon

class PerformanceCard(QFrame):
    def __init__(self, icon_char, title, object_name_prefix=""):
        super().__init__()
        self.setObjectName(f"{object_name_prefix}Card")
        self.setProperty("cardType", object_name_prefix)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Header với icon và title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon_char)
        icon_label.setObjectName(f"{object_name_prefix}Icon")
        
        title_label = QLabel(title)
        title_label.setObjectName(f"{object_name_prefix}Title")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Giá trị chính
        self.value_label = QLabel("0%")
        self.value_label.setObjectName(f"{object_name_prefix}Value")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)
        
        # Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName(f"{object_name_prefix}Progress")
        layout.addWidget(self.progress_bar)
        
        # Chi tiết
        self.details_label = QLabel("Đang tải...")
        self.details_label.setObjectName(f"{object_name_prefix}Details")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)

        layout.addStretch()
        self.setLayout(layout)
    
    def update_value(self, new_value_text):
        self.value_label.setText(new_value_text)

    def update_details(self, new_details_text):
        self.details_label.setText(new_details_text)

    def update_progress(self, new_progress_value):
        self.progress_bar.setValue(new_progress_value)

class QuickActionButton(QPushButton):
    def __init__(self, text, icon_text, color):
        super().__init__()
        self.setText(f"{icon_text} {text}")
        self.setObjectName("ActionBtn") # For QSS styling
        self.setProperty("btnColor", color) # Custom property for QSS
        self.setFont(QFont("Segoe UI", 10)) # Set font here, QSS will override some properties
        self.setFixedHeight(40) # Set fixed height
    
    def darken_color(self, color, factor=0.2):
        # Simple color darkening logic (can be expanded for more precise control)
        # For now, use a simple mapping or direct manipulation if colors are known
        qcolor = QColor(color)
        darker_qcolor = qcolor.darker(100 + int(factor * 100)) # 100 means no change, 200 means twice as dark
        return darker_qcolor.name()
    # Override setStyleSheet to apply dynamic color
    def setStyleSheet(self, styleSheet):
        # This method is called by Qt when setting QSS.
        # We need to ensure our dynamic color is applied.
        # The actual styling is now handled in gui_qt.py's _apply_styles
        # using the 'btnColor' property.
        super().setStyleSheet(styleSheet)

def create_dashboard_tab_content(parent_app):
    """
    Tạo nội dung cho tab Dashboard.
    'parent_app' là instance của PcInfoAppQt để truy cập các thuộc tính/phương thức cần thiết
    (ví dụ: fonts, hằng số màu, hoặc các phương thức để kết nối signals).
    """
    # parent_app.page_dashboard là QWidget của tab, layout sẽ được đặt cho nó
    layout = QVBoxLayout(parent_app.page_dashboard) 
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(20)

    # Sử dụng QScrollArea để nội dung có thể cuộn khi cửa sổ nhỏ lại
    dashboard_scroll_area = QScrollArea() 
    dashboard_scroll_area.setWidgetResizable(True)
    dashboard_scroll_area.setObjectName("DashboardScrollArea")
    dashboard_scroll_area.setStyleSheet("QScrollArea { border: none; }")
    
    dashboard_content_widget = QWidget() # Widget chứa toàn bộ nội dung của scroll area
    dashboard_content_layout = QVBoxLayout(dashboard_content_widget)
    dashboard_content_layout.setSpacing(20)

    # --- Phần 1: Các thẻ thông tin (PerformanceCard) ---
    info_cards_grid_layout = QGridLayout()
    info_cards_grid_layout.setSpacing(20)
    
    # Lưu các card vào parent_app để dễ dàng cập nhật
    parent_app.cpu_card = PerformanceCard("🖥️", "Sử dụng CPU", "cpu")
    parent_app.ram_card = PerformanceCard("🧠", "Sử dụng RAM", "ram")
    parent_app.ssd_card = PerformanceCard("💾", "Sử dụng SSD", "ssd")
    parent_app.gpu_card = PerformanceCard("🎮", "Sử dụng GPU", "gpu")

    info_cards_grid_layout.addWidget(parent_app.cpu_card, 0, 0)
    info_cards_grid_layout.addWidget(parent_app.ram_card, 0, 1)
    info_cards_grid_layout.addWidget(parent_app.ssd_card, 1, 0)
    info_cards_grid_layout.addWidget(parent_app.gpu_card, 1, 1)
    dashboard_content_layout.addLayout(info_cards_grid_layout)

    # Phần "Tối ưu nhanh"
    quick_actions_widget = QWidget()
    quick_actions_widget.setObjectName("QuickActionsWidget")
    quick_actions_layout = QVBoxLayout(quick_actions_widget)
    
    quick_actions_title = QLabel("⚡ Tối Ưu Nhanh")
    quick_actions_title.setObjectName("QuickActionsTitle")
    quick_actions_layout.addWidget(quick_actions_title)

    parent_app.action_buttons_grid_layout = QGridLayout()
    parent_app.action_buttons_grid_layout.setSpacing(15)

    actions = [
        ("Dọn Dẹp Hệ Thống", "🗑️", "#ff6b35", parent_app.on_dashboard_cleanup_system_clicked),
        ("Tăng Tốc PC", "🚀", "#e74c3c", parent_app.on_dashboard_boost_pc_clicked),
        ("Quét Bảo Mật", "🛡️", "#3498db", parent_app.on_dashboard_security_scan_clicked),
        ("Cập Nhật Driver", "💿", "#1abc9c", parent_app.on_dashboard_update_drivers_clicked)
    ]

    for i, (text, icon, color, handler) in enumerate(actions):
        btn = QuickActionButton(text, icon, color) # QuickActionButton now handles its own QSS based on 'btnColor' property
        btn.clicked.connect(handler)
        setattr(parent_app, f"btn_dashboard_quick_action_{i}", btn) # Store button as an attribute
        parent_app.action_buttons_grid_layout.addWidget(btn, 0, i)
        parent_app.action_buttons_grid_layout.setColumnStretch(i, 1)

    quick_actions_layout.addLayout(parent_app.action_buttons_grid_layout)
    dashboard_content_layout.addWidget(quick_actions_widget) # Thêm phần Tối ưu nhanh vào layout chính
    dashboard_content_layout.addStretch(1)
    dashboard_content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)) # Push content to top

    dashboard_scroll_area.setWidget(dashboard_content_widget)
    layout.addWidget(dashboard_scroll_area)