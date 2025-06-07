from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QGroupBox, QScrollArea, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt

def create_system_info_tab_content(parent_app):
    """
    Tạo nội dung cho tab Hệ Thống.
    'parent_app' là instance của PcInfoAppQt.
    """
    layout = QVBoxLayout(parent_app.page_system_info)
    layout.setSpacing(15)

    # --- User Info Frame (QGroupBox) ---
    group_user_info = QGroupBox("Thông tin người dùng")
    group_user_info.setFont(parent_app.h2_font)
    group_user_info.setObjectName("UserInfoGroup")
    layout.addWidget(group_user_info)
    
    user_info_grid_layout = QGridLayout(group_user_info)

    # Dòng 1: Tên và Phòng Ban
    user_info_grid_layout.addWidget(QLabel("Tên:"), 0, 0)
    parent_app.entry_name_qt = QLineEdit()
    parent_app.entry_name_qt.setFont(parent_app.body_font)
    user_info_grid_layout.addWidget(parent_app.entry_name_qt, 0, 1)

    user_info_grid_layout.addWidget(QLabel("Phòng Ban:"), 0, 2)
    parent_app.entry_department_qt = QLineEdit()
    parent_app.entry_department_qt.setFont(parent_app.body_font)
    user_info_grid_layout.addWidget(parent_app.entry_department_qt, 0, 3)

    # Dòng 1: Vị Trí Tầng và ô nhập tầng tùy chỉnh
    user_info_grid_layout.addWidget(QLabel("Vị Trí:"), 1, 0)
    parent_app.combo_floor_qt = QComboBox()
    parent_app.combo_floor_qt.setFont(parent_app.body_font)
    parent_app.combo_floor_qt.addItems(["Tầng G", "Lầu 1", "Lầu 2", "Khác"])
    parent_app.combo_floor_qt.currentIndexChanged.connect(parent_app.on_floor_change_qt)
    user_info_grid_layout.addWidget(parent_app.combo_floor_qt, 1, 1)

    parent_app.entry_custom_floor_label_qt = QLabel("Vị trí khác:")
    parent_app.entry_custom_floor_label_qt.setFont(parent_app.h2_font)
    parent_app.entry_custom_floor_qt = QLineEdit()
    parent_app.entry_custom_floor_qt.setFont(parent_app.body_font)
    # Sẽ được thêm/xóa bởi on_floor_change_qt

    # Dòng 2: Chức Vụ và Checkbox Ghi chú
    user_info_grid_layout.addWidget(QLabel("Chức Vụ:"), 2, 0)
    parent_app.entry_position_qt = QLineEdit()
    parent_app.entry_position_qt.setFont(parent_app.body_font)
    user_info_grid_layout.addWidget(parent_app.entry_position_qt, 2, 1)

    parent_app.checkbox_show_notes = QCheckBox("Thêm ghi chú")
    parent_app.checkbox_show_notes.setFont(parent_app.body_font)
    parent_app.checkbox_show_notes.toggled.connect(parent_app.toggle_notes_visibility)
    user_info_grid_layout.addWidget(parent_app.checkbox_show_notes, 2, 2, 1, 2)

    # Dòng 3: Ghi chú (ẩn/hiện)
    parent_app.label_notes_qt = QLabel("Ghi chú:")
    parent_app.label_notes_qt.setFont(parent_app.body_font)
    parent_app.text_notes_qt = QTextEdit()
    parent_app.text_notes_qt.setFont(parent_app.body_font)
    parent_app.text_notes_qt.setFixedHeight(60)
    user_info_grid_layout.addWidget(parent_app.label_notes_qt, 3, 0, Qt.AlignTop)
    user_info_grid_layout.addWidget(parent_app.text_notes_qt, 3, 1, 1, 3)

    parent_app.toggle_notes_visibility(False) # Ẩn ghi chú ban đầu
    parent_app.on_floor_change_qt() # Initial state for custom floor

    user_info_grid_layout.setColumnStretch(1, 1)
    user_info_grid_layout.setColumnStretch(3, 1)

    # --- System Info Display (Card Layout) ---
    cards_scroll_area = QScrollArea()
    cards_scroll_area.setWidgetResizable(True)
    cards_scroll_area.setObjectName("CardsScrollArea")
    
    cards_container_widget = QWidget()
    parent_app.home_cards_layout = QGridLayout(cards_container_widget)
    parent_app.home_cards_layout.setSpacing(15)

    # Tạo các card thông tin (sử dụng _create_info_card từ parent_app)
    parent_app.card_general_info = parent_app._create_info_card("Thông tin Chung")
    parent_app.card_os_info = parent_app._create_info_card("Hệ Điều Hành")
    parent_app.card_cpu_info = parent_app._create_info_card("CPU")
    parent_app.card_ram_info = parent_app._create_info_card("RAM")
    parent_app.card_mainboard_info = parent_app._create_info_card("Mainboard")
    parent_app.card_disks_info = parent_app._create_info_card("Ổ Đĩa")
    parent_app.card_gpus_info = parent_app._create_info_card("Card Đồ Họa (GPU)")
    parent_app.card_screens_info = parent_app._create_info_card("Màn Hình")
    parent_app.card_temperatures_info = parent_app._create_info_card("Nhiệt Độ Hệ Thống")

    parent_app.home_cards_layout.addWidget(parent_app.card_general_info, 0, 0)
    parent_app.home_cards_layout.addWidget(parent_app.card_os_info, 0, 1)
    parent_app.home_cards_layout.addWidget(parent_app.card_cpu_info, 1, 0)
    parent_app.home_cards_layout.addWidget(parent_app.card_ram_info, 1, 1)
    parent_app.home_cards_layout.addWidget(parent_app.card_mainboard_info, 2, 0)
    parent_app.home_cards_layout.addWidget(parent_app.card_disks_info, 2, 1)
    parent_app.home_cards_layout.addWidget(parent_app.card_gpus_info, 3, 0, 1, 2)
    parent_app.home_cards_layout.addWidget(parent_app.card_screens_info, 4, 0) 
    parent_app.home_cards_layout.addWidget(parent_app.card_temperatures_info, 4, 1)

    cards_scroll_area.setWidget(cards_container_widget)
    layout.addWidget(cards_scroll_area, 1)