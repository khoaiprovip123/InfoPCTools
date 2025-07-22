# -*- coding: utf-8 -*-

current_language = "vi" # Default language

# Define translations for different languages
all_translations = {
    "en": {
        # Sidebar and Titles
        "app_title": "HPC System Monitor",
        "Dashboard": "Dashboard",
        "Hardware Info": "Hardware Info",
        "Applications": "Applications",
        "Security": "Security",
        "Update & Security": "Update & Security",
        "Update": "Update",
        "System Update": "System Update",
        "Application Updates": "Application Updates",
        "Driver Updates": "Driver Updates",
        "Check for Updates": "Check for Updates",
        "Network": "Network",
        "Backup & Restore": "Backup & Restore",
        "About": "About",
        "Settings": "Settings",

        # Dashboard
        "CPU Usage": "CPU Usage",
        "RAM Usage": "RAM Usage",
        "System Info": "System Info",
        "OS": "OS",
        "Hostname": "Hostname",
        "Uptime": "Uptime",
        "Network Activity": "Network Activity",
        "Local IP": "Local IP",
        "Download": "Download",
        "Upload": "Upload",
        "Disk Usage": "Disk Usage",

        # Hardware Info
        "wmi_not_found": "'wmi' library not found. Please install with 'pip install wmi'",
        "error_occurred": "An error occurred: {e}",
        "System": "System",
        "System Type": "System Type",
        "Manufacturer": "Manufacturer",
        "Operating System": "Operating System",
        "Version": "Version",
        "Build": "Build",
        "CPU": "CPU",
        "Name": "Name",
        "Cores": "Cores",
        "Threads": "Threads",
        "Clock Speed": "Clock Speed",
        "RAM": "RAM",
        "Total": "Total",
        "Type": "Type",
        "GPU": "GPU",
        "VRAM": "VRAM",
        "Storage": "Storage",
        "Network Adapters": "Network Adapters",
        "Desktop": "Desktop",
        "Laptop": "Laptop",

        # User Info
        "User Information": "User Information",
        "Full Name:": "Full Name:",
        "Department:": "Department:",
        "Notes:": "Notes:",
        "Enter full name": "Enter full name",
        "Enter department": "Enter department",
        "Add notes": "Add notes",
        "Save": "Save",
        "Print": "Print",
        "No user info entered.": "No user info entered.",
        "Error": "Error",
        "fullname_department_required": "Full Name and Department are required to export.",
        "no_qr_code_to_export": "No QR code available to export.",

        # Applications
        "Export to TXT": "Export to TXT",
        "Generate QR Code": "Generate QR Code",
        "Export & Generate QR": "Export & Generate QR",
        "Export QR": "Export QR",
        "Export TXT": "Export TXT",

        # Applications
        "Installed Apps": "Installed Apps",
        "Startup Apps": "Startup Apps",
        "Processes": "Processes",
        "Uninstall": "Uninstall",
        "Process Name": "Process Name",
        "PID": "PID",
        "CPU": "CPU",
        "Memory": "Memory",
        "No running processes found.": "No running processes found.",
        "Search installed apps...": "Search installed apps...",
        "Search startup apps...": "Search startup apps...",
        "Search processes...": "Search processes...",

        # Security
        "Firewall Status": "Firewall Status",
        "Antivirus": "Antivirus",
        "Windows Update": "Windows Update",
        "On": "On",
        "Off": "Off",
        "Unknown": "Unknown",
        "Not found": "Not found",
        "Click to check": "Click to check",
        "Check": "Check",
        "Settings": "Settings",

        # Network
        "Network Configuration": "Network Configuration",
        "Interface": "Interface",
        "IP Address": "IP Address",
        "Netmask": "Netmask",
        "Active Network Connections": "Active Network Connections",
        "access_denied_connections": "Access denied to retrieve network connection information.",

        # Backup & Restore
        "System Repair": "System Repair",
        "Backup": "Backup",
        "Restore": "Restore",
        "Printer Management": "Printer Management",
        "Scan and Fix System Files (SFC)": "Scan and Fix System Files (SFC)",
        "Check and Repair Disk (CHKDSK)": "Check and Repair Disk (CHKDSK)",
        "Troubleshoot Print Spooler": "Troubleshoot Print Spooler",
        "Open Device Manager": "Open Device Manager",
        "Create System Restore Point": "Create System Restore Point",
        "Backup Drivers": "Backup Drivers",
        "driver_backup_info": "Driver backups will be saved to C:\\driver-backups",
        "Create System Image": "Create System Image",
        "Backup Files and Folders": "Backup Files and Folders",
        "Restore Files and Folders": "Restore Files and Folders",
        "Create Recovery Drive": "Create Recovery Drive",
        "Add a Printer": "Add a Printer",
        "Remove a Printer": "Remove a Printer",
        "Troubleshoot Printer": "Troubleshoot Printer",
        "Open Print Management": "Open Print Management",

        # Explanations
        "sfc_scannow_desc": "Scans and repairs corrupted Windows system files.",
        "chkdsk_desc": "Checks the hard drive for errors and attempts to repair them.",
        "print_spooler_desc": "Resets the print spooler service to fix printing issues.",
        "device_manager_desc": "Opens Device Manager to view and manage hardware devices.",
        "create_restore_point_desc": "Creates a system restore point, allowing you to revert system changes.",
        "backup_drivers_desc": "Backs up all installed device drivers to a specified location.",
        "create_system_image_desc": "Creates a full system image for disaster recovery.",
        "backup_files_folders_desc": "Opens Windows settings to configure file and folder backup options.",
        "restore_files_folders_desc": "Opens Windows File History to restore previous versions of files.",
        "create_recovery_drive_desc": "Creates a recovery drive to troubleshoot and restore your PC.",
        "add_printer_desc": "Starts the wizard to add a new printer to your system.",
        "remove_printer_desc": "Opens the print management console to remove an installed printer.",
        "troubleshoot_printer_desc": "Runs the Windows printer troubleshooter to diagnose and fix printer problems.",
        "open_print_management_desc": "Opens the Print Management console for advanced printer configuration.",
        "check_windows_update_desc": "Checks for and installs the latest Windows updates.",
        "update_applications_desc": "Checks for updates for installed applications.",
        "update_drivers_desc": "Checks for and installs updated device drivers.",
        "export_hardware_info_desc": "Exports your system's hardware information to a text file.",
        "open_firewall_settings_desc": "Opens Windows Firewall settings to manage network security.",
        "open_windows_defender_settings_desc": "Opens Windows Security settings for antivirus and threat protection.",
        "open_uac_settings_desc": "Adjusts User Account Control settings to manage security prompts.",
        "enable_firewall_desc": "Enables the Windows Firewall for all network profiles.",
        "disable_firewall_desc": "Disables the Windows Firewall for all network profiles.",
        "toggle_realtime_protection_desc": "Toggles Windows Defender real-time protection on or off.",
        "update_virus_definitions_desc": "Downloads and installs the latest Windows Defender virus definitions.",
        "run_quick_scan_desc": "Performs a quick scan of your system for malware.",
        "run_full_scan_desc": "Performs a comprehensive scan of your entire system for malware.",
        "run_custom_scan_desc": "Allows you to select specific files or folders to scan for malware.",
        "open_windows_security_desc": "Opens the main Windows Security dashboard.",
        "open_account_settings_desc": "Opens Windows account settings to manage sign-in options and user accounts.",
        "open_app_browser_control_desc": "Manages reputation-based protection settings for apps and browsers.",

        # About
        "about_text": '''HPC System Monitor\nVersion 1.1\n\nDeveloped by Gemini AI from Google.\n\nThis application provides a comprehensive overview of your system\'s performance and hardware,\nalong with tools for system maintenance and repair.\n\nFor more information, visit the project\'s GitHub page.''',
        "github_repo": "GitHub Repository (Placeholder)",
        
        # Settings
        "Application Information": "Application Information",
        "Version": "Version",
        "Developed by Gemini AI from Google.": "Developed by Gemini AI from Google.",
        "Theme Settings": "Theme Settings",
        "Dark Mode": "Dark Mode",
        "Language Settings": "Language Settings",
        "English": "English",
        "Vietnamese": "Vietnamese"
    },
    "vi": {
        # Sidebar and Titles
        "app_title": "HPC Giám sát Hệ thống",
        "Dashboard": "Bảng điều khiển",
        "Hardware Info": "Thông tin Phần cứng",
        "Applications": "Ứng dụng",
        "Security": "Bảo mật",
        "Update & Security": "Cập nhật & Bảo mật",
        "Update": "Cập nhật",
        "System Update": "Cập nhật Hệ thống",
        "Application Updates": "Cập nhật Ứng dụng",
        "Driver Updates": "Cập nhật Driver",
        "Check for Updates": "Kiểm tra Cập nhật",
        "Network": "Mạng",
        "Backup & Restore": "Sao lưu & Khôi phục",
        "About": "Giới thiệu",
        "Settings": "Cấu hình",

        # Dashboard
        "CPU Usage": "Sử dụng CPU",
        "RAM Usage": "Sử dụng RAM",
        "System Info": "Thông tin Hệ thống",
        "OS": "Hệ điều hành",
        "Hostname": "Tên máy",
        "Uptime": "Thời gian hoạt động",
        "Network Activity": "Hoạt động Mạng",
        "Local IP": "IP Cục bộ",
        "Download": "Tải xuống",
        "Upload": "Tải lên",
        "Disk Usage": "Sử dụng Đĩa",

        # Hardware Info
        "wmi_not_found": "'Thư viện 'wmi' không được tìm thấy. Vui lòng cài đặt bằng lệnh 'pip install wmi'",
        "error_occurred": "Đã xảy ra lỗi: {e}",
        "System": "Hệ thống",
        "System Type": "Loại hệ thống",
        "Manufacturer": "Nhà sản xuất",
        "Operating System": "Hệ điều hành",
        "Version": "Phiên bản",
        "Build": "Bản dựng",
        "CPU": "CPU",
        "Name": "Tên",
        "Cores": "Số lõi",
        "Threads": "Số luồng",
        "Clock Speed": "Tốc độ xung nhịp",
        "RAM": "RAM",
        "Total": "Tổng cộng",
        "Type": "Loại",
        "GPU": "GPU",
        "VRAM": "VRAM",
        "Storage": "Lưu trữ",
        "Network Adapters": "Card mạng",
        "Desktop": "Máy tính để bàn",
        "Laptop": "Máy tính xách tay",

        # User Info
        "User Information": "Thông tin Người dùng",
        "Full Name:": "Họ tên:",
        "Department:": "Phòng ban:",
        "Notes:": "Ghi chú:",
        "Enter full name": "Nhập họ tên đầy đủ",
        "Enter department": "Nhập phòng ban",
        "Add notes": "Thêm ghi chú",
        "Save": "Lưu",
        "Print": "In",
        "No user info entered.": "Chưa nhập thông tin người dùng.",
        "Error": "Lỗi",
        "fullname_department_required": "Cần nhập Họ tên và Phòng ban để xuất.",
        "no_qr_code_to_export": "Không có mã QR để xuất.",

        # Applications
        "Generate QR Code": "Tạo mã QR",
        "Export & Generate QR": "Xuất & Tạo mã QR",
        "Export QR": "Xuất QR",
        "Export TXT": "Xuất TXT",

        # Applications
        "Name": "Tên",
        "Publisher": "Tên nhà cung cấp",
        "Install Date": "Ngày cài đặt",
        "Action": "Hành động",
        "Path": "Đường dẫn",
        "Status": "Trạng thái",
        "Failed to change startup app status": "Không thể thay đổi trạng thái ứng dụng khởi động",

        "Installed Apps": "Ứng dụng đã cài đặt",
        "Startup Apps": "Ứng dụng khởi động",
        "Processes": "Tiến trình",
        "Uninstall": "Gỡ cài đặt",
        "Process Name": "Tên tiến trình",
        "PID": "PID",
        "CPU": "CPU",
        "Memory": "Bộ nhớ",
        "No running processes found.": "Không tìm thấy tiến trình nào đang chạy.",
        "Search installed apps...": "Tìm kiếm ứng dụng đã cài đặt...",
        "Search startup apps...": "Tìm kiếm ứng dụng khởi động...",
        "Search processes...": "Tìm kiếm tiến trình...",

        # Security
        "Firewall Status": "Trạng thái Tường lửa",
        "Antivirus": "Phần mềm diệt virus",
        "Windows Update": "Cập nhật Windows",
        "On": "Bật",
        "Off": "Tắt",
        "Unknown": "Không xác định",
        "Not found": "Không tìm thấy",
        "Click to check": "Nhấn để kiểm tra",
        "Check": "Kiểm tra",
        "Settings": "Cài đặt",
        "System Security": "Bảo mật Hệ thống",
        "Windows Defender": "Windows Defender",
        "User Account Control (UAC)": "Kiểm soát Tài khoản Người dùng (UAC)",
        "Drive Encryption": "Mã hóa Ổ đĩa",
        "BitLocker Status": "Trạng thái BitLocker",
        "Security Scans": "Quét Bảo mật",
        "Quick Scan": "Quét Nhanh",
        "Full Scan": "Quét Toàn bộ",
        "Click to run": "Nhấn để chạy",
        "Open Settings": "Mở Cài đặt",
        "Run Scan": "Chạy Quét",
        "Enable": "Bật",
        "Disable": "Tắt",
        "Firewall & Network Protection": "Bảo vệ Tường lửa & Mạng",
        "Real-time Protection": "Bảo vệ Thời gian thực",
        "Virus Definitions": "Cập nhật Định nghĩa Virus",
        "Last updated: N/A": "Cập nhật lần cuối: N/A",
        "Function Name": "Tên Chức năng",
        "Description": "Mô tả",
        "Action": "Hành động",
        "Status": "Trạng thái",

        # Network
        "Network Configuration": "Cấu hình Mạng",
        "Interface": "Giao diện",
        "IP Address": "Địa chỉ IP",
        "Netmask": "Subnet Mask",
        "Active Network Connections": "Kết nối Mạng đang hoạt động",
        "access_denied_connections": "Từ chối truy cập để lấy thông tin kết nối mạng.",

        "Flush DNS": "Xóa bộ nhớ cache DNS",
        "Release IP": "Giải phóng địa chỉ IP",
        "Renew IP": "Gia hạn địa chỉ IP",
        "Open Network and Sharing Center": "Mở Trung tâm Mạng và Chia sẻ",
        "Ping Host": "Ping máy chủ",

        "flush_dns_desc": "Xóa bộ nhớ cache của trình phân giải DNS để giải quyết các sự cố phân giải tên.",
        "release_ip_desc": "Giải phóng địa chỉ IP hiện tại của tất cả các bộ điều hợp mạng.",
        "renew_ip_desc": "Gia hạn địa chỉ IP của tất cả các bộ điều hợp mạng.",
        "open_network_sharing_center_desc": "Mở Trung tâm Mạng và Chia sẻ của Windows để quản lý cài đặt mạng.",
        "ping_host_desc": "Kiểm tra kết nối mạng đến một máy chủ hoặc địa chỉ IP cụ thể.",

        "Set DNS": "Cấu hình DNS",
        "Set Static IP": "Cấu hình IP tĩnh",
        "Gateway": "Cổng mặc định",
        "MAC Address": "Địa chỉ MAC",
        "DHCP Enabled": "DHCP được bật",
        "PID": "PID",
        "Process Name": "Tên tiến trình",
        "Remote Address": "Địa chỉ từ xa",

        "set_dns_desc": "Cho phép người dùng đặt máy chủ DNS tùy chỉnh cho một bộ điều hợp mạng.",
        "set_static_ip_desc": "Cho phép người dùng đặt địa chỉ IP tĩnh, mặt nạ mạng con và cổng mặc định cho một bộ điều hợp mạng.",

        # Backup & Restore
        "System Repair": "Sửa chữa Hệ thống",
        "Backup": "Sao lưu",
        "Restore": "Khôi phục",
        "Printer Management": "Quản lý Máy in",
        "Scan and Fix System Files (SFC)": "Quét và Sửa chữa Tệp Hệ thống (SFC)",
        "Check and Repair Disk (CHKDSK)": "Kiểm tra và Sửa chữa Ổ đĩa (CHKDSK)",
        "Troubleshoot Print Spooler": "Khắc phục sự cố Dịch vụ In",
        "Open Device Manager": "Mở Trình quản lý Thiết bị",
        "Create System Restore Point": "Tạo Điểm Khôi phục Hệ thống",
        "Backup Drivers": "Sao lưu Trình điều khiển",
        "driver_backup_info": "Các bản sao lưu trình điều khiển sẽ được lưu vào C:\\driver-backups",
        "Create System Image": "Tạo Ảnh Hệ thống",
        "Backup Files and Folders": "Sao lưu Tệp và Thư mục",
        "Restore Files and Folders": "Khôi phục Tệp và Thư mục",
        "Create Recovery Drive": "Tạo Ổ đĩa Khôi phục",
        "Add a Printer": "Thêm Máy in",
        "Remove a Printer": "Xóa Máy in",
        "Troubleshoot Printer": "Khắc phục sự cố Máy in",
        "Open Print Management": "Mở Quản lý In",

        # Explanations
        "sfc_scannow_desc": "Quét và sửa chữa các tệp hệ thống Windows bị hỏng.",
        "chkdsk_desc": "Kiểm tra ổ cứng để tìm lỗi và cố gắng sửa chữa chúng.",
        "print_spooler_desc": "Đặt lại dịch vụ in để khắc phục các sự cố liên quan đến in ấn.",
        "device_manager_desc": "Mở Trình quản lý Thiết bị để xem và quản lý các thiết bị phần cứng.",
        "create_restore_point_desc": "Tạo một điểm khôi phục hệ thống, cho phép bạn hoàn nguyên các thay đổi của hệ thống.",
        "backup_drivers_desc": "Sao lưu tất cả các trình điều khiển thiết bị đã cài đặt vào một vị trí được chỉ định.",
        "create_system_image_desc": "Tạo một ảnh hệ thống đầy đủ để phục hồi sau thảm họa.",
        "backup_files_folders_desc": "Mở cài đặt Windows để cấu hình các tùy chọn sao lưu tệp và thư mục.",
        "restore_files_folders_desc": "Mở Lịch sử Tệp của Windows để khôi phục các phiên bản tệp trước đó.",
        "create_recovery_drive_desc": "Tạo một ổ đĩa khôi phục để khắc phục sự cố và khôi phục PC của bạn.",
        "add_printer_desc": "Bắt đầu trình hướng dẫn để thêm một máy in mới vào hệ thống của bạn.",
        "remove_printer_desc": "Mở bảng điều khiển quản lý in để xóa một máy in đã cài đặt.",
        "troubleshoot_printer_desc": "Chạy trình khắc phục sự cố máy in của Windows để chẩn đoán và khắc phục sự cố máy in.",
        "open_print_management_desc": "Mở bảng điều khiển Quản lý In để cấu hình máy in nâng cao.",
        "check_windows_update_desc": "Kiểm tra và cài đặt các bản cập nhật Windows mới nhất.",
        "update_applications_desc": "Kiểm tra các bản cập nhật cho các ứng dụng đã cài đặt.",
        "update_drivers_desc": "Kiểm tra và cài đặt các trình điều khiển thiết bị đã cập nhật.",
        "export_hardware_info_desc": "Xuất thông tin phần cứng của hệ thống ra một tệp văn bản.",
        "open_firewall_settings_desc": "Mở cài đặt Tường lửa Windows để quản lý bảo mật mạng.",
        "open_windows_defender_settings_desc": "Mở cài đặt Bảo mật Windows để bảo vệ chống vi-rút và mối đe dọa.",
        "open_uac_settings_desc": "Điều chỉnh cài đặt Kiểm soát Tài khoản Người dùng để quản lý các lời nhắc bảo mật.",
        "enable_firewall_desc": "Bật Tường lửa Windows cho tất cả các cấu hình mạng.",
        "disable_firewall_desc": "Tắt Tường lửa Windows cho tất cả các cấu hình mạng.",
        "toggle_realtime_protection_desc": "Bật hoặc tắt tính năng bảo vệ thời gian thực của Windows Defender.",
        "update_virus_definitions_desc": "Tải xuống và cài đặt các định nghĩa vi-rút Windows Defender mới nhất.",
        "run_quick_scan_desc": "Thực hiện quét nhanh hệ thống của bạn để tìm phần mềm độc hại.",
        "run_full_scan_desc": "Thực hiện quét toàn diện toàn bộ hệ thống của bạn để tìm phần mềm độc hại.",
        "run_custom_scan_desc": "Cho phép bạn chọn các tệp hoặc thư mục cụ thể để quét tìm phần mềm độc hại.",
        "open_windows_security_desc": "Mở bảng điều khiển Bảo mật Windows chính.",
        "open_account_settings_desc": "Mở cài đặt tài khoản Windows để quản lý các tùy chọn đăng nhập và tài khoản người dùng.",
        "open_app_browser_control_desc": "Quản lý cài đặt bảo vệ dựa trên danh tiếng cho ứng dụng và trình duyệt.",

        # About
        "about_text": '''HPC Giám sát Hệ thống\nPhiên bản 1.1\n\nPhát triển bởi Gemini AI từ Google.\n\nỨng dụng này cung cấp cái nhìn tổng quan về hiệu suất và phần cứng của hệ thống,\ncùng với các công cụ để bảo trì và sửa chữa hệ thống.\n\nĐể biết thêm thông tin, hãy truy cập trang GitHub của dự án.''',
        "github_repo": "Kho lưu trữ GitHub (Placeholder)",

        # Settings
        "Application Information": "Thông tin Ứng dụng",
        "app_info_desc": "Hiển thị thông tin về ứng dụng này, bao gồm phiên bản và nhà phát triển.",
        "Version": "Phiên bản",
        "Developed by Gemini AI from Google.": "Được phát triển bởi Gemini AI từ Google.",
        "Theme Settings": "Cài đặt Giao diện",
        "theme_settings_desc": "Thay đổi giao diện của ứng dụng giữa chế độ sáng và tối.",
        "Dark Mode": "Chế độ Tối",
        "Language Settings": "Cài đặt Ngôn ngữ",
        "language_settings_desc": "Thay đổi ngôn ngữ hiển thị của ứng dụng.",
        "English": "Tiếng Anh",
        "Vietnamese": "Tiếng Việt",
        "About": "Giới thiệu",
        "about_desc": "Thông tin về ứng dụng, phiên bản và nguồn gốc."
    }
}

# Mapping from display name to language code
language_map = {
    "English": "en",
    "Tiếng Việt": "vi"
}

def get_text(key):
    return all_translations[current_language].get(key, key)

def set_language(lang_code):
    global current_language
    if lang_code in all_translations:
        current_language = lang_code
        return True
    return False

def get_available_languages():
    return list(language_map.keys())

def get_current_language_name():
    for name, code in language_map.items():
        if code == current_language:
            return name
    return "Unknown" # Should not happen

def set_language_by_name(lang_name):
    lang_code = language_map.get(lang_name)
    if lang_code:
        return set_language(lang_code)
    return False