from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout, QLabel, QProgressBar, QPushButton
)
from PyQt5.QtCore import Qt

# Bạn có thể cần import thêm các hằng số hoặc hàm helper nếu chúng được sử dụng trực tiếp
# trong việc tạo UI của tab này và không được truyền từ PcInfoAppQt.
# Ví dụ: from .gui_qt import DEFAULT_FONT_FAMILY, H1_FONT_SIZE, BODY_FONT_SIZE (nếu cần)

def create_dashboard_tab_content(parent_app):
    """
    Tạo nội dung cho tab Dashboard.
    'parent_app' là instance của PcInfoAppQt để truy cập các thuộc tính/phương thức cần thiết
    (ví dụ: fonts, hằng số màu, hoặc các phương thức để kết nối signals).
    """
    # parent_app.page_dashboard là QWidget của tab, layout sẽ được đặt cho nó
    layout = QVBoxLayout(parent_app.page_dashboard) 
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(15)

    dashboard_scroll_area = QScrollArea()
    dashboard_scroll_area.setWidgetResizable(True)
    dashboard_scroll_area.setObjectName("DashboardScrollArea")
    
    dashboard_content_widget = QWidget()
    dashboard_content_layout = QVBoxLayout(dashboard_content_widget)
    dashboard_content_layout.setSpacing(25)

    stats_grid_widget = QWidget()
    stats_grid_widget.setObjectName("StatsGridWidget")
    parent_app.stats_grid_layout = QGridLayout(stats_grid_widget) # Gán vào parent_app
    parent_app.stats_grid_layout.setSpacing(10)

    def create_hw_card_content_local(title_text, icon_char, object_name_prefix):
        card_widget = QWidget()
        card_widget.setObjectName(f"{object_name_prefix}Card")
        card_widget.setProperty("cardType", object_name_prefix)
        card_layout = QVBoxLayout(card_widget)

        stat_header_widget = QWidget()
        stat_header_layout = QHBoxLayout(stat_header_widget)
        stat_title_label = QLabel(title_text)
        stat_title_label.setObjectName(f"{object_name_prefix}Title")
        stat_header_layout.addWidget(stat_title_label, 1)
        
        stat_icon_label = QLabel(icon_char)
        stat_icon_label.setObjectName(f"{object_name_prefix}Icon")
        stat_icon_label.setFixedSize(36,36)
        stat_icon_label.setAlignment(Qt.AlignCenter)
        stat_header_layout.addWidget(stat_icon_label)
        card_layout.addWidget(stat_header_widget)

        hw_value_label = QLabel("0%") 
        hw_value_label.setObjectName(f"{object_name_prefix}Value")
        card_layout.addWidget(hw_value_label)

        hw_progress = QProgressBar()
        hw_progress.setRange(0, 100)
        hw_progress.setTextVisible(True)
        hw_progress.setFixedHeight(8)
        hw_progress.setObjectName(f"{object_name_prefix}Progress")
        hw_progress.setValue(0) 
        card_layout.addWidget(hw_progress)

        hw_details_label = QLabel("Đang tải...")
        hw_details_label.setObjectName(f"{object_name_prefix}Details")
        hw_details_label.setWordWrap(True)
        card_layout.addWidget(hw_details_label)
        return card_widget, hw_value_label, hw_progress, hw_details_label

    parent_app.card_cpu, parent_app.label_cpu_value, parent_app.progress_cpu, parent_app.label_cpu_details = create_hw_card_content_local("CPU Usage", "🖥️", "cpu")
    parent_app.stats_grid_layout.addWidget(parent_app.card_cpu, 0, 0)

    parent_app.card_ram, parent_app.label_ram_value, parent_app.progress_ram, parent_app.label_ram_details = create_hw_card_content_local("RAM Usage", "🧠", "ram")
    parent_app.stats_grid_layout.addWidget(parent_app.card_ram, 0, 1)

    parent_app.card_ssd, parent_app.label_ssd_value, parent_app.progress_ssd, parent_app.label_ssd_details = create_hw_card_content_local("SSD Usage", "💾", "ssd")
    parent_app.stats_grid_layout.addWidget(parent_app.card_ssd, 1, 0)

    parent_app.card_gpu, parent_app.label_gpu_value, parent_app.progress_gpu, parent_app.label_gpu_details = create_hw_card_content_local("GPU Usage", "🎮", "gpu")
    parent_app.stats_grid_layout.addWidget(parent_app.card_gpu, 1, 1)
    
    parent_app.stats_grid_layout.setColumnStretch(0, 1)
    parent_app.stats_grid_layout.setColumnStretch(1, 1)
    dashboard_content_layout.addWidget(stats_grid_widget)

    quick_actions_widget = QWidget()
    quick_actions_widget.setObjectName("QuickActionsWidget")
    quick_actions_layout = QVBoxLayout(quick_actions_widget)
    
    quick_actions_title = QLabel("⚡ Tối Ưu Nhanh")
    quick_actions_title.setObjectName("QuickActionsTitle")
    quick_actions_layout.addWidget(quick_actions_title)

    parent_app.action_buttons_grid_layout = QGridLayout()
    parent_app.action_buttons_grid_layout.setSpacing(15)

    actions = [
        ("btn_cleanup_system", "🧹 Dọn Dẹp Hệ Thống", parent_app.on_dashboard_cleanup_system_clicked),
        ("btn_boost_pc", "🚀 Tăng Tốc PC", parent_app.on_dashboard_boost_pc_clicked),
        ("btn_security_scan", "🛡️ Quét Bảo Mật", parent_app.on_dashboard_security_scan_clicked),
        ("btn_update_drivers", "🔄 Cập Nhật Driver", parent_app.on_dashboard_update_drivers_clicked)
    ]

    for i, (attr_name, text, handler) in enumerate(actions):
        btn = QPushButton(text)
        btn.setObjectName("ActionBtn")
        btn.clicked.connect(handler)
        setattr(parent_app, attr_name, btn) # Gán nút vào parent_app
        parent_app.action_buttons_grid_layout.addWidget(btn, 0, i)
        parent_app.action_buttons_grid_layout.setColumnStretch(i, 1)

    quick_actions_layout.addLayout(parent_app.action_buttons_grid_layout)
    dashboard_content_layout.addWidget(quick_actions_widget)
    dashboard_content_layout.addStretch(1)

    dashboard_scroll_area.setWidget(dashboard_content_widget)
    layout.addWidget(dashboard_scroll_area)