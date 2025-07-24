import flet as ft
import os
import sys
import threading
import logging
from datetime import datetime
import win32com.client

# Add the project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
from gui.flet_dashboard import Dashboard

# --- Cấu hình Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối của resource để tương thích với PyInstaller. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

class ModernApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.results_text_field = self.create_results_text_field()
        self.build_layout()
        self.dashboard = self.content_area.controls[0]
        self.timer = ft.Timer(2, self.dashboard.update_dashboard)
        self.page.overlay.append(self.timer)
        self.timer.start()

    def setup_page(self):
        self.page.title = "PC Support Tool"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 900
        self.page.window_min_height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_GREY)
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def create_results_text_field(self):
        return ft.TextField(
            label="Kết quả",
            multiline=True,
            read_only=True,
            min_lines=15,
            expand=True,
            border_color=ft.Colors.BLUE_GREY_800,
            text_style=ft.TextStyle(font_family="Consolas", size=12),
            value="Chào mừng bạn đến với Công cụ Hỗ trợ PC. Kết quả các tác vụ sẽ hiển thị ở đây.",
        )

    def build_layout(self):
        self.main_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Dashboard", icon=ft.Icons.DASHBOARD_ROUNDED),
                ft.Tab(text="Thông tin hệ thống", icon=ft.Icons.INFO_ROUNDED),
                ft.Tab(text="Bảo mật", icon=ft.Icons.SECURITY_ROUNDED),
                ft.Tab(text="Internet", icon=ft.Icons.WIFI_ROUNDED),
                ft.Tab(text="Tiện ích", icon=ft.Icons.CONSTRUCTION_ROUNDED),
                ft.Tab(text="Cài đặt", icon=ft.Icons.SETTINGS_ROUNDED),
            ],
            expand=True,
        )

        header_row = ft.Row(
            [
                ft.Image(src=resource_path("assets/logo/hpc-logo.png"), width=30, height=30),
                ft.Text("PC Support Tool", size=20, weight=ft.FontWeight.BOLD),
                ft.VerticalDivider(width=20),
                self.main_tabs,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        # The content area needs to be wrapped in a control that can expand.
        self.content_area = ft.Column([self.build_dashboard_tab()], expand=True)

        self.page.add(
            header_row,
            ft.Divider(),
            self.content_area,
        )
        self.main_tabs.on_change = self.tabs_changed

    def tabs_changed(self, e):
        # Clear the old content from the content_area
        self.content_area.controls.clear()

        selected_index = e.control.selected_index
        new_content = None
        if selected_index == 0:
            new_content = self.build_dashboard_tab()
        elif selected_index == 1:
            new_content = self.build_system_info_tab()
        elif selected_index == 2:
            new_content = self.build_security_tab()
        elif selected_index == 3:
            new_content = self.build_internet_tab()
        elif selected_index == 4:
            new_content = self.build_utilities_tab()
        elif selected_index == 5:
            new_content = self.build_settings_tab()
        
        if new_content:
            self.content_area.controls.append(new_content)
        
        self.page.update()

    def build_dashboard_tab(self):
        return Dashboard(self.page)

    def build_system_info_tab(self):
        return ft.Text("Nội dung tab Thông tin hệ thống")

    def build_security_tab(self):
        return ft.Text("Nội dung tab Bảo mật")

    def build_internet_tab(self):
        return ft.Text("Nội dung tab Internet")

    def build_utilities_tab(self):
        return ft.Text("Nội dung tab Tiện ích")

    def build_tab_with_submenu(self, title, submenus):
        submenu_content_area = ft.Column(expand=True, controls=[submenus[0][2]]) # Load first submenu by default

        def on_navigation_change(e):
            selected_index = e.control.selected_index
            submenu_content_area.controls.clear()
            submenu_content_area.controls.append(submenus[selected_index][2])
            self.page.update()

        navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=icon, label=label) for label, icon, _ in submenus
            ],
            on_change=on_navigation_change,
        )

        return ft.Container(
            content=ft.Row(
                [
                    navigation_rail,
                    ft.VerticalDivider(width=1),
                    ft.Column(
                        [
                            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    submenu_content_area,
                                    ft.VerticalDivider(width=1),
                                    ft.Column([self.results_text_field], expand=3),
                                ],
                                expand=True,
                                vertical_alignment=ft.CrossAxisAlignment.START
                            )
                        ],
                        expand=True
                    )
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            padding=20,
            expand=True,
        )

    def create_action_button(self, text, on_click, icon):
        return ft.ElevatedButton(text=text, on_click=on_click, icon=icon, width=250)

    def build_submenu_view(self, title, buttons):
        return ft.Column(
            [ft.Text(title, size=16, weight=ft.FontWeight.BOLD)] + buttons,
            spacing=10,
            expand=2
        )

    # --- Submenu builders for Utilities ---
    def build_security_submenu(self):
        buttons = [
            self.create_action_button("Quét Virus Nhanh", self.run_defender_quick_scan, ft.Icons.FLASH_ON_ROUNDED),
            self.create_action_button("Quét Virus Toàn Bộ", self.run_defender_full_scan, ft.Icons.SHIELD_ROUNDED),
            self.create_action_button("Cập Nhật Định Nghĩa Virus", self.run_defender_update, ft.Icons.NEW_RELEASES_ROUNDED),
            self.create_action_button("Kiểm Tra Tường Lửa", self.check_firewall_status_gui, ft.Icons.POLICY_ROUNDED),
            self.create_action_button("Bật Tường Lửa", self.enable_firewall_gui, ft.Icons.TOGGLE_ON_ROUNDED),
            self.create_action_button("Tắt Tường Lửa", self.disable_firewall_gui, ft.Icons.TOGGLE_OFF_ROUNDED),
        ]
        return self.build_submenu_view("Bảo mật & Virus", buttons)

    def build_diagnostics_submenu(self):
        buttons = [
            self.create_action_button("Xem Dung Lượng Ổ Đĩa", self.show_disk_usage, ft.Icons.STORAGE_ROUNDED),
            self.create_action_button("Tạo Báo Cáo Pin", self.create_battery_report, ft.Icons.BATTERY_CHARGING_FULL_ROUNDED),
            self.create_action_button("Kiểm tra kích hoạt Windows", self.run_check_windows_activation, ft.Icons.KEY_ROUNDED),
            self.create_action_button("Xem Event Log Gần Đây", self.show_recent_event_logs, ft.Icons.EVENT_NOTE_ROUNDED),
            self.create_action_button("Kiểm Tra Phiên Bản Phần Mềm", self.show_installed_software, ft.Icons.APPS_ROUNDED),
            self.create_action_button("Kiểm Tra Nhiệt Độ", self.show_system_temperatures, ft.Icons.THERMOSTAT_ROUNDED),
            self.create_action_button("Tiến Trình Đang Chạy", self.show_running_processes, ft.Icons.MEMORY_ROUNDED),
        ]
        return self.build_submenu_view("Thông tin & Chẩn đoán", buttons)

    def build_network_submenu(self):
        buttons = [
            self.create_action_button("Kiểm Tra Kết Nối Wifi", self.show_wifi_info, ft.Icons.WIFI_ROUNDED),
            self.create_action_button("Ping (google.com)", self.run_ping_google, ft.Icons.NETWORK_PING_ROUNDED),
            self.create_action_button("Reset Kết Nối Internet", self.run_reset_internet_connection, ft.Icons.NETWORK_CHECK_ROUNDED),
        ]
        return self.build_submenu_view("Mạng", buttons)

    # --- Submenu builders for Fixes ---
    def build_cleanup_submenu(self):
        buttons = [
            self.create_action_button("Xóa File Tạm & Dọn Dẹp", self.run_clear_temp_files, ft.Icons.CLEANING_SERVICES_ROUNDED),
            self.create_action_button("Mở Resource Monitor", self.run_open_resource_monitor, ft.Icons.INSERT_CHART_ROUNDED),
        ]
        return self.build_submenu_view("Dọn dẹp & Tối ưu", buttons)

    def build_repair_submenu(self):
        buttons = [
            self.create_action_button("Chạy SFC Scan", self.run_sfc_scan_command, ft.Icons.HEALTH_AND_SAFETY_ROUNDED),
            self.create_action_button("Tạo Điểm Khôi Phục", self.run_create_restore_point, ft.Icons.RESTORE_PAGE_ROUNDED),
        ]
        return self.build_submenu_view("Sửa lỗi Hệ thống", buttons)

    def build_updates_submenu(self):
        buttons = [
            self.create_action_button("Quản Lý Khởi Động Cùng Win", self.show_startup_programs, ft.Icons.PLAYLIST_ADD_CHECK_ROUNDED),
            self.create_action_button("Cập Nhật Phần Mềm (Winget)", self.run_winget_update_all, ft.Icons.SYSTEM_UPDATE_ALT_ROUNDED),
        ]
        return self.build_submenu_view("Cập nhật", buttons)

    def build_settings_tab(self):
        self.entry_name = ft.TextField(label="Tên người dùng")
        self.entry_department = ft.TextField(label="Phòng Ban")
        self.entry_position = ft.TextField(label="Chức Vụ")
        self.text_notes = ft.TextField(label="Ghi chú", multiline=True, min_lines=3)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Cài đặt & Xuất File", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Nhập thông tin người dùng để đưa vào file xuất."),
                    self.entry_name,
                    self.entry_department,
                    self.entry_position,
                    self.text_notes,
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Xuất Dữ liệu PC",
                                icon=ft.Icons.SAVE_ROUNDED,
                                on_click=self.on_export_info,
                            ),
                            ft.ElevatedButton(
                                "Lưu Kết Quả Hiện Tại",
                                icon=ft.Icons.DESCRIPTION_ROUNDED,
                                on_click=lambda e: self.save_tab_result(self.results_text_field, "KetQua_HienTai"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    )
                ],
                spacing=15,
            ),
            padding=20,
            expand=True,
        )

    # --- Task Execution Logic (copied and adapted from old file) ---
    def _update_display_widget(self, text_control: ft.TextField, content: str, is_error: bool = False):
        text_control.value = content
        text_control.error_text = content if is_error else None
        text_control.update()


    def _run_task_in_thread(self, task_function, needs_wmi=False, *task_args):
        target_text_control = self.results_text_field
        self._update_display_widget(target_text_control, f"Đang thực hiện: {task_function.__name__}...")

        def task_wrapper():
            wmi_service_local, com_initialized_local = None, False
            try:
                if needs_wmi:
                    wmi_service_local, com_initialized_local = _connect_wmi()
                    if not wmi_service_local:
                        raise ConnectionError(ERROR_WMI_CONNECTION)
                    result_data = task_function(wmi_service_local, *task_args)
                else:
                    result_data = task_function(*task_args)
                
                display_text = self._format_task_result_for_display(result_data)
                self._update_display_widget(target_text_control, display_text)
            except Exception as e:
                logging.exception(f"Lỗi khi chạy tác vụ {task_function.__name__}:")
                self._update_display_widget(target_text_control, f"Lỗi: {e}", is_error=True)
            finally:
                if com_initialized_local:
                    try:
                        win32com.client.pythoncom.CoUninitialize()
                    except Exception as com_e:
                        logging.error(f"Lỗi khi giải phóng COM: {com_e}")

        threading.Thread(target=task_wrapper, daemon=True).start()

    def _format_task_result_for_display(self, result_data):
        # This function can be enhanced for better formatting
        if isinstance(result_data, list):
            return "\n---\n".join(map(str, result_data)) or "Hoàn thành, không có dữ liệu."
        if isinstance(result_data, dict):
            return "\n".join(f"{k}: {v}" for k, v in result_data.items()) or "Hoàn thành, không có dữ liệu."
        return str(result_data) or "Hoàn thành, không có dữ liệu."

    def on_export_info(self, e):
        try:
            user_info = {
                "Name": self.entry_name.value.strip(),
                "Department": self.entry_department.value.strip(),
                "Position": self.entry_position.value.strip(),
                "Notes": self.text_notes.value.strip(),
                "Floor": "N/A" # Can be added back if needed
            }
            validate_user_input(user_info)
            full_content = format_pc_info_to_string(self.pc_info_dict)
            filename = generate_filename(user_info, self.pc_info_dict)
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Info_Exports")
            file_path = os.path.join(save_dir, filename)
            save_text_to_file(full_content, file_path)
            self.show_snackbar(f"Đã lưu thành công vào: {file_path}")
        except Exception as ex:
            self.show_snackbar(f"Lỗi khi xuất file: {ex}")

    def save_tab_result(self, text_control, prefix):
        content = text_control.value.strip()
        if not content or "Chào mừng" in content or "Đang thực hiện" in content:
            self.show_snackbar("Không có kết quả để lưu.")
            return
        try:
            filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "PC_Tool_Results")
            file_path = os.path.join(save_dir, filename)
            save_text_to_file(content, file_path)
            self.show_snackbar(f"Đã lưu kết quả vào: {file_path}")
        except Exception as ex:
            self.show_snackbar(f"Lỗi khi lưu file: {ex}")

    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message), open=True)
        self.page.update()

    # --- Event Handlers ---
    def show_disk_usage(self, e): self._run_task_in_thread(get_disk_partitions_usage, True)
    def create_battery_report(self, e): self._run_task_in_thread(generate_battery_report)
    def run_check_windows_activation(self, e): self._run_task_in_thread(check_windows_activation_status)
    def show_recent_event_logs(self, e): self._run_task_in_thread(get_recent_event_logs, True)
    def show_installed_software(self, e): self._run_task_in_thread(get_installed_software_versions, True)
    def show_wifi_info(self, e): self._run_task_in_thread(get_wifi_connection_info)
    def show_system_temperatures(self, e): self._run_task_in_thread(get_system_temperatures, True)
    def show_running_processes(self, e): self._run_task_in_thread(get_running_processes)
    def run_ping_google(self, e): self._run_task_in_thread(run_ping_test, False, "google.com", 4)
    def run_defender_quick_scan(self, e): self._run_task_in_thread(run_windows_defender_scan, False, "QuickScan")
    def run_defender_full_scan(self, e): self._run_task_in_thread(run_windows_defender_scan, False, "FullScan")
    def run_defender_update(self, e): self._run_task_in_thread(update_windows_defender_definitions)
    def check_firewall_status_gui(self, e): self._run_task_in_thread(get_firewall_status)
    def enable_firewall_gui(self, e): self._run_task_in_thread(toggle_firewall, False, True)
    def disable_firewall_gui(self, e): self._run_task_in_thread(toggle_firewall, False, False)
    def run_clear_temp_files(self, e): self._run_task_in_thread(clear_temporary_files)
    def run_open_resource_monitor(self, e): self._run_task_in_thread(open_resource_monitor)
    def run_reset_internet_connection(self, e): self._run_task_in_thread(reset_internet_connection)
    def run_sfc_scan_command(self, e): self._run_task_in_thread(run_sfc_scan)
    def run_winget_update_all(self, e): self._run_task_in_thread(update_all_winget_packages)
    def show_startup_programs(self, e): self._run_task_in_thread(get_startup_programs)
    def run_create_restore_point(self, e): self._run_task_in_thread(create_system_restore_point)

def main(page: ft.Page):
    app = ModernApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="../assets")
