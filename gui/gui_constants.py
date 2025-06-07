# gui/gui_constants.py

# --- Font Settings ---
DEFAULT_FONT_FAMILY = "Segoe UI" # Hoặc "Arial", "Tahoma", "Calibri"
MONOSPACE_FONT_FAMILY = "Courier New" # Hoặc "Consolas"
H1_FONT_SIZE = 16 # Font size cho tiêu đề cấp 1
H2_FONT_SIZE = 12
BODY_FONT_SIZE = 10
MONOSPACE_FONT_SIZE = 9

APP_VERSION = "2.1.0" # Cập nhật phiên bản
APP_AUTHOR = "VIETNAM"
APP_CONTACT_EMAIL = "vankhoai690@gmail.com"

# --- Color Palette (Lấy cảm hứng từ Tailwind CSS và các theme hiện đại) ---
# Primary Colors
PRIMARY_COLOR = "#3B82F6" # Blue-500
SECONDARY_COLOR = "#10B981" # Green-500
ACCENT_COLOR = "#F59E0B" # Amber-500
PURPLE_COLOR = "#8B5CF6" # Violet-500

# Text Colors
TEXT_COLOR_PRIMARY = "#1F2937" # Gray-800 (Darker for primary text)
TEXT_COLOR_SECONDARY = "#6B7280" # Gray-500 (Lighter for secondary text)
TEXT_COLOR_ACCENT = ACCENT_COLOR # Text color that matches accent
HEADER_TEXT_COLOR = TEXT_COLOR_PRIMARY # Màu cho tiêu đề trang, thường giống màu chữ chính

# Background Colors
WINDOW_BG = "#F9FAFB" # Gray-50 (Lightest gray for window background)
MAIN_CONTENT_BG = "#FFFFFF" # White for main content area
SIDEBAR_BG_START = "#1F2937" # Gray-800
SIDEBAR_BG_END = "#111827"   # Gray-900 (Darker for gradient)
SIDEBAR_LOGO_SUBTITLE_COLOR = "#9CA3AF" # Gray-400, for subtitle text in dark sidebar
HEADER_BG = "#FFFFFF" # White for page header (can add shadow later)
GROUPBOX_BG = "#FFFFFF" # White for groupbox background
FRAME_BG = "#FFFFFF" # White for frames, tab panes
INPUT_BG = "#F3F4F6" # Gray-100 (Slightly darker than window for inputs)

# Button Colors
BUTTON_DANGER_BG = "#EF4444" # Red-500 for danger/exit buttons
BUTTON_DANGER_HOVER = "#DC2626" # Red-600
BUTTON_PRIMARY_BG = PRIMARY_COLOR
BUTTON_PRIMARY_HOVER = "#2563EB" # Blue-600
BUTTON_PRIMARY_PRESSED = "#1D4ED8" # Blue-700
BUTTON_SECONDARY_BG = "#E5E7EB" # Gray-200
BUTTON_SECONDARY_HOVER = "#D1D5DB" # Gray-300
BUTTON_SECONDARY_PRESSED = "#9CA3AF" # Gray-400
BUTTON_SECONDARY_TEXT = TEXT_COLOR_PRIMARY # Text color for secondary buttons
BUTTON_EXPORT_BG = SECONDARY_COLOR # Green-500 for export
BUTTON_EXPORT_HOVER = "#059669" # Green-600
BUTTON_EXPORT_PRESSED = "#047857" # Green-700
ACCENT_COLOR_HOVER = "#D97706" # Amber-600
ACCENT_COLOR_PRESSED = "#B45309" # Amber-700

# Border Colors
BORDER_COLOR_LIGHT = "#E5E7EB" # Gray-200 (Light border for elements)
BORDER_COLOR_DARK = "#D1D5DB"  # Gray-300 (Slightly darker border, e.g., for splitter handle hover)
INPUT_BORDER_COLOR = "#D1D5DB" # Gray-300 (Border for input fields)

# Tab Colors
TAB_BG_ACTIVE = FRAME_BG # Nền tab đang active giống nền frame
TAB_BG_INACTIVE = WINDOW_BG # Nền tab không active giống nền window
TAB_TEXT_ACTIVE = TEXT_COLOR_PRIMARY # Màu chữ tab active
TAB_TEXT_INACTIVE = TEXT_COLOR_SECONDARY # Màu chữ tab inactive

# Sidebar Colors
SIDEBAR_TEXT_COLOR = "#E5E7EB" # Gray-200 (Light text for dark sidebar)
SIDEBAR_TEXT_ACTIVE_COLOR = "#FFFFFF" # White for active/hovered text
SIDEBAR_TEXT_ACTIVE_BG = PRIMARY_COLOR # Blue-500 for active item background
SIDEBAR_TEXT_HOVER_BG = "#374151" # Gray-700 (Slightly lighter than sidebar for hover)

# Other UI Element Colors
HIGHLIGHT_COLOR = ACCENT_COLOR # Màu để highlight text khi tìm kiếm (ví dụ: vàng cam)
TOAST_TEXT_COLOR = "#FFFFFF" # White text for toasts
TOAST_INFO_BG = "#3B82F6"    # Blue-500 for info toasts
TOAST_SUCCESS_BG = "#10B981" # Green-500 for success toasts
TOAST_ERROR_BG = "#EF4444"   # Red-500 for error toasts
STAT_CARD_BG = "#FFFFFF" # White background for stat cards
STAT_CARD_TITLE_COLOR = TEXT_COLOR_SECONDARY # Gray-500 for card titles
STAT_CARD_VALUE_COLOR = TEXT_COLOR_PRIMARY   # Gray-800 for main values
STAT_CARD_DETAILS_COLOR = TEXT_COLOR_SECONDARY # Gray-500 for smaller details
GRADIENT_BG_START = "#667eea" # Example gradient start for quick action buttons
GRADIENT_BG_END = "#764ba2"   # Example gradient end

# --- Application Information ---
APP_DESCRIPTION = """
**PC Pro - System Optimizer** là một công cụ toàn diện giúp bạn quản lý, tối ưu và bảo trì máy tính Windows một cách hiệu quả.

**Các chức năng chính:**

*   **Dashboard (Bảng điều khiển):**
    *   Hiển thị tổng quan về hiệu suất hệ thống theo thời gian thực: CPU, RAM, SSD/HDD, GPU.
    *   Đánh giá "Điểm Sức Khỏe Hệ Thống" dựa trên nhiều yếu tố.
    *   Các nút hành động nhanh: Dọn dẹp hệ thống, Tăng tốc PC (đang phát triển), Quét bảo mật, Cập nhật Driver (đang phát triển).

*   **Hệ Thống (Thông tin chi tiết):**
    *   Cung cấp thông tin chi tiết về phần cứng: Tên máy, Loại máy, IP, MAC, Hệ điều hành, Phiên bản Windows, Trạng thái kích hoạt.
    *   Thông tin CPU: Model, Lõi, Luồng, Tốc độ.
    *   Thông tin RAM: Tổng dung lượng, Chi tiết các thanh RAM.
    *   Thông tin Mainboard: Nhà sản xuất, Model, Số Sê-ri.
    *   Thông tin Ổ đĩa: Model, Dung lượng, Giao tiếp, Loại, Sê-ri.
    *   Thông tin Card đồ họa (GPU): Tên, Nhà sản xuất, VRAM, Độ phân giải, Phiên bản Driver, Ngày Driver.
    *   Thông tin Màn hình: Tên, Độ phân giải, Tỷ lệ, Kích thước, Trạng thái.
    *   Nhiệt độ hệ thống: CPU, GPU, Ổ cứng (nếu có).

*   **Bảo Mật:**
    *   Quét Virus Nhanh và Toàn Bộ với Windows Defender.
    *   Cập nhật định nghĩa Virus cho Windows Defender.
    *   Kiểm tra và Bật/Tắt Tường lửa Windows (cho tất cả profile).

*   **Tối Ưu:**
    *   **Tối Ưu Hóa Toàn Diện (1-Click):** Chạy các tác vụ dọn dẹp, tối ưu cơ bản.
    *   **Chế Độ Gaming:** Tối ưu hệ thống cho trải nghiệm chơi game tốt hơn (đang phát triển).
    *   Dọn dẹp File Tạm & Cache.
    *   Mở Resource Monitor.
    *   Quản lý Ứng Dụng Khởi Động cùng Windows.
    *   Chạy SFC Scan để kiểm tra và sửa lỗi file hệ thống.
    *   Tạo Điểm Khôi Phục Hệ Thống.
    *   Cập nhật Phần Mềm đã cài đặt thông qua Winget.
    *   Tối ưu Dịch Vụ Windows (nâng cao, cần cẩn trọng).
    *   Dọn Dẹp Registry (có sao lưu, nâng cao, cần cẩn trọng).
    *   Quản lý Máy In: Liệt kê, Gỡ máy in lỗi, Xóa hàng đợi in, Khởi động lại dịch vụ Spooler.

*   **Mạng:**
    *   Kiểm tra thông tin Kết Nối Wifi hiện tại.
    *   Xem Cấu Hình Mạng Chi Tiết (IP, DNS, Gateway, DHCP...).
    *   Ping đến một địa chỉ (mặc định google.com).
    *   Phân giải địa chỉ IP từ Tên Miền.
    *   Xem các Kết Nối Mạng Đang Hoạt Động (tương tự netstat).
    *   Cấu hình DNS Chính và Phụ cho card mạng.
    *   Xóa Cache DNS của hệ thống.
    *   Reset Kết Nối Internet (giải phóng IP, làm mới DNS, reset Winsock).

*   **Trung Tâm Cập Nhật:**
    *   Kiểm tra trạng thái và mở cài đặt Windows Update.
    *   Liệt kê các ứng dụng có thể cập nhật qua Winget.
    *   Cập nhật tất cả ứng dụng qua Winget.
    *   Cập nhật định nghĩa Virus (tương tự như ở tab Bảo Mật).

*   **Báo Cáo & Cài đặt:**
    *   Nhập thông tin người dùng (Tên, Phòng ban, Tầng, Chức vụ) và Ghi chú.
    *   Xuất toàn bộ thông tin PC và người dùng ra file văn bản (.txt).
    *   Hiển thị thông tin phiên bản ứng dụng, tác giả và liên hệ hỗ trợ.

**Lưu ý:** Một số chức năng yêu cầu quyền Administrator để hoạt động. Ứng dụng sẽ cố gắng thông báo khi cần thiết.
"""