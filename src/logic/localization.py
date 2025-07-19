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
        "Network": "Network",
        "Repair & Restore": "Repair & Restore",
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
        "Full Name": "Full Name",
        "Department": "Department",
        "Notes": "Notes",
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
        "Uninstall": "Uninstall",

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

        # Repair & Restore
        "Scan and Fix System Files": "Scan and Fix System Files (sfc /scannow)",
        "Troubleshoot Print Spooler": "Troubleshoot Print Spooler",
        "Open Device Manager": "Open Device Manager",
        "Create System Restore Point": "Create System Restore Point",
        "Backup Drivers": "Backup Drivers",
        "driver_backup_info": "Driver backups will be saved to C:\\driver-backups",

        # About
        "about_text": "HPC System Monitor\nVersion 1.0\n\nDeveloped by Gemini AI from Google.\n\nThis application provides a comprehensive overview of your system's performance and hardware,\nalong with tools for system maintenance and repair.\n\nFor more information, visit the project's GitHub page.",
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
        "Network": "Mạng",
        "Repair & Restore": "Sửa chữa & Phục hồi",
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
        "Full Name": "Họ tên",
        "Department": "Phòng ban",
        "Notes": "Ghi chú",
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
        "Publisher": "Nhà phát hành",
        "Install Date": "Ngày cài đặt",
        "Action": "Hành động",
        "Path": "Đường dẫn",
        "Status": "Trạng thái",
        "Failed to change startup app status": "Không thể thay đổi trạng thái ứng dụng khởi động",

        "Installed Apps": "Ứng dụng đã cài đặt",
        "Startup Apps": "Ứng dụng khởi động",
        "Uninstall": "Gỡ cài đặt",

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

        # Network
        "Network Configuration": "Cấu hình Mạng",
        "Interface": "Giao diện",
        "IP Address": "Địa chỉ IP",
        "Netmask": "Subnet Mask",
        "Active Network Connections": "Kết nối Mạng đang hoạt động",
        "access_denied_connections": "Từ chối truy cập để lấy thông tin kết nối mạng.",

        # Repair & Restore
        "Scan and Fix System Files": "Quét và sửa chữa tệp hệ thống (sfc /scannow)",
        "Troubleshoot Print Spooler": "Xử lý sự cố Dịch vụ In (Print Spooler)",
        "Open Device Manager": "Mở Trình quản lý Thiết bị (Device Manager)",
        "Create System Restore Point": "Tạo điểm Khôi phục Hệ thống",
        "Backup Drivers": "Sao lưu Trình điều khiển (Driver)",
        "driver_backup_info": "Các bản sao lưu trình điều khiển sẽ được lưu vào C:\\driver-backups",

        # About
        "about_text": "HPC Giám sát Hệ thống\nPhiên bản 1.0\n\nPhát triển bởi Gemini AI từ Google.\n\nỨng dụng này cung cấp cái nhìn tổng quan về hiệu suất và phần cứng của hệ thống,\ncùng với các công cụ để bảo trì và sửa chữa hệ thống.\n\nĐể biết thêm thông tin, hãy truy cập trang GitHub của dự án.",
        "github_repo": "Kho lưu trữ GitHub (Placeholder)",

        # Settings
        "Application Information": "Thông tin Ứng dụng",
        "Version": "Phiên bản",
        "Developed by Gemini AI from Google.": "Được phát triển bởi Gemini AI từ Google.",
        "Theme Settings": "Cài đặt Giao diện",
        "Dark Mode": "Chế độ Tối",
        "Language Settings": "Cài đặt Ngôn ngữ",
        "English": "Tiếng Anh",
        "Vietnamese": "Tiếng Việt"
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