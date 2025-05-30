## 2. core/pc_info_manager.py
# Quản lý xử lý dữ liệu, định dạng và tiện ích lưu file
import os
import logging
# Import các hằng số và hàm cần thiết từ module khác
from core.pc_info_functions import (
    NOT_AVAILABLE, NOT_IDENTIFIED, ERROR_FETCHING_INFO, ERROR_WMI_CONNECTION, NOT_FOUND,
    STATUS_OK # Thêm STATUS_OK để so sánh
)

# --- Cấu hình Logging ---
# (Giả sử logging đã được cấu hình ở file chính hoặc ở đây nếu cần)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Hằng số ---
DEFAULT_FILENAME_BASE = "pc_info_fallback"

# --- Hàm Validation (Giữ nguyên) ---
def validate_user_input(user_info):
    """
    Kiểm tra xem các trường thông tin người dùng bắt buộc có được cung cấp không.
    Trường "Chức vụ" không còn bắt buộc.
    """
    errors = []
    required_fields = {
        "Name": "Tên người dùng",
        "Department": "Bộ phận",
        "Floor": "Tầng",
    }
    for key, display_name in required_fields.items():
        value = str(user_info.get(key, "")).strip()
        # Kiểm tra đặc biệt cho Tầng khi chọn "Khác"
        # Logic này giả định rằng giá trị cuối cùng của 'Floor' trong user_info
        # đã được cập nhật thành giá trị nhập tay nếu người dùng chọn 'Khác'.
        # Nếu giá trị vẫn là "Khác", nghĩa là người dùng chưa nhập gì.
        if key == "Floor" and value == "Khác":
             errors.append(f"{display_name} (Vui lòng nhập tầng cụ thể khi chọn 'Khác')")
        elif not value:
            errors.append(display_name)

    if errors:
        error_message = "Vui lòng nhập đầy đủ thông tin bắt buộc: " + ", ".join(errors) + "."
        logging.error(f"Validation failed: {error_message}")
        raise ValueError(error_message)

    logging.info("Thông tin người dùng hợp lệ (Chức vụ không bắt buộc).")
    return True

# --- Hàm Chuẩn hóa Tên File (Giữ nguyên) ---
def sanitize_filename(name):
    """
    Loại bỏ các ký tự không hợp lệ cho tên file và thay khoảng trắng bằng gạch dưới.
    """
    if not name or not isinstance(name, str):
        return ""

    invalid_chars = r'<>:"/\|?*'
    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '')

    # Thay thế khoảng trắng và gạch ngang bằng gạch dưới, loại bỏ gạch dưới thừa
    sanitized = sanitized.replace(" ", "_").replace("-", "_")
    sanitized = '_'.join(filter(None, sanitized.split('_'))) # Loại bỏ các phần tử rỗng do nhiều dấu gạch dưới liên tiếp
    sanitized = sanitized.strip('_') # Xóa gạch dưới ở đầu/cuối

    # Giới hạn độ dài tên file (tùy chọn)
    max_len = 100
    if len(sanitized) > max_len:
        # Cắt bớt và đảm bảo không cắt giữa từ (cắt tại dấu gạch dưới cuối cùng)
        sanitized = sanitized[:max_len].rsplit('_', 1)[0]

    # Trả về tên đã chuẩn hóa hoặc tên mặc định nếu kết quả rỗng
    return sanitized if sanitized else "invalid_name"

# --- Hàm Tạo Tên File (Giữ nguyên - vẫn tạo đuôi .txt) ---
def generate_filename(user_info, pc_info):
    """
    Tạo tên file .txt. Ưu tiên tên người dùng đã chuẩn hóa nếu có và hợp lệ.
    Nếu không, sử dụng tên máy tính đã chuẩn hóa.
    Cần pc_info để lấy tên máy tính làm fallback.
    """
    filename_base = DEFAULT_FILENAME_BASE
    try:
        # Ưu tiên tên người dùng
        user_name = str(user_info.get("Name", "")).strip()
        sanitized_user_name = sanitize_filename(user_name)

        if sanitized_user_name and sanitized_user_name != "invalid_name":
            filename_base = sanitized_user_name
            logging.info(f"Sử dụng tên người dùng đã chuẩn hóa cho tên file: '{filename_base}'")
        else:
            # Fallback về tên máy tính
            # Cần pc_info ở đây để lấy tên máy tính
            # Cập nhật đường dẫn để lấy Tên máy tính từ cấu trúc mới
            computer_name = pc_info.get("SystemInformation", {}).get("PC", {}).get("Tên máy tính", "UnknownPC")
            sanitized_computer_name = sanitize_filename(computer_name)

            if sanitized_computer_name and sanitized_computer_name != "invalid_name":
                # Thêm hậu tố '_info' để phân biệt nếu dùng tên máy tính
                filename_base = f"{sanitized_computer_name}_info"
                logging.info(f"Tên người dùng không hợp lệ/trống. Sử dụng tên máy tính: '{filename_base}'")
            else:
                # Fallback cuối cùng nếu cả hai đều không hợp lệ
                logging.warning(f"Cả tên người dùng và tên máy tính đều không tạo được tên file hợp lệ. Sử dụng fallback.")
                filename_base = DEFAULT_FILENAME_BASE # Đã được gán ở đầu

        # Đảm bảo filename_base không rỗng trước khi tạo tên file cuối cùng
        final_filename_base = filename_base if filename_base else DEFAULT_FILENAME_BASE
        filename = f"{final_filename_base}.txt"
        return filename

    except Exception as e:
        # Bắt lỗi chung trong quá trình tạo tên file
        logging.warning(f"Lỗi khi tạo tên file động, sử dụng tên mặc định '{DEFAULT_FILENAME_BASE}.txt': {e}", exc_info=True)
        return f"{DEFAULT_FILENAME_BASE}.txt"

# --- Hàm Ghi Dữ liệu vào File (Đơn giản hóa - chỉ ghi text) ---
def save_text_to_file(content, file_path):
    """
    Ghi nội dung chuỗi văn bản vào đường dẫn file được chỉ định.
    Tự động tạo thư mục nếu chưa tồn tại.
    """
    try:
        # Đảm bảo thư mục cha tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Ghi file với encoding utf-8
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logging.info(f"Đã lưu nội dung thành công vào: {file_path}")
        return True
    except IOError as e:
        # Lỗi liên quan đến đọc/ghi file
        logging.error(f"Lỗi I/O khi lưu file '{os.path.basename(file_path)}': {e}", exc_info=True)
        # Ném lại lỗi để lớp gọi có thể xử lý (ví dụ: hiển thị thông báo cho người dùng)
        raise IOError(f"Lỗi I/O khi lưu file: {e}")
    except Exception as e:
        # Các lỗi không mong muốn khác
        logging.error(f"Lỗi không xác định khi lưu file '{os.path.basename(file_path)}': {e}", exc_info=True)
        raise RuntimeError(f"Lỗi không xác định khi lưu file: {e}")

# --- Helper Formatting Functions ---

def _format_dict_items(data_dict, keys_map):
    """
    Helper để định dạng các mục từ dictionary dựa trên mapping key.
    keys_map: list of tuples (data_key, display_name)
    """
    lines = []
    if isinstance(data_dict, dict):
        # Các hằng số chỉ trạng thái "không có giá trị" hoặc "không xác định"
        UNAVAILABLE_VALUES = {None, "", NOT_IDENTIFIED, NOT_AVAILABLE}
        # Các chuỗi con chỉ báo lỗi cần được hiển thị nguyên văn
        ERROR_INDICATOR_SUBSTRINGS = {ERROR_FETCHING_INFO, ERROR_WMI_CONNECTION, NOT_FOUND}

        for data_key, display_name in keys_map:
            value = data_dict.get(data_key)
            display_value = NOT_AVAILABLE # Giá trị hiển thị mặc định là "Không khả dụng"

            if value in UNAVAILABLE_VALUES:
                display_value = NOT_AVAILABLE # Nếu giá trị là một trong các hằng số "không có", hiển thị "Không khả dụng"
            elif isinstance(value, str) and any(err_sub in value for err_sub in ERROR_INDICATOR_SUBSTRINGS):
                display_value = value # Nếu giá trị là chuỗi chứa thông báo lỗi, hiển thị nguyên văn chuỗi đó
            else:
                display_value = value # Trường hợp còn lại, hiển thị giá trị thực tế

            lines.append(f"  {display_name}: {display_value}")
    else:
        lines.append(f"  {ERROR_FETCHING_INFO} (Dữ liệu không hợp lệ)")
    return lines

def _format_list_of_dicts(data_list, item_title_prefix, item_formatter_func):
    """
    Helper để định dạng list các dictionary.
    item_formatter_func: hàm nhận 1 dict item và trả về list các dòng string.
    """
    lines = []
    if isinstance(data_list, list) and data_list:
        if isinstance(data_list[0], dict) and ("Lỗi" in data_list[0] or "Thông tin" in data_list[0]):
             lines.append(f"  {data_list[0].get('Lỗi', data_list[0].get('Thông tin', ERROR_FETCHING_INFO))}")
        else:
            for i, item in enumerate(data_list):
                if isinstance(item, dict):
                    lines.append(f"  - {item_title_prefix} {i+1}:")
                    lines.extend([f"    {line}" for line in item_formatter_func(item)]) # Thụt lề các dòng con
    elif isinstance(data_list, list) and not data_list: lines.append(f"  {NOT_FOUND}")
    else: lines.append(f"  {ERROR_FETCHING_INFO}")
    return lines

# --- Hàm Định dạng Thông tin Hệ thống Chi tiết ---
def format_system_details_to_string(system_info_data_dict):
    """
    Định dạng phần "SystemInformation" của dữ liệu PC thành chuỗi dễ đọc.
    """
    output_lines = ["**--- THÔNG TIN HỆ THỐNG ---**"] # Tiêu đề, bỏ dòng trống sau tiêu đề chính
    pc_data = system_info_data_dict.get("PC", {})
    screen_data = system_info_data_dict.get("Màn hình", [])

    # --- Thông tin Cơ bản & Hệ điều hành ---
    output_lines.append("**Thông tin Chung:**")
    basic_info_keys = [
        ("Tên máy tính", "Tên máy tính"),
        ("Loại máy", "Loại máy"),
        ("Hệ điều hành", "Hệ điều hành"),
        ("Phiên bản Windows", "Phiên bản HĐH"), # Đổi tên hiển thị
        ("Địa chỉ IP", "Địa chỉ IP"),
        ("Địa chỉ MAC", "Địa chỉ MAC"),
    ]
    for data_key, display_name in basic_info_keys:
        output_lines.append(f"  {display_name}: {pc_data.get(data_key, NOT_AVAILABLE)}") # Sử dụng get với default
    output_lines.append("**Cấu hình Phần cứng:**") # Đổi tên section

    # CPU
    cpu_info = pc_data.get("CPU", {})
    output_lines.append("  CPU:")
    if isinstance(cpu_info, dict) and cpu_info: # cpu_info is like {"Kiểu máy": "...", "Số lõi": ..., "Số luồng": ...}
        cpu_model = cpu_info.get("Kiểu máy", NOT_IDENTIFIED)
        cores = cpu_info.get("Số lõi", NOT_AVAILABLE)
        threads = cpu_info.get("Số luồng", NOT_AVAILABLE)

        # Hiển thị kiểu máy CPU, ngay cả khi là lỗi hoặc không xác định
        output_lines.append(f"    Kiểu máy: {cpu_model}")
        
        # Hiển thị số lõi và số luồng
        output_lines.append(f"    Số lõi: {cores}")
        output_lines.append(f"    Số luồng: {threads}")
    else:
        # Trường hợp lỗi lấy cả cụm CPU hoặc cpu_info không phải dict
        output_lines.append(f"    {ERROR_FETCHING_INFO} (Không có thông tin chi tiết CPU)")

    # RAM
    ram_info = pc_data.get("Bộ nhớ RAM", ERROR_FETCHING_INFO)
    output_lines.append(f"  Bộ nhớ RAM: {ram_info}")

    # Mainboard
    mainboard_info = pc_data.get("Mainboard", {})
    output_lines.append("  Mainboard:")
    if isinstance(mainboard_info, dict) and "Lỗi" not in mainboard_info and "Thông tin" not in mainboard_info:
        mainboard_keys = [
            ("Nhà sản xuất", "Nhà sản xuất"),
            ("Kiểu máy", "Kiểu máy"),
            ("Số Sê-ri", "Số Sê-ri"),
        ]
        output_lines.extend(_format_dict_items(mainboard_info, mainboard_keys))
    elif isinstance(mainboard_info, dict) and mainboard_info.get("Lỗi"):
        output_lines.append(f"    Lỗi: {mainboard_info['Lỗi']}")
    elif isinstance(mainboard_info, dict) and mainboard_info.get("Thông tin"):
         output_lines.append(f"    Thông tin: {mainboard_info['Thông tin']}")
    else:
        output_lines.append(f"    {ERROR_FETCHING_INFO}")

    # Ổ đĩa
    disk_details = pc_data.get("Ổ đĩa", [])
    output_lines.append("  Ổ đĩa:")
    def format_disk_item(disk):
        return [
            f"Kiểu máy: {disk.get('Kiểu máy', NOT_IDENTIFIED)}",
            f"Dung lượng (GB): {disk.get('Dung lượng (GB)', NOT_IDENTIFIED)}",
            f"Giao tiếp: {disk.get('Giao tiếp', NOT_IDENTIFIED)}",
            f"Loại phương tiện: {disk.get('Loại phương tiện', NOT_IDENTIFIED)}",
        ]
    output_lines.extend(_format_list_of_dicts(disk_details, "Ổ đĩa", format_disk_item))

    # Card đồ họa (GPU)
    gpu_details = pc_data.get("Card đồ họa (GPU)", [])
    output_lines.append("  Card đồ họa (GPU):")
    def format_gpu_item(gpu):
        return [
            f"Tên: {gpu.get('Tên', NOT_IDENTIFIED)}",
            f"Nhà sản xuất: {gpu.get('Nhà sản xuất', NOT_IDENTIFIED)}",
            f"Tổng bộ nhớ (MB): {gpu.get('Tổng bộ nhớ (MB)', NOT_AVAILABLE)}",
            f"Độ phân giải hiện tại: {gpu.get('Độ phân giải hiện tại', NOT_IDENTIFIED)}",
        ]
    output_lines.extend(_format_list_of_dicts(gpu_details, "GPU", format_gpu_item))

    # Màn hình (Chuyển vào cùng Phần cứng)
    output_lines.append("  Màn hình:")
    if isinstance(screen_data, list) and screen_data:
        first_item = screen_data[0]
        if isinstance(first_item, dict) and "Lỗi" in first_item:
            output_lines.append(f"    Lỗi: {first_item['Lỗi']}")
        elif isinstance(first_item, dict) and "Thông tin" in first_item:
             output_lines.append(f"    Thông tin: {first_item['Thông tin']}")
        else:
            def format_screen_item(screen):
                return [
                    f"Tên: {screen.get('Tên', NOT_IDENTIFIED)}",
                    f"Độ phân giải: {screen.get('Độ phân giải', NOT_IDENTIFIED)}",
                    f"Trạng thái: {screen.get('Trạng thái', NOT_AVAILABLE)}",
                ]
            output_lines.extend(_format_list_of_dicts(screen_data, "Màn hình", format_screen_item))

    return "\n".join(output_lines)

# --- Hàm Định dạng Tiện ích Kiểm tra Hệ thống ---
def format_system_checks_to_string(system_checks_data_dict):
    """
    Định dạng phần "SystemCheckUtilities" của dữ liệu PC thành chuỗi dễ đọc.
    """
    output_lines = [] # Bắt đầu list rỗng, tiêu đề sẽ được thêm nếu có dữ liệu

    if not system_checks_data_dict: # Handles None or empty dict {}
        # Nếu muốn luôn hiển thị section này ngay cả khi không có dữ liệu:
        # output_lines.append("**--- KIỂM TRA TÌNH TRẠNG HỆ THỐNG ---**")
        # output_lines.append("")
        # output_lines.append(f"  {NOT_AVAILABLE}")
        return "\n".join(output_lines) # Trả về sớm nếu không có dữ liệu

    if isinstance(system_checks_data_dict, dict) and "Lỗi" in system_checks_data_dict:
        output_lines.append("**--- KIỂM TRA TÌNH TRẠNG HỆ THỐNG ---**")
        # output_lines.append("") # Bỏ dòng trống
        output_lines.append(f"Lỗi khi lấy thông tin kiểm tra hệ thống: {system_checks_data_dict['Lỗi']}")
        return "\n".join(output_lines) # Trả về sớm nếu có lỗi tổng thể

    # Nếu không có lỗi tổng thể và có dữ liệu
    output_lines.append("**--- KIỂM TRA TÌNH TRẠNG HỆ THỐNG ---**")
    output_lines.append("")
    
    uptime = system_checks_data_dict.get("Thời gian hoạt động", NOT_AVAILABLE)
    output_lines.append(f"**Thời gian hoạt động hệ thống:**\n  {uptime}\n")

    disk_usage_list = system_checks_data_dict.get("Dung lượng ổ đĩa", [])
    output_lines.append("**Dung lượng ổ đĩa (Fixed Disks):**")
    def format_disk_usage_item(disk_item):
        name = disk_item.get("Ổ đĩa", NOT_IDENTIFIED)
        vol_name = disk_item.get("Tên ổ đĩa", "")
        total = disk_item.get("Tổng (GB)", NOT_AVAILABLE)
        free = disk_item.get("Còn trống (GB)", NOT_AVAILABLE)
        percent_free = disk_item.get("Tỷ lệ trống (%)", NOT_AVAILABLE)
        status = disk_item.get("Trạng thái", "")

        if status and NOT_AVAILABLE in str(status):
            return [f"{name} ({vol_name}): {status}"] # Bỏ thụt lề '  '
        else:
            lines = [f"{name} ({vol_name}): Còn trống {free} GB ({percent_free}%) - Tổng: {total} GB"] # Bỏ thụt lề '  '
            if status and status != STATUS_OK:
                lines.append(f"  Trạng thái: {status}") # Giữ thụt lề '  ' cho dòng con
            return lines
    output_lines.extend(_format_list_of_dicts(disk_usage_list, "Ổ đĩa", format_disk_usage_item))
    # output_lines.append("") # Bỏ dòng trống cuối section

    event_log_summary = system_checks_data_dict.get("Tóm tắt Event Log gần đây", {})
    output_lines.append("**Tóm tắt Event Log (24 giờ qua):**")
    if isinstance(event_log_summary, dict) and "Lỗi" not in event_log_summary and event_log_summary: # Thêm kiểm tra event_log_summary không rỗng
        output_lines.append(f"  System Log: {event_log_summary.get('System', {}).get('Errors', 0)} Lỗi, {event_log_summary.get('System', {}).get('Warnings', 0)} Cảnh báo")
        output_lines.append(f"  Application Log: {event_log_summary.get('Application', {}).get('Errors', 0)} Lỗi, {event_log_summary.get('Application', {}).get('Warnings', 0)} Cảnh báo")
        if event_log_summary.get("Ghi chú"): output_lines.append(f"  {event_log_summary['Ghi chú']}")
    elif isinstance(event_log_summary, dict) and event_log_summary.get("Lỗi"):
        output_lines.append(f"  Lỗi: {event_log_summary['Lỗi']} {event_log_summary.get('Chi tiết', '')}".strip())
    else: # Trường hợp event_log_summary là rỗng hoặc không có key "Lỗi"
        output_lines.append(f"  {NOT_AVAILABLE}")
    # output_lines.append("") # Bỏ dòng trống

    temperatures = system_checks_data_dict.get("Nhiệt độ hệ thống", [])
    output_lines.append("**Nhiệt độ Hệ thống:**")
    def format_temp_item(temp_item):
        return [f"{temp_item.get('Vùng', NOT_IDENTIFIED)}: {temp_item.get('Nhiệt độ (°C)', NOT_AVAILABLE)} °C"] # Bỏ thụt lề '  '
    output_lines.extend(_format_list_of_dicts(temperatures, "Cảm biến", format_temp_item))
    # output_lines.append("") # Bỏ dòng trống

    return "\n".join(output_lines)

# --- Hàm Định dạng Thông tin PC thành Chuỗi (Tổng hợp) ---
def format_pc_info_to_string(pc_info_dict):
    """
    Định dạng toàn bộ dữ liệu thông tin PC từ dictionary thành một chuỗi văn bản dễ đọc.
    Kết hợp thông tin hệ thống chi tiết và tiện ích kiểm tra.
    """
    all_output_lines = []

    system_info_data = pc_info_dict.get("SystemInformation")
    if system_info_data:
        all_output_lines.append(format_system_details_to_string(system_info_data))

    system_checks_data = pc_info_dict.get("SystemCheckUtilities")
    if system_checks_data:
        all_output_lines.append("\n" + format_system_checks_to_string(system_checks_data)) # Thêm dòng trống nếu có cả 2 phần

    # --- Lỗi gặp phải (Nếu có) ---
    errors = pc_info_dict.get("Lỗi gặp phải")
    if errors:
        all_output_lines.append("\n\n**--- LỖI GẶP PHẢI TRONG QUÁ TRÌNH LẤY THÔNG TIN ---**") # Tiêu đề rõ ràng hơn
        all_output_lines.append(f"  {errors}")

    # Kết hợp các dòng thành một chuỗi duy nhất
    return "\n".join(all_output_lines).strip()
# --- Khối Kiểm Tra (Có thể xóa hoặc cập nhật nếu cần) ---

# --- Hàm Định dạng Thông tin Người dùng cho Hiển thị/File ---
def format_user_info_for_display(user_info_dict):
    """
    Định dạng thông tin người dùng từ dictionary thành chuỗi dễ đọc cho file xuất.
    """
    if not isinstance(user_info_dict, dict):
        return "Lỗi: Dữ liệu người dùng không hợp lệ."

    lines = ["**--- THÔNG TIN NGƯỜI DÙNG ---**"]
    user_info_map = {
        "Name": "Tên người dùng",
        "Department": "Phòng Ban",
        "Floor": "Vị Trí Tầng",
        "Position": "Chức Vụ",
        "Notes": "Ghi Chú"
    }
    for key, display_name in user_info_map.items():
        lines.append(f"  {display_name}: {user_info_dict.get(key, '').strip() or NOT_AVAILABLE}")
    return "\n".join(lines)
if __name__ == "__main__": # Giữ lại 1 khối main để test
    print("Đang thu thập thông tin PC để kiểm tra định dạng...")
    # Đảm bảo import get_pc_info từ module functions
    from core.pc_info_functions import get_detailed_system_information, NOT_AVAILABLE # <-- Đổi tên hàm ở đây
    # from core.pc_info_functions import get_pc_info, NOT_AVAILABLE # Dòng cũ
    import json # Import json chỉ cho mục đích test ở đây

    test_pc_info = get_detailed_system_information() # Sử dụng tên hàm mới

    print("\n--- Dữ liệu gốc (Dictionary) ---")
    print(json.dumps(test_pc_info, indent=4, ensure_ascii=False))

    print("\n--- Định dạng Thông tin Hệ thống Chi tiết ---")
    system_info_formatted = format_system_details_to_string(test_pc_info.get("SystemInformation", {}))
    print(system_info_formatted)

    print("\n--- Định dạng Tiện ích Kiểm tra Hệ thống ---")
    system_checks_formatted = format_system_checks_to_string(test_pc_info.get("SystemCheckUtilities", {}))
    print(system_checks_formatted)

    print("\n--- Định dạng Tổng hợp (như file báo cáo) ---")
    combined_formatted_string = format_pc_info_to_string(test_pc_info)
    print(combined_formatted_string)

    if test_pc_info.get("Lỗi gặp phải"):
        print(f"\n**Lỗi chung:** {test_pc_info['Lỗi gặp phải']}")

    # Ví dụ lưu file đã định dạng (bỏ comment nếu muốn thử)
    # test_user_info = {"Name": "Nguoi_Dung_Test", "Department": "IT", "Floor": "Tầng 5"} # Cần thông tin để tạo tên file
    # filename = generate_filename(test_user_info, test_pc_info)
    # output_dir = "output_test" # Thư mục lưu trữ thử nghiệm
    # file_path = os.path.join(output_dir, filename)
    # try:
    #     save_text_to_file(combined_formatted_string, file_path) # Lưu chuỗi tổng hợp
    #     print(f"\nĐã lưu thử vào: {file_path}")
    # except Exception as e:
    #     print(f"\nLỗi khi lưu file thử: {e}")
