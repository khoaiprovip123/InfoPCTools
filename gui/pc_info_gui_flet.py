import flet as ft
from flet.core.icons import Icons
from flet.core.colors import Colors
import os
import sys
import threading
import logging
from PIL import Image
from datetime import datetime
import win32com.client

# Import các hàm cần thiết từ core
from core.pc_info_functions import (
    get_detailed_system_information, NOT_AVAILABLE,
    _connect_wmi, ERROR_WMI_CONNECTION,
    get_disk_partitions_usage,
    generate_battery_report,
    check_windows_activation_status,
    open_resource_monitor,
    clear_temporary_files,
    get_recent_event_logs,
    get_installed_software_versions,
    get_wifi_connection_info,
    get_system_temperatures,
    get_running_processes,
    reset_internet_connection,
    run_sfc_scan,
    update_all_winget_packages,
    run_windows_defender_scan,
    update_windows_defender_definitions,
    get_firewall_status,
    toggle_firewall,
    get_startup_programs, run_ping_test, create_system_restore_point
)
from core.pc_info_manager import (
    validate_user_input,
    generate_filename,
    save_text_to_file,
    format_pc_info_to_string,
    format_system_details_to_string
)

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối của resource (ảnh, file...) để tương thích với PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

def format_user_info_for_display(user_info):
    """
    Định dạng thông tin người dùng thành chuỗi, bao gồm cả ghi chú.
    """
    lines = ["--- THÔNG TIN NGƯỜI DÙNG ---"]
    lines.append(f"  Tên người dùng: {user_info.get('Name', NOT_AVAILABLE)}")
    lines.append(f"  Bộ phận: {user_info.get('Department', NOT_AVAILABLE)}")
    lines.append(f"  Tầng: {user_info.get('Floor', NOT_AVAILABLE)}")
    position = user_info.get('Position')
    lines.append(f"  Chức vụ: {position if position else NOT_AVAILABLE}")
    notes = user_info.get('Notes')
    if notes:
        indented_notes = notes.replace('\n', '\n    ')
        lines.append(f"  Ghi chú:\n    {indented_notes}")
    return "\n".join(lines)

class PcInfoAppFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Thông Tin Cấu Hình PC"
        self.page.window_width = 850
        self.page.window_height = 750
        self.page.window_resizable = True
        self.page.vertical_alignment = ft.CrossAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.theme_mode = ft.ThemeMode.SYSTEM # Light, Dark, SYSTEM

        self.pc_info_dict = None
        self.formatted_pc_info_string = "Chưa lấy thông tin."

        self._load_logo()
        self._create_widgets()

        # Start initial info fetch after widgets are created
        self.fetch_pc_info_threaded()

    def _load_logo(self):
        try:
            logo_relative_path = os.path.join("assets", "logo", "hpc-logo.png")
            logo_path = resource_path(logo_relative_path)
            if os.path.exists(logo_path):
                self.logo_image_asset = logo_path # Flet can directly use image paths
            else:
                logging.warning(f"Không tìm thấy file logo tại: {logo_path}")
                self.logo_image_asset = None
        except Exception as e:
            logging.error(f"Lỗi khi tải logo: {e}", exc_info=True)
            self.logo_image_asset = None

    def _create_widgets(self):
        # Top Row for Logo and Title
        self.title_row = ft.Row(
            controls=[
                ft.Text("Công Cụ Hỗ Trợ PC", size=30, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        if self.logo_image_asset:
            self.title_row.controls.append(ft.Image(src=self.logo_image_asset, width=70, height=70))
            self.title_row.controls.reverse() # Put logo on the right

        # Navigation Rail (Menu Tabs)
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=False,
            min_width=50,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=Icons.HOME_OUTLINED,
                    selected_icon=Icons.HOME,
                    label="Trang Chủ",
                ),
                ft.NavigationRailDestination(
                    icon=Icons.HANDYMAN_OUTLINED,
                    selected_icon=Icons.HANDYMAN,
                    label="Tiện ích",
                ),
                ft.NavigationRailDestination(
                    icon=Icons.BUILD_OUTLINED,
                    selected_icon=Icons.BUILD,
                    label="Sửa Lỗi Hệ Thống",
                ),
            ],
            on_change=self._on_navigation_change,
        )

        # Content Area for each tab
        self.home_view = ft.Column([], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        self.utilities_view = ft.Column([], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        self.fixes_view = ft.Column([], expand=True, scroll=ft.ScrollMode.ADAPTIVE)

        self.views = {
            0: self.home_view,
            1: self.utilities_view,
            2: self.fixes_view,
        }

        self.content_area = ft.Column(
            controls=[
                self.views[self.navigation_rail.selected_index]
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
        )

        # Global Buttons
        self.export_button = ft.ElevatedButton(
            text="Xuất Dữ liệu PC",
            icon=Icons.SAVE,
            on_click=self.on_export_info,
            disabled=True,
        )
        self.exit_button = ft.ElevatedButton(
            text="Thoát Ứng Dụng",
            icon=Icons.EXIT_TO_APP,
            on_click=lambda e: self.page.window_destroy(),
            style=ft.ButtonStyle(bgcolor={ft.ControlState.DEFAULT: Colors.RED_500}),
        )

        self.global_buttons_row = ft.Row(
            controls=[
                self.export_button,
                self.exit_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=self.page.window_width - 40, # Adjust width based on window size
        )

        self.page.add(
            self.title_row,
            ft.Divider(),
            ft.Row(
                controls=[
                    self.navigation_rail,
                    ft.VerticalDivider(width=1),
                    self.content_area,
                ],
                expand=True,
            ),
            ft.Divider(),
            self.global_buttons_row,
        )

        # Initial content for views
        self._create_home_view(self.home_view)
        self._create_utilities_view(self.utilities_view)
        self._create_fixes_view(self.fixes_view)

        self.page.update()
        self.on_floor_change(None) # Initial call to set visibility

    def _on_navigation_change(self, e):
        self.content_area.controls.clear()
        self.content_area.controls.append(self.views[e.control.selected_index])
        self.page.update()

    def _create_home_view(self, view_control: ft.Column):
        # --- User Info Section ---
        user_info_controls = []

        self.entry_name = ft.TextField(label="Tên:", expand=True)
        user_info_controls.append(ft.Row([ft.Text("Tên:"), self.entry_name]))

        self.entry_department = ft.TextField(label="Phòng Ban:", expand=True)
        user_info_controls.append(ft.Row([ft.Text("Phòng Ban:"), self.entry_department]))

        floor_options = [ft.dropdown.Option(text) for text in ["Tầng G", "Lầu 1", "Lầu 2", "Khác"]]
        self.combo_floor = ft.Dropdown(
            label="Vị Trí Tầng:",
            options=floor_options,
            value=floor_options[0].text,
            on_change=self.on_floor_change,
            expand=True
        )
        self.entry_custom_floor = ft.TextField(label="Nhập vị trí hiện tại:", visible=False, expand=True)
        self.floor_row = ft.Row([ft.Text("Vị Trí Tầng:"), self.combo_floor, self.entry_custom_floor])
        user_info_controls.append(self.floor_row)

        self.entry_position = ft.TextField(label="Chức Vụ:", expand=True)
        user_info_controls.append(ft.Row([ft.Text("Chức Vụ:"), self.entry_position]))

        self.text_notes = ft.TextField(label="Ghi chú:", multiline=True, min_lines=3, max_lines=5, expand=True)
        user_info_controls.append(ft.Row([ft.Text("Ghi chú:"), self.text_notes], vertical_alignment=ft.CrossAxisAlignment.START))

        frame_user = ft.Container(
            content=ft.Column(user_info_controls),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
        )
        view_control.controls.append(ft.Text("Thông tin người dùng (cho file xuất)", size=16, weight=ft.FontWeight.BOLD))
        view_control.controls.append(frame_user)

        # --- System Info Display for Home Tab ---
        self.text_home_info = ft.TextField(
            label="Thông tin hệ thống",
            multiline=True,
            read_only=True,
            min_lines=15,
            max_lines=20,
            expand=True,
            text_style=ft.TextStyle(font_family="Consolas", size=12),
            value="Đang tải thông tin ban đầu...",
        )
        frame_home_results = ft.Container(
            content=self.text_home_info,
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            expand=True,
        )
        view_control.controls.append(frame_home_results)

        # --- Button to refresh Home tab info ---
        self.button_refresh_home = ft.ElevatedButton(
            text="Làm mới",
            icon=Icons.REFRESH,
            on_click=self.fetch_pc_info_threaded,
            width=180,
        )
        view_control.controls.append(self.button_refresh_home)
        self.page.update()

    def _create_utilities_view(self, view_control: ft.Column):
        # Main frame for utilities tab
        utilities_main_row = ft.Row(
            controls=[],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        view_control.controls.append(utilities_main_row)

        # --- Left Column: Action Buttons ---
        actions_column_frame = ft.Column(
            controls=[],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=2, # Corresponds to weight=2
        )
        utilities_main_row.controls.append(actions_column_frame)

        utility_button_width = 250 # Adjusted width for Flet buttons

        # --- Group: Bảo mật & Virus ---
        frame_security = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Bảo mật & Virus", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(text="Quét Virus Nhanh", on_click=self.run_defender_quick_scan, width=utility_button_width),
                    ft.ElevatedButton(text="Quét Virus Toàn Bộ", on_click=self.run_defender_full_scan, width=utility_button_width),
                    ft.ElevatedButton(text="Cập Nhật Định Nghĩa Virus", on_click=self.run_defender_update, width=utility_button_width),
                    ft.ElevatedButton(text="Kiểm Tra Trạng Thái Tường Lửa", on_click=self.check_firewall_status_gui, width=utility_button_width),
                    ft.ElevatedButton(text="Bật Tường Lửa (Tất cả Profile)", on_click=self.enable_firewall_gui, width=utility_button_width),
                    ft.ElevatedButton(text="Tắt Tường Lửa (Tất cả Profile)", on_click=self.disable_firewall_gui, width=utility_button_width),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            width=utility_button_width + 30, # Adjust container width
        )
        actions_column_frame.controls.append(frame_security)

        # --- Group: Thông tin & Chẩn đoán Hệ thống ---
        frame_diagnostics = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Thông tin & Chẩn đoán", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(text="Xem Dung Lượng Ổ Đĩa", on_click=self.show_disk_usage, width=utility_button_width),
                    ft.ElevatedButton(text="Tạo Báo Cáo Pin (Laptop)", on_click=self.create_battery_report, width=utility_button_width),
                    ft.ElevatedButton(text="Kiểm tra kích hoạt Windows", on_click=self.run_check_windows_activation, width=utility_button_width),
                    ft.ElevatedButton(text="Xem Event Log Gần Đây", on_click=self.show_recent_event_logs, width=utility_button_width),
                    ft.ElevatedButton(text="Kiểm Tra Phiên Bản Phần Mềm", on_click=self.show_installed_software, width=utility_button_width),
                    ft.ElevatedButton(text="Kiểm Tra Kết Nối Wifi", on_click=self.show_wifi_info, width=utility_button_width),
                    ft.ElevatedButton(text="Kiểm Tra Nhiệt Độ Hệ Thống", on_click=self.show_system_temperatures, width=utility_button_width),
                    ft.ElevatedButton(text="Liệt Kê Tiến Trình Đang Chạy", on_click=self.show_running_processes, width=utility_button_width),
                    ft.ElevatedButton(text="Ứng Dụng Người Dùng Đã Cài", on_click=self.show_user_installed_applications, width=utility_button_width),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            width=utility_button_width + 30, # Adjust container width
        )
        actions_column_frame.controls.append(frame_diagnostics)

        # --- Right Column: Utilities Results Display ---
        results_column_frame = ft.Column(
            controls=[],
            expand=5, # Corresponds to weight=5
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        utilities_main_row.controls.append(results_column_frame)

        self.utilities_results_text = ft.TextField(
            label="Kết quả Tiện ích",
            multiline=True,
            read_only=True,
            min_lines=10,
            max_lines=20,
            expand=True,
            text_style=ft.TextStyle(font_family="Consolas", size=12),
            value="Kết quả của tiện ích sẽ hiển thị ở đây.",
        )
        frame_text_results_utils = ft.Container(
            content=self.utilities_results_text,
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            expand=True,
        )
        results_column_frame.controls.append(frame_text_results_utils)

        # Frame for buttons below results
        utils_results_buttons_row = ft.Row(
            controls=[
                ft.ElevatedButton(text="Ping (google.com)", on_click=self.run_ping_google, width=180),
                ft.ElevatedButton(text="Lưu Kết Quả", on_click=lambda e: self.save_tab_result(self.utilities_results_text, "KetQua_TienIch"), width=150, disabled=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
        )
        results_column_frame.controls.append(utils_results_buttons_row)
        self.page.update()

    def _create_fixes_view(self, view_control: ft.Column):
        fixes_main_row = ft.Row(
            controls=[],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        view_control.controls.append(fixes_main_row)

        actions_column_frame_fixes = ft.Column(
            controls=[],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=2,
        )
        fixes_main_row.controls.append(actions_column_frame_fixes)

        fix_button_width = 250

        # --- Group: Dọn dẹp & Tối ưu ---
        frame_cleanup = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Dọn dẹp & Tối ưu", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(text="Xóa File Tạm & Dọn Dẹp", on_click=self.run_clear_temp_files, width=fix_button_width),
                    ft.ElevatedButton(text="Mở Resource Monitor", on_click=self.run_open_resource_monitor, width=fix_button_width),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            width=fix_button_width + 30,
        )
        actions_column_frame_fixes.controls.append(frame_cleanup)

        # --- Group: Sửa lỗi Hệ thống ---
        frame_system_fix = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Sửa lỗi Hệ thống", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(text="Reset Kết Nối Internet", on_click=self.run_reset_internet_connection, width=fix_button_width),
                    ft.ElevatedButton(text="Chạy SFC Scan", on_click=self.run_sfc_scan_command, width=fix_button_width),
                    ft.ElevatedButton(text="Tạo Điểm Khôi Phục Hệ Thống", on_click=self.run_create_restore_point, width=fix_button_width),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            width=fix_button_width + 30,
        )
        actions_column_frame_fixes.controls.append(frame_system_fix)

        # --- Group: Cập nhật ---
        frame_updates = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Cập nhật", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(text="Quản Lý Khởi Động Cùng Windows", on_click=self.show_startup_programs, width=fix_button_width),
                    ft.ElevatedButton(text="Cập Nhật Phần Mềm (Winget)", on_click=self.run_winget_update_all, width=fix_button_width),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            width=fix_button_width + 30,
        )
        actions_column_frame_fixes.controls.append(frame_updates)

        # --- Right Column: Fixes Results Display ---
        results_column_frame_fixes = ft.Column(
            controls=[],
            expand=5,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        fixes_main_row.controls.append(results_column_frame_fixes)

        self.fixes_results_text = ft.TextField(
            label="Kết quả Tác vụ Sửa lỗi",
            multiline=True,
            read_only=True,
            min_lines=10,
            max_lines=20,
            expand=True,
            text_style=ft.TextStyle(font_family="Consolas", size=12),
            value="Chọn một tác vụ để thực hiện.",
        )
        frame_text_results_fixes = ft.Container(
            content=self.fixes_results_text,
            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
            border_radius=ft.border_radius.all(10),
            expand=True,
        )
        results_column_frame_fixes.controls.append(frame_text_results_fixes)

        self.button_save_fix_result = ft.ElevatedButton(
            text="Lưu Kết Quả Sửa Lỗi",
            on_click=lambda e: self.save_tab_result(self.fixes_results_text, "KetQua_SuaLoi"),
            width=180,
            disabled=True,
        )
        results_column_frame_fixes.controls.append(self.button_save_fix_result)
        self.page.update()

    def on_floor_change(self, e):
        """Show/hide custom floor entry based on combobox selection."""
        if self.combo_floor.value == "Khác":
            self.entry_custom_floor.visible = True
        else:
            self.entry_custom_floor.visible = False
            self.entry_custom_floor.value = ""
        self.floor_row.update() # Update the row containing these controls

    def _update_display_widget(self, text_control: ft.TextField, content: str):
        text_control.value = content
        if "Lỗi" in content or "Error" in content or "Không thể" in content:
            text_control.text_style = ft.TextStyle(color=ft.Colors.RED_500)
        else:
            text_control.text_style = ft.TextStyle(color=ft.Colors.ON_SURFACE)
        text_control.update()

    def _toggle_buttons(self, enable_refresh_home=True, enable_export_home=False, enable_save_utility=False, enable_save_fix=False):
        # Flet buttons are disabled by setting disabled=True/False
        self.export_button.disabled = not enable_export_home
        if hasattr(self, 'button_refresh_home'):
            self.button_refresh_home.disabled = not enable_refresh_home
        
        # Handle save utility button
        if hasattr(self, 'button_save_utility_result'):
            self.button_save_utility_result.disabled = not enable_save_utility
        # Handle save fix button
        if hasattr(self, 'button_save_fix_result'):
            self.button_save_fix_result.disabled = not enable_save_fix

        self.page.update()

    def _fetch_task(self):
        try:
            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, "Đang lấy thông tin, vui lòng chờ...")
            self._toggle_buttons(enable_refresh_home=False, enable_export_home=False)

            self.pc_info_dict = get_detailed_system_information()

            home_info_data = self.pc_info_dict.get("SystemInformation", {"PC": {"Lỗi": "Không có dữ liệu SystemInformation"}})
            self.formatted_pc_info_string = format_system_details_to_string(home_info_data)

            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, self.formatted_pc_info_string)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=True)

        except Exception as e:
            error_msg = f"Lỗi khi lấy thông tin:\n{e}"
            logging.exception("Lỗi trong luồng lấy thông tin PC:")
            self.pc_info_dict = None
            self.formatted_pc_info_string = error_msg
            if hasattr(self, 'text_home_info'):
                self._update_display_widget(self.text_home_info, error_msg)
            self._toggle_buttons(enable_refresh_home=True, enable_export_home=False)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi: {error_msg}"), open=True)
            self.page.update()

    def fetch_pc_info_threaded(self):
        fetch_thread = threading.Thread(target=self._fetch_task, daemon=True)
        fetch_thread.start()

    def on_export_info(self, e):
        """Handles the 'Export File' button click."""
        if not self.pc_info_dict:
            self.page.snack_bar = ft.SnackBar(ft.Text("Chưa có thông tin. Vui lòng đợi hoặc làm mới."), open=True)
            self.page.update()
            return

        try:
            # 1. Get user info from GUI
            user_name = self.entry_name.value.strip()
            department = self.entry_department.value.strip()
            floor_selection = self.combo_floor.value
            custom_floor = self.entry_custom_floor.value.strip() if floor_selection == "Khác" else ""
            position = self.entry_position.value.strip()
            notes = self.text_notes.value.strip()
            final_floor = custom_floor if floor_selection == "Khác" and custom_floor else floor_selection

            user_info = {
                "Name": user_name,
                "Department": department,
                "Floor": final_floor,
                "Position": position,
                "Notes": notes
            }

            # 2. Validate user input
            validate_user_input(user_info) # Raises ValueError on failure

            # 3. PC info is already in self.pc_info_dict
            # 4. Format the *entire* pc_info_dict for the file
            full_formatted_pc_info_for_file = format_pc_info_to_string(self.pc_info_dict)

            # 5. Format user info for saving
            formatted_user_text = format_user_info_for_display(user_info)
            # 6. Combine content for saving
            full_content_to_save = f"{formatted_user_text}\n\n{full_formatted_pc_info_for_file}"

            # 7. Generate filename
            filename = generate_filename(user_info, self.pc_info_dict)

            # 8. Determine save path
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Exports_Formatted_TXT")
            file_path = os.path.join(save_dir, filename)

            # 9. Save the file
            save_text_to_file(full_content_to_save, file_path) # Raises exceptions on failure

            # 10. Show success message
            network_instruction = "\\\\pc-it-08\\Tools\\User"
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Thông tin đã được lưu thành công vào file:\n{file_path}\n\n" +
                         f"Vui lòng copy file này và dán vào thư mục bằng cách nhấn Win+R " +
                         f"và nhập: {network_instruction}"),
                open=True,
            )
            self.page.update()

        except ValueError as ve: # Validation error
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Thiếu thông tin: {str(ve)}"), open=True)
            self.page.update()
        except (IOError, RuntimeError) as save_e: # File saving error
             self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi Lưu File: Không thể lưu file:\n{save_e}"), open=True)
             self.page.update()
        except Exception as e: # Other unexpected errors
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi Không Xác Định: Đã xảy ra lỗi không mong muốn khi xuất file: {e}"), open=True)
            self.page.update()
            logging.exception("Lỗi không xác định khi xuất file:")

    def save_tab_result(self, text_control: ft.TextField, default_prefix="KetQua"):
        """Saves the content of a Flet TextField widget to a .txt file."""
        content = text_control.value.strip()
        if not content or content == "Kết quả của tiện ích sẽ hiển thị ở đây." or content == "Chọn một tác vụ để thực hiện." or "Đang thực hiện:" in content:
            self.page.snack_bar = ft.SnackBar(ft.Text("Không có kết quả để lưu hoặc tác vụ đang chạy."), open=True)
            self.page.update()
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{default_prefix}_{timestamp}.txt"
            
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Tool_Results")
            file_path = os.path.join(save_dir, filename)

            save_text_to_file(content, file_path)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Kết quả đã được lưu vào:\n{file_path}"), open=True)
            self.page.update()

        except (IOError, RuntimeError) as save_e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi Lưu File: Không thể lưu file kết quả:\n{save_e}"), open=True)
            self.page.update()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Lỗi Không Xác Định: Đã xảy ra lỗi không mong muốn khi lưu kết quả: {e}"), open=True)
            self.page.update()
            logging.exception("Lỗi không xác định khi lưu kết quả tab:")

    def _format_task_result_for_display(self, result_data):
        if isinstance(result_data, list):
            formatted_items = []
            for item in result_data:
                if isinstance(item, dict):
                    item_str = "\n".join([f"  {k}: {v}" for k, v in item.items()])
                    formatted_items.append(item_str)
                else:
                    formatted_items.append(str(item))
            final_display_text = "\n---\n".join(formatted_items)
            if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về."
        elif isinstance(result_data, dict):
            if "message" in result_data and "status" in result_data:
                final_display_text = f"Trạng thái: {result_data.get('status', 'N/A')}\nThông điệp: {result_data['message']}"
                if "details" in result_data and result_data['details']:
                    details_content = result_data['details']
                    if isinstance(details_content, dict):
                        details_str = "\n".join([f"  {k_detail}: {v_detail}" for k_detail, v_detail in details_content.items() if k_detail != 'errors_list'])
                        if 'errors_list' in details_content and details_content['errors_list']:
                            details_str += f"\n  Lỗi chi tiết:\n    " + "\n    ".join(details_content['errors_list'][:5]) + ("..." if len(details_content['errors_list']) > 5 else "")
                        final_display_text += f"\n\nChi tiết:\n{details_str}"
                    else:
                        final_display_text += f"\n\nChi tiết:\n{details_content}"
                if "path" in result_data and result_data['path']: final_display_text += f"\n\nĐường dẫn file: {result_data['path']}"
            else:
                final_display_text = "\n".join([f"{k}: {v}" for k, v in result_data.items()])
                if not final_display_text: final_display_text = "Tác vụ hoàn thành, không có dữ liệu trả về (dict rỗng)."
        else:
            final_display_text = str(result_data) if result_data is not None else "Tác vụ hoàn thành, không có dữ liệu trả về."

        return final_display_text

    def _run_task_in_thread(self, target_text_control: ft.TextField, task_function, needs_wmi=False, *task_args):
        self._update_display_widget(target_text_control, f"Đang thực hiện: {task_function.__name__}...")
        # Disable save button for this tab (will be handled in view classes)

        def task_wrapper():
            wmi_service_local = None
            com_initialized_local = False
            result_data = None

            try:
                if needs_wmi:
                    wmi_service_local, com_initialized_local = _connect_wmi()
                    if not wmi_service_local:
                        result_data = {"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kết nối WMI cho tác vụ này."}
                    else:
                        result_data = task_function(wmi_service_local, *task_args)
                else:
                    result_data = task_function(*task_args)

                self._update_display_widget(target_text_control, self._format_task_result_for_display(result_data))
            except Exception as e:
                logging.exception(f"Lỗi khi chạy tiện ích {task_function.__name__}:")
                self._update_display_widget(target_text_control, f"Lỗi khi thực hiện {task_function.__name__}:\n{e}")
            finally:
                if com_initialized_local:
                    try:
                        win32com.client.pythoncom.CoUninitialize()
                        logging.info(f"Đã giải phóng COM cho tác vụ {task_function.__name__}.")
                    except Exception as com_e:
                        logging.error(f"Lỗi khi giải phóng COM cho tác vụ {task_function.__name__}: {com_e}")
                # Re-enable save button for this tab (will be handled in view classes)

        threading.Thread(target=task_wrapper, daemon=True).start()

    # Handlers for Utilities Tab (will be moved to a separate class later)
    def show_disk_usage(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_disk_partitions_usage, needs_wmi=True)

    def create_battery_report(self, e):
        self._run_task_in_thread(self.utilities_results_text, generate_battery_report)

    def run_check_windows_activation(self, e):
        self._run_task_in_thread(self.utilities_results_text, check_windows_activation_status)

    def show_recent_event_logs(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_recent_event_logs, needs_wmi=True)

    def show_installed_software(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_installed_software_versions, needs_wmi=True)

    def show_wifi_info(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_wifi_connection_info)

    def show_system_temperatures(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_system_temperatures, needs_wmi=True)

    def show_running_processes(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_running_processes)

    def show_user_installed_applications(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_installed_software_versions, needs_wmi=False)

    def run_ping_google(self, e):
        self._run_task_in_thread(self.utilities_results_text, run_ping_test, False, "google.com", 4)

    def run_defender_quick_scan(self, e):
        self._run_task_in_thread(self.utilities_results_text, run_windows_defender_scan, False, "QuickScan")

    def run_defender_full_scan(self, e):
        self._run_task_in_thread(self.utilities_results_text, run_windows_defender_scan, False, "FullScan")

    def run_defender_update(self, e):
        self._run_task_in_thread(self.utilities_results_text, update_windows_defender_definitions)

    def check_firewall_status_gui(self, e):
        self._run_task_in_thread(self.utilities_results_text, get_firewall_status)

    def enable_firewall_gui(self, e):
        def confirm_enable(e):
            if e.control.text == "Yes":
                self._run_task_in_thread(self.utilities_results_text, toggle_firewall, False, True)
            self.page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Xác nhận Bật Tường lửa"),
            content=ft.Text("Bạn có chắc chắn muốn BẬT Windows Firewall cho tất cả các profile không?"),
            actions=[
                ft.ElevatedButton("No", on_click=confirm_enable),
                ft.ElevatedButton("Yes", on_click=confirm_enable),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def disable_firewall_gui(self, e):
        def confirm_disable(e):
            if e.control.text == "Yes":
                self._run_task_in_thread(self.utilities_results_text, toggle_firewall, False, False)
            self.page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("XÁC NHẬN TẮT TƯỜNG LỬA"),
            content=ft.Text("CẢNH BÁO: Tắt tường lửa có thể khiến máy tính của bạn dễ bị tấn công.\nBạn có chắc chắn muốn TẮT Windows Firewall cho tất cả các profile không?"),
            actions=[
                ft.ElevatedButton("No", on_click=confirm_disable),
                ft.ElevatedButton("Yes", on_click=confirm_disable, style=ft.ButtonStyle(bgcolor={ft.MaterialState.DEFAULT: ft.Colors.RED_500})),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    # Handlers for Fixes Tab (will be moved to a separate class later)
    def run_clear_temp_files(self, e):
        self._run_task_in_thread(self.fixes_results_text, clear_temporary_files)

    def run_open_resource_monitor(self, e):
        self._run_task_in_thread(self.fixes_results_text, open_resource_monitor)

    def run_reset_internet_connection(self, e):
        self._run_task_in_thread(self.fixes_results_text, reset_internet_connection)

    def run_sfc_scan_command(self, e):
        self._run_task_in_thread(self.fixes_results_text, run_sfc_scan)

    def run_winget_update_all(self, e):
        self._run_task_in_thread(self.fixes_results_text, update_all_winget_packages)

    def show_startup_programs(self, e):
        self._run_task_in_thread(self.fixes_results_text, get_startup_programs)

    def run_create_restore_point(self, e):
        self._run_task_in_thread(self.fixes_results_text, create_system_restore_point)

def main(page: ft.Page):
    PcInfoAppFlet(page)

if __name__ == "__main__":
    ft.app(target=main)
