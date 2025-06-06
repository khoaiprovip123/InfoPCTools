## 1. core/pc_info_functions.py
# Chứa các hàm xử lý thông tin PC
import subprocess
import platform
import psutil
import uuid
import socket
import win32com.client
import os
import pywintypes
import logging
import shutil # For file operations like temp file deletion
import ctypes # For checking admin rightsimport platform # Ensure platform is imported for ping
from datetime import datetime, timedelta # Thêm import datetime và timedelta
import locale # For preferred encoding
import time # For disk speed test
import tempfile # For disk speed test
import win32serviceutil, win32service # For optimizing windows services
import json # Thêm import json cho phần if __name__ == "__main__":
import winreg # Thêm import winreg để truy cập Registry

# --- Cấu hình Logging ---
# Cấu hình cơ bản, có thể được ghi đè ở file chính
logging.basicConfig(
     format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants (Giữ nguyên tiếng Việt) ---
ERROR_WMI_CONNECTION = "Lỗi kết nối WMI"
ERROR_FETCHING_INFO = "Lỗi khi lấy thông tin"
NOT_AVAILABLE = "Không khả dụng"
NOT_FOUND = "Không tìm thấy"
NOT_IDENTIFIED = "Không xác định"
# Thêm hằng số cho loại máy
MACHINE_TYPE_DESKTOP = "PC"
MACHINE_TYPE_LAPTOP = "Laptop"
MACHINE_TYPE_UNKNOWN = "Không xác định"
STATUS_OK = "Tốt"
STATUS_WARNING = "Cảnh báo"
STATUS_CRITICAL = "Nghiêm trọng"

# --- WMI Helper ---
def _connect_wmi():
    """
    Thiết lập kết nối WMI.
    Trả về tuple (đối tượng service WMI, cờ báo đã khởi tạo COM).
    Trả về (None, False) nếu lỗi.
    """
    com_initialized = False # Khởi tạo cờ
    try:
        try:
            # Thử khởi tạo COM. Nếu đã khởi tạo, nó sẽ không làm gì.
            # Nếu chưa, nó sẽ khởi tạo và ta cần giải phóng sau.
            win32com.client.pythoncom.CoInitialize()
            com_initialized = True
        except pywintypes.com_error:
            # Lỗi nếu COM đã được khởi tạo bởi luồng khác với mô hình khác (ít gặp)
            # Hoặc nếu đã khởi tạo trong cùng luồng (không phải lỗi thực sự)
            com_initialized = False # Giả định là đã khởi tạo trước đó hoặc không cần quản lý
            logging.debug("COM có thể đã được khởi tạo trước đó.")

        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\CIMV2")
        logging.info("Kết nối WMI thành công.")
        return service, com_initialized
    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.error(f"Lỗi kết nối WMI: {e}", exc_info=True) # Changed to True for more detailed traceback
        # Nếu lỗi kết nối, đảm bảo giải phóng COM nếu đã khởi tạo ở đây
        if com_initialized:
            try: win32com.client.pythoncom.CoUninitialize()
            except Exception as com_e: logging.error(f"Lỗi khi giải phóng COM sau khi kết nối thất bại: {com_e}")
        return None, False # Trả về None và False vì kết nối thất bại

def _get_wmi_property(wmi_object, property_name, default_value=NOT_IDENTIFIED):
    """Helper để lấy thuộc tính WMI một cách an toàn."""
    try:
        value = getattr(wmi_object, property_name, default_value)
        if value is None: return default_value
        if isinstance(value, str): return value.strip()
        return value
    except (pywintypes.com_error, AttributeError):
        return default_value

# --- Information Gathering Functions ---

# --- CPU Info Function (Updated) ---
def get_cpu_info(wmi_service): # Thêm wmi_service làm tham số
    """
    Lấy thông tin chi tiết về CPU. Ưu tiên WMI trực tiếp, fallback về wmic, cuối cùng là platform.
    """
    cpu_name = NOT_IDENTIFIED
    clock_speed = NOT_IDENTIFIED # Có thể lấy thêm tốc độ nếu muốn

    # --- Ưu tiên 1: Dùng WMI Service trực tiếp ---
    if wmi_service:
        try:
            processors = wmi_service.ExecQuery("SELECT Name, CurrentClockSpeed FROM Win32_Processor")
            processor_list = list(processors) # Chuyển thành list để kiểm tra
            if processor_list:
                # Lấy thông tin từ processor đầu tiên tìm thấy
                processor = processor_list[0]
                cpu_name = _get_wmi_property(processor, "Name", NOT_IDENTIFIED)
                clock_speed = _get_wmi_property(processor, "CurrentClockSpeed", NOT_IDENTIFIED)
                logging.info("Lấy thông tin CPU thành công qua WMI Service.")
                # Trả về kết quả nếu lấy được tên
                if cpu_name != NOT_IDENTIFIED:
                     # Bạn có thể trả về cả tốc độ nếu muốn:
                     # return f"{cpu_name} @ {clock_speed} MHz" if clock_speed != NOT_IDENTIFIED else cpu_name
                     return cpu_name
            else:
                logging.warning("Truy vấn WMI Win32_Processor không trả về kết quả.")
        except (pywintypes.com_error, Exception) as wmi_e:
            logging.warning(f"Lỗi khi lấy thông tin CPU qua WMI Service ({type(wmi_e).__name__}), thử wmic: {wmi_e}")
    else:
         logging.warning("Không có WMI Service, thử wmic.")

    # --- Ưu tiên 2: Dùng wmic qua subprocess (Fallback 1) ---
    try:
        # Sử dụng CREATE_NO_WINDOW để ẩn cửa sổ console của wmic
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.check_output(
            "wmic cpu get name,CurrentClockSpeed /value",
            shell=False, # An toàn hơn khi không dùng shell=True
            text=True, stderr=subprocess.PIPE,
            encoding='utf-8', errors='ignore', timeout=15,
            startupinfo=startupinfo # Thêm startupinfo
        )
        parsed_name = NOT_IDENTIFIED
        parsed_speed = NOT_IDENTIFIED
        for line in result.strip().splitlines():
            line = line.strip() # Loại bỏ khoảng trắng thừa
            if line.startswith("Name="):
                parsed_name = line.split("=", 1)[1].strip()
            elif line.startswith("CurrentClockSpeed="):
                parsed_speed = line.split("=", 1)[1].strip()

        if parsed_name and parsed_name != NOT_IDENTIFIED: # Chỉ cần tên là đủ
            logging.info("Lấy thông tin CPU thành công qua wmic.")
            # return f"{parsed_name} @ {parsed_speed} MHz" if parsed_speed != NOT_IDENTIFIED else parsed_name
            return parsed_name
        else:
             logging.warning("Lệnh wmic không trả về tên CPU hợp lệ.")
             # Không raise lỗi ở đây để chuyển sang fallback tiếp theo

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, Exception) as sub_e:
        logging.warning(f"Lỗi khi lấy thông tin CPU qua wmic ({type(sub_e).__name__}), thử platform: {sub_e}")

    # --- Ưu tiên 3: Dùng platform (Fallback 2) ---
    try:
        cpu_name_platform = platform.processor()
        if cpu_name_platform:
            # Kiểm tra xem có phải chuỗi generic không (tùy chọn)
            if "Family" in cpu_name_platform and "Stepping" in cpu_name_platform:
                 logging.warning(f"Platform trả về thông tin CPU generic: '{cpu_name_platform}'")
                 # Bạn có thể quyết định trả về NOT_IDENTIFIED ở đây nếu muốn
                 # return NOT_IDENTIFIED
            logging.info(f"Lấy thông tin CPU qua platform: '{cpu_name_platform}'")
            return cpu_name_platform
        else:
             logging.warning("Platform.processor() trả về chuỗi rỗng.")
             return f"{ERROR_FETCHING_INFO} CPU (platform rỗng)"
    except Exception as plat_e:
        logging.error(f"Lỗi khi lấy thông tin CPU qua platform: {plat_e}")
        return f"{ERROR_FETCHING_INFO} CPU (platform lỗi)"

    # Nếu tất cả đều thất bại
    logging.error("Không thể lấy thông tin CPU từ mọi phương thức.")
    return f"{ERROR_FETCHING_INFO} CPU (tất cả thất bại)"

# --- Constants for Disk Info Enhancement ---
MSFT_BUS_TYPE_MAP = {
    0: "Unknown", 1: "SCSI", 2: "ATAPI", 3: "ATA", 4: "IEEE 1394",
    5: "SSA", 6: "Fibre Channel", 7: "USB", 8: "RAID", 9: "iSCSI",
    10: "SAS", 11: "SATA", 12: "SD", 13: "MMC", 17: "NVMe",
}

MSFT_MEDIA_TYPE_MAP = {
    0: NOT_IDENTIFIED,  # Unspecified
    3: "HDD",
    4: "SSD",
    5: "SCM",           # Storage Class Memory
}
# --- End Constants for Disk Info Enhancement ---


def get_disk_drive_details(wmi_service): # Renamed from a comment block to a function definition
    """
    Lấy thông tin chi tiết về tất cả ổ cứng vật lý.
    Trả về list các dict hoặc list chứa lỗi/thông tin.
    Luôn bao gồm "Loại phương tiện" (HDD/SSD/Không xác định).
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION}] # Key tiếng Việt
    
    msft_physical_disks_data = {}
    try:
        _local_com_init_storage = False
        service_msft_storage = None
        try:
            win32com.client.pythoncom.CoInitialize()
            _local_com_init_storage = True
        except pywintypes.com_error:
            logging.debug("COM already initialized for MSFT_PhysicalDisk query or different model.")

        wmi_locator_msft = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service_msft_storage = wmi_locator_msft.ConnectServer(".", r"root\Microsoft\Windows\Storage")
        logging.info("Successfully connected to WMI namespace root\\Microsoft\\Windows\\Storage for MSFT_PhysicalDisk.")
        if service_msft_storage:
            msft_disks_query = service_msft_storage.ExecQuery("SELECT DeviceId, BusType, MediaType, FriendlyName FROM MSFT_PhysicalDisk")
            for disk_msft_raw in msft_disks_query:
                dev_id = _get_wmi_property(disk_msft_raw, "DeviceId")
                if dev_id is not None:
                    msft_physical_disks_data[str(dev_id)] = {
                        "BusType": _get_wmi_property(disk_msft_raw, "BusType", default_value=-1),
                        "MediaType": _get_wmi_property(disk_msft_raw, "MediaType", default_value=-1),
                        "FriendlyName": _get_wmi_property(disk_msft_raw, "FriendlyName", NOT_IDENTIFIED)
                    }
            logging.info(f"Fetched {len(msft_physical_disks_data)} entries from MSFT_PhysicalDisk.")
    except (pywintypes.com_error, Exception) as e_msft:
        logging.warning(f"Could not query MSFT_PhysicalDisk: {e_msft}. Falling back to Win32_DiskDrive only for extended info.")
    finally:
        if _local_com_init_storage:
            win32com.client.pythoncom.CoUninitialize()
            logging.debug("COM uninitialized for MSFT_PhysicalDisk query.")
    disk_details = []
    try:
        # Query Win32_DiskDrive, ensure Index is included for matching with MSFT_PhysicalDisk.DeviceId
        disks_w32_query = wmi_service.ExecQuery("SELECT Model, Size, MediaType, InterfaceType, Index, DeviceID FROM Win32_DiskDrive")
        # Kiểm tra xem có kết quả không trước khi lặp
        disk_w32_list = list(disks_w32_query)
        if not disk_w32_list:
            return [{"Thông tin": f"{NOT_FOUND} ổ cứng vật lý nào."}] # Key tiếng Việt

        for disk_w32 in disk_w32_list:
            model = _get_wmi_property(disk_w32, "Model")
            size = _get_wmi_property(disk_w32, "Size", default_value=0)
            disk_index_w32 = _get_wmi_property(disk_w32, "Index", default_value=-1) # Integer
            
            # Initialize with Win32_DiskDrive values as fallback
            interface_type_str = _get_wmi_property(disk_w32, "InterfaceType")
            media_type_str = NOT_IDENTIFIED

            # Try to get more accurate info from MSFT_PhysicalDisk
            disk_msft_info = msft_physical_disks_data.get(str(disk_index_w32))

            if disk_msft_info:
                logging.debug(f"Disk '{model}' (Index {disk_index_w32}): Found matching MSFT_PhysicalDisk entry (FriendlyName: {disk_msft_info.get('FriendlyName')}).")
                # Get Interface Type from MSFT_PhysicalDisk.BusType
                msft_bus_type_code = disk_msft_info.get("BusType", -1)
                mapped_msft_interface = MSFT_BUS_TYPE_MAP.get(msft_bus_type_code)
                if mapped_msft_interface and mapped_msft_interface not in ["Unknown", NOT_IDENTIFIED]:
                    interface_type_str = mapped_msft_interface
                    logging.debug(f"Disk '{model}': Using InterfaceType '{interface_type_str}' from MSFT_PhysicalDisk.BusType {msft_bus_type_code}.")
                elif mapped_msft_interface == "Unknown" and interface_type_str in (None, "", NOT_IDENTIFIED, "Unknown"):
                    interface_type_str = "Unknown" # If Win32 was also bad, use MSFT's Unknown

                # Get Media Type from MSFT_PhysicalDisk.MediaType
                msft_media_type_code = disk_msft_info.get("MediaType", -1)
                mapped_msft_media = MSFT_MEDIA_TYPE_MAP.get(msft_media_type_code)
                if mapped_msft_media and mapped_msft_media != NOT_IDENTIFIED:
                    media_type_str = mapped_msft_media
                    logging.debug(f"Disk '{model}': Using MediaType '{media_type_str}' from MSFT_PhysicalDisk.MediaType {msft_media_type_code}.")

            # If MSFT_PhysicalDisk didn't provide a definitive media type, use Win32_DiskDrive.MediaType
            if media_type_str == NOT_IDENTIFIED:
                media_type_code_w32 = _get_wmi_property(disk_w32, "MediaType", default_value=0)
                if media_type_code_w32 == 4: media_type_str = "SSD"
                elif media_type_code_w32 == 3: media_type_str = "HDD"
                elif media_type_code_w32 == 5: media_type_str = "SCM"
                # else: media_type_str remains NOT_IDENTIFIED
                if media_type_str != NOT_IDENTIFIED:
                     logging.debug(f"Disk '{model}': Using MediaType '{media_type_str}' from Win32_DiskDrive.MediaType {media_type_code_w32}.")
                elif disk_msft_info is None: # Only log if MSFT info was not available at all
                     logging.debug(f"Disk '{model}': Win32_DiskDrive.MediaType {media_type_code_w32} did not map to a known type. MediaType remains '{media_type_str}'.")

            # Use > 0 check for size conversion
            size_gb = int(size) // (1024 ** 3) if size and int(size) > 0 else NOT_IDENTIFIED

            # Final Heuristic: If determined InterfaceType is NVMe, it's an SSD.
            if interface_type_str and isinstance(interface_type_str, str) and "NVMe" in interface_type_str:
                if media_type_str != "SSD":
                    logging.info(
                        f"Disk '{model}': Final InterfaceType is '{interface_type_str}'. "
                        f"Overriding MediaType from '{media_type_str}' to 'SSD'. "
                    )
                    media_type_str = "SSD"

            disk_info = {
                "Kiểu máy": model,             # Key tiếng Việt
                "Dung lượng (GB)": size_gb,   # Key tiếng Việt
                "Giao tiếp": interface_type_str if interface_type_str else NOT_IDENTIFIED,  # Key tiếng Việt
                "Loại phương tiện": media_type_str
            }
            disk_details.append(disk_info)
        # Trả về danh sách nếu có
        return disk_details

    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi xử lý thông tin ổ cứng: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} ổ cứng: {e}"}] # Key tiếng Việt


def get_gpu_details(wmi_service):
    """
    Lấy thông tin chi tiết về GPU.
    Trả về list các dict hoặc list chứa lỗi/thông tin.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION}]

    details = []
    try:
        # Thêm DriverVersion và DriverDate
        video_controllers = wmi_service.ExecQuery("SELECT Name, AdapterCompatibility, AdapterRAM, CurrentHorizontalResolution, CurrentVerticalResolution, DriverVersion, DriverDate FROM Win32_VideoController")
        vc_list = list(video_controllers)
        if not vc_list:
             return [{"Thông tin": f"{NOT_FOUND} GPU nào."}]
        note_added = False

        for controller in vc_list:
            name = _get_wmi_property(controller, "Name", NOT_AVAILABLE)
            manufacturer = _get_wmi_property(controller, "AdapterCompatibility", NOT_AVAILABLE)
            total_memory = _get_wmi_property(controller, "AdapterRAM", default_value=0)
            h_res = _get_wmi_property(controller, "CurrentHorizontalResolution", default_value=None)
            v_res = _get_wmi_property(controller, "CurrentVerticalResolution", default_value=None)
            driver_version = _get_wmi_property(controller, "DriverVersion", NOT_AVAILABLE)
            driver_date_wmi = _get_wmi_property(controller, "DriverDate", None) # YYYYMMDDHHMMSS.ffffff+/-UUU

            driver_date_formatted = NOT_AVAILABLE
            if driver_date_wmi:
                try:
                    # Chuyển đổi sang đối tượng datetime rồi định dạng lại
                    dt_obj = datetime.strptime(driver_date_wmi.split('.')[0], "%Y%m%d%H%M%S")
                    driver_date_formatted = dt_obj.strftime("%d/%m/%Y")
                except ValueError:
                    driver_date_formatted = driver_date_wmi # Để nguyên nếu không parse được


            # Tính toán bộ nhớ và độ phân giải
            # Use > 0 check for memory conversion
            total_memory_mb = round(total_memory / (1024 ** 2)) if total_memory and total_memory > 0 else NOT_AVAILABLE # Simplified: total_memory is already an int
            resolution = f"{h_res}x{v_res}" if h_res and v_res else NOT_IDENTIFIED

            gpu_info = {
                "Tên": name,                      # Key tiếng Việt
                "Nhà sản xuất": manufacturer,     # Key tiếng Việt
                "Tổng bộ nhớ (MB)": total_memory_mb, # Key tiếng Việt
                "Độ phân giải hiện tại": resolution, # Key tiếng Việt
                "Phiên bản Driver": driver_version, # Key tiếng Việt
                "Ngày Driver": driver_date_formatted, # Key tiếng Việt
            }
            details.append(gpu_info)
        return details
    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin GPU: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} GPU: {e}"}]

def get_screen_details(wmi_service):
    """
    Lấy thông tin màn hình: Tên, Độ phân giải (pixels), Tỷ lệ khung hình.
    Trả về list các dict hoặc list chứa lỗi/thông tin.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION}]

    details = []
    def gcd(a, b):
        while(b):
            a, b = b, a % b
        return a

    def get_aspect_ratio(width, height):
        if width and height and isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            common_divisor = gcd(width, height)
            return f"{width // common_divisor}:{height // common_divisor}"
        return NOT_IDENTIFIED
    gpu_resolution = NOT_IDENTIFIED
    # Lấy độ phân giải từ GPU (chỉ cần lấy 1 lần)
    try:
        vcs = wmi_service.ExecQuery("SELECT CurrentHorizontalResolution, CurrentVerticalResolution FROM Win32_VideoController")
        # Lấy độ phân giải từ card đồ họa đầu tiên có thông tin
        for vc in vcs:
            hres = _get_wmi_property(vc, "CurrentHorizontalResolution")
            vres = _get_wmi_property(vc, "CurrentVerticalResolution")
            if hres and vres and isinstance(hres, int) and isinstance(vres, int) and hres > 0 and vres > 0:
                gpu_resolution = f"{hres}x{vres}" # Độ phân giải pixel
                aspect_ratio_str = get_aspect_ratio(hres, vres)
                break # Lấy được rồi thì dừng
            else: # Nếu vòng lặp không break (không tìm thấy độ phân giải hợp lệ)
                aspect_ratio_str = NOT_IDENTIFIED
    except (pywintypes.com_error, Exception) as e:
        logging.warning(f"Không lấy được độ phân giải từ GPU: {e}")
        aspect_ratio_str = NOT_IDENTIFIED

    # Lấy thông tin màn hình
    try:
        monitors = wmi_service.ExecQuery("SELECT Name, Status, PNPDeviceID FROM Win32_DesktopMonitor")
        monitor_list = list(monitors)
        if not monitor_list:
             return [{"Thông tin": f"{NOT_FOUND} màn hình nào."}]

        monitor_count = 0
        for monitor in monitor_list:
            monitor_count += 1
            monitor_name = _get_wmi_property(monitor, "Name", f"Màn hình {monitor_count}") # Tiếng Việt
            status = _get_wmi_property(monitor, "Status", NOT_AVAILABLE)
            pnp_device_id = _get_wmi_property(monitor, "PNPDeviceID", None)
            device_manager_name = monitor_name # Mặc định dùng tên từ DesktopMonitor

            # Cố gắng lấy tên thân thiện hơn từ PnPEntity nếu có PNPDeviceID
            if pnp_device_id:
                try:
                    # Escape backslashes and single quotes for WQL query
                    pnp_device_id_escaped = pnp_device_id.replace("\\", "\\\\").replace("'", "''")
                    query = f"SELECT Name FROM Win32_PnPEntity WHERE DeviceID = '{pnp_device_id_escaped}'"
                    pnp_entities = wmi_service.ExecQuery(query)
                    pnp_list = list(pnp_entities)
                    if pnp_list:
                        pnp_name = _get_wmi_property(pnp_list[0], "Name", None)
                        if pnp_name: device_manager_name = pnp_name # Ưu tiên tên từ PnPEntity
                except (pywintypes.com_error, Exception) as e_pnp:
                    # Lỗi này không nghiêm trọng, chỉ là không lấy được tên đẹp hơn
                    logging.warning(f"Lỗi khi truy vấn Win32_PnPEntity cho {pnp_device_id}: {e_pnp}")

            details.append({
                "Tên": device_manager_name,             # Key tiếng Việt
                "Độ phân giải (pixels)": gpu_resolution, # Key tiếng Việt
                "Tỷ lệ khung hình": aspect_ratio_str,    # Key tiếng Việt
                "Kích thước (đường chéo)": f"{NOT_AVAILABLE} (qua WMI)", # Key tiếng Việt
                "Trạng thái": status                     # Key tiếng Việt
            })
        return details

    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin màn hình: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} màn hình: {e}"}]

def get_mainboard_info(wmi_service):
    """
    Lấy thông tin về mainboard.
    Trả về dict chứa thông tin hoặc dict chứa lỗi/thông tin.
    """
    if not wmi_service:
        return {"Lỗi": ERROR_WMI_CONNECTION}

    # Common default serial number values that should be treated as NOT_IDENTIFIED
    DEFAULT_SERIAL_VALUES = frozenset([
        "none", "to be filled by o.e.m.", "default string", "system serial number",
        "0", "", "not applicable", "not specified", "serialnumber", "o.e.m."
    ])

    try:
        baseboard = wmi_service.ExecQuery("SELECT Manufacturer, Product, SerialNumber FROM Win32_BaseBoard")
        board_list = list(baseboard)
        if board_list:
            board = board_list[0]
            manufacturer = _get_wmi_property(board, "Manufacturer")
            product = _get_wmi_property(board, "Product")
            serial_number = _get_wmi_property(board, "SerialNumber")

            # Chuẩn hóa số serial nếu nó là giá trị mặc định không hữu ích
            if serial_number.lower() in DEFAULT_SERIAL_VALUES:
                 serial_number = NOT_IDENTIFIED

            return {
                "Nhà sản xuất": manufacturer, # Key tiếng Việt
                "Kiểu máy": product,       # Key tiếng Việt
                "Số Sê-ri": serial_number   # Key tiếng Việt
            }
        else:
            return {"Thông tin": f"{NOT_FOUND} thông tin mainboard"}

    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin mainboard: {e}", exc_info=True)
        return {"Lỗi": f"{ERROR_FETCHING_INFO} mainboard: {e}"}

# --- PC Check Utilities ---

def get_system_uptime():
    """Lấy thời gian hoạt động của hệ thống."""
    try:
        boot_time_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_time_timestamp)
        now = datetime.now()
        uptime_delta = now - boot_time

        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        uptime_str_parts = []
        if days > 0:
            uptime_str_parts.append(f"{days} ngày")
        if hours > 0:
            uptime_str_parts.append(f"{hours} giờ")
        # Luôn hiển thị phút nếu thời gian hoạt động dưới 1 giờ hoặc có phút
        if minutes > 0 or (days == 0 and hours == 0):
            uptime_str_parts.append(f"{minutes} phút")

        return ", ".join(uptime_str_parts) if uptime_str_parts else "Vừa khởi động"
    except Exception as e:
        logging.error(f"Lỗi khi lấy thời gian uptime: {e}", exc_info=True)
        return f"{ERROR_FETCHING_INFO} Uptime"

def get_disk_partitions_usage(wmi_service):
    """
    Lấy thông tin sử dụng dung lượng cho các ổ đĩa cứng cục bộ (Fixed Disks).
    Trả về list các dict hoặc list chứa lỗi.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kiểm tra dung lượng ổ đĩa."}]

    partitions_usage = []
    try:
        # DriveType=3 tương ứng với Local Disk (ổ đĩa cục bộ)
        logical_disks = wmi_service.ExecQuery("SELECT DeviceID, Size, FreeSpace, VolumeName FROM Win32_LogicalDisk WHERE DriveType=3")
        disk_list = list(logical_disks)

        if not disk_list:
            return [{"Thông tin": f"{NOT_FOUND} ổ đĩa cứng cục bộ nào."}]

        for disk in disk_list:
            device_id = _get_wmi_property(disk, "DeviceID", NOT_IDENTIFIED)
            total_size_bytes = _get_wmi_property(disk, "Size", default_value=0) # Là string, cần convert
            free_space_bytes = _get_wmi_property(disk, "FreeSpace", default_value=0) # Là string, cần convert
            volume_name = _get_wmi_property(disk, "VolumeName", "Không có tên")

            # Chuyển đổi sang số nếu cần
            total_size_bytes = int(total_size_bytes) if str(total_size_bytes).isdigit() else 0
            free_space_bytes = int(free_space_bytes) if str(free_space_bytes).isdigit() else 0

            if total_size_bytes == 0:
                partitions_usage.append({
                    "Ổ đĩa": device_id, "Tên ổ đĩa": volume_name,
                    "Trạng thái": f"{NOT_AVAILABLE} (Tổng dung lượng là 0)"
                })
                continue

            total_gb = round(total_size_bytes / (1024**3), 2)
            free_gb = round(free_space_bytes / (1024**3), 2)
            used_gb = round((total_size_bytes - free_space_bytes) / (1024**3), 2)
            percent_free = round((free_space_bytes / total_size_bytes) * 100, 1)

            status = STATUS_OK
            if percent_free < 5:
                status = f"{STATUS_CRITICAL} (Còn dưới 5% dung lượng trống)"
            elif percent_free < 15:
                status = f"{STATUS_WARNING} (Còn dưới 15% dung lượng trống)"

            partitions_usage.append({
                "Ổ đĩa": device_id, "Tên ổ đĩa": volume_name,
                "Tổng (GB)": total_gb, "Đã dùng (GB)": used_gb,
                "Còn trống (GB)": free_gb, "Tỷ lệ trống (%)": percent_free,
                "Trạng thái": status
            })
        return partitions_usage
    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin dung lượng ổ đĩa: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} dung lượng ổ đĩa: {str(e)}"}]

def get_wmi_utc_datetime_str(dt_object_utc):
    """Chuyển đổi đối tượng datetime Python UTC thành chuỗi datetime WMI (DMTF format)."""
    return dt_object_utc.strftime('%Y%m%d%H%M%S') + ".000000+000"

def get_recent_event_log_summary(wmi_service, hours_ago=24):
    """Đếm số lượng lỗi và cảnh báo trong System/Application event logs gần đây."""
    if not wmi_service:
        return {"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kiểm tra Event Logs."}

    summary = {"System": {"Errors": 0, "Warnings": 0}, "Application": {"Errors": 0, "Warnings": 0},
               "Ghi chú": f"Tổng hợp lỗi/cảnh báo trong {hours_ago} giờ qua. Kiểm tra Event Viewer để biết chi tiết."}
    try:

        # Make threshold_utc_dt timezone-aware (UTC)
        from datetime import timezone as dt_timezone # Import timezone
        threshold_utc_dt = datetime.now(dt_timezone.utc) - timedelta(hours=hours_ago)

        event_types_map = {1: "Errors", 2: "Warnings"}

        for logfile in ["System", "Application"]:
            # Modified Query: Remove TimeGenerated filter from WQL, fetch all relevant event types
            query = (f"SELECT EventType, TimeGenerated FROM Win32_NTLogEvent WHERE Logfile = '{logfile}' "
                     f"AND (EventType = 1 OR EventType = 2)")
            raw_events_query = wmi_service.ExecQuery(query)
            for event_obj in raw_events_query:
                time_generated_wmi_val = _get_wmi_property(event_obj, "TimeGenerated", None)
                if time_generated_wmi_val is not None:
                    try:
                        # Ensure time_generated_as_str is unequivocally a string.
                        time_generated_as_str = str(time_generated_wmi_val)
                        # CRITICAL LOG: Check type and representation right before the call
                        logging.debug(f"DEBUG: Argument for pywintypes.Time - Original WMI val: '{time_generated_wmi_val}', Type: {type(time_generated_wmi_val)}")
                        # Extract the main datetime part (YYYYMMDDHHMMSS)
                        # WMI datetime format is YYYYMMDDHHMMSS.ffffff+/-UUU
                        # We only need the YYYYMMDDHHMMSS part for pywintypes.Time
                        if '.' in time_generated_as_str:
                            parsable_time_str = time_generated_as_str.split('.')[0]
                        else: # Handle cases where there might not be a fractional part or offset
                            parsable_time_str = time_generated_as_str[:14] # Take first 14 chars
                        
                        # Convert string to datetime object first
                        # Assume WMI time is UTC, make the datetime object UTC-aware
                        dt_object_for_pywintypes = datetime.strptime(parsable_time_str, "%Y%m%d%H%M%S").replace(tzinfo=dt_timezone.utc)
                        event_time_pywintypes = pywintypes.Time(dt_object_for_pywintypes) # type: ignore
                        
                        if event_time_pywintypes >= threshold_utc_dt: # Compare timezone-aware datetimes
                            event_type_code = _get_wmi_property(event_obj, "EventType", 0)
                            if event_type_code in event_types_map:
                                summary[logfile][event_types_map[event_type_code]] += 1
                    except (pywintypes.error, ValueError) as e_time: # type: ignore
                        # Log both the original value and its string representation for better debugging
                        logging.warning(f"Không thể phân tích TimeGenerated (orig: '{time_generated_wmi_val}', parsed_attempt: '{parsable_time_str if 'parsable_time_str' in locals() else 'N/A'}') cho log {logfile}: {e_time}")
        return summary
    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.error(f"Lỗi khi lấy tóm tắt Event Log: {e}", exc_info=True)
        summary["Lỗi"] = f"{ERROR_FETCHING_INFO} Event Logs: {str(e)}"
        return summary

# --- Main Function to Gather Core System Info & Basic Checks ---
def get_detailed_system_information():
    """
    Thu thập và định dạng thông tin cấu hình PC tổng hợp (với keys tiếng Việt).
    Bao gồm cả phân loại PC/Laptop.
    """
    wmi_service, com_initialized = _connect_wmi()

    # Dữ liệu cho phần thông tin hệ thống chi tiết
    system_details_pc_data = {}
    system_details_screen_data = []
    error_messages = []

    try:
        # --- Thông tin hệ thống cơ bản ---
        # Initialize pc_data for this scope, was missing
        try: system_details_pc_data["Tên máy tính"] = platform.node() # Key tiếng Việt
        except Exception as e:
            logging.error(f"Lỗi lấy Tên máy tính: {e}")
            system_details_pc_data["Tên máy tính"] = ERROR_FETCHING_INFO
            error_messages.append("Tên máy tính")

        # --- Xác định Loại máy (PC/Laptop) ---
        system_details_pc_data["Loại máy"] = NOT_IDENTIFIED # Giá trị mặc định

        if wmi_service:
            try:
                # Truy vấn Win32_SystemEnclosure để lấy ChassisTypes
                system_enclosures = wmi_service.ExecQuery("SELECT ChassisTypes FROM Win32_SystemEnclosure")
                enclosure_list = list(system_enclosures)

                if enclosure_list:
                    enclosure = enclosure_list[0]
                    # Lấy danh sách các loại chassis (thường chỉ có 1 phần tử chính)
                    chassis_types_tuple = getattr(enclosure, "ChassisTypes", None)

                    # Use > 0 check for tuple length
                    if chassis_types_tuple and len(chassis_types_tuple) > 0:
                        try:
                            # Lấy giá trị đầu tiên trong danh sách
                            first_type = int(chassis_types_tuple[0])

                            # Định nghĩa các mã cho Laptop và Desktop
                            # Tham khảo: https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-systemenclosure-chassistypes
                            laptop_types = {8, 9, 10, 11, 14, 30, 31, 32} # Portable, Laptop, Notebook, Hand Held, Sub Notebook, Tablet, Convertible, Detachable
                            desktop_types = {3, 4, 5, 6, 7, 13, 15, 23} # Desktop, Low Profile, Pizza Box, Mini Tower, Tower, All in One, Space-Saving, Sealed-Case PC

                            if first_type in laptop_types:
                                system_details_pc_data["Loại máy"] = MACHINE_TYPE_LAPTOP
                                logging.info(f"Xác định loại máy: Laptop (ChassisType: {first_type})")
                            elif first_type in desktop_types:
                                system_details_pc_data["Loại máy"] = MACHINE_TYPE_DESKTOP
                                logging.info(f"Xác định loại máy: PC (ChassisType: {first_type})") # Changed log message slightly
                            else:
                                system_details_pc_data["Loại máy"] = f"{MACHINE_TYPE_UNKNOWN} (Mã: {first_type})"
                                logging.info(f"Mã ChassisType không xác định: {first_type}")
                                # Không thêm vào error_messages vì đã lấy được mã, chỉ là không phân loại được
                        except (ValueError, TypeError) as type_e:
                             logging.warning(f"Giá trị ChassisType không hợp lệ: {chassis_types_tuple[0]} - {type_e}")
                             system_details_pc_data["Loại máy"] = f"{ERROR_FETCHING_INFO} Loại máy (giá trị không hợp lệ)"
                             if "Loại máy" not in error_messages: error_messages.append("Loại máy (giá trị không hợp lệ)")
                    else:
                        logging.warning("Thuộc tính ChassisTypes không tồn tại hoặc rỗng trong Win32_SystemEnclosure.")
                        # Giữ giá trị mặc định NOT_IDENTIFIED
                        if "Loại máy" not in error_messages: error_messages.append("Loại máy (thiếu ChassisTypes)")
                else:
                    logging.warning("Truy vấn Win32_SystemEnclosure không trả về kết quả.")
                    # Giữ giá trị mặc định NOT_IDENTIFIED
                    if "Loại máy" not in error_messages: error_messages.append("Loại máy (không có SystemEnclosure)")

            except (pywintypes.com_error, Exception) as e:
                logging.error(f"Lỗi khi lấy thông tin loại máy (Win32_SystemEnclosure): {e}")
                system_details_pc_data["Loại máy"] = f"{ERROR_FETCHING_INFO} Loại máy"
                if "Loại máy" not in error_messages: error_messages.append("Loại máy (lỗi WMI)")
        else:
            # WMI không khả dụng, không thể xác định loại máy bằng phương pháp này
            logging.warning("WMI không khả dụng, không thể xác định loại máy.")
            # Giữ giá trị mặc định NOT_IDENTIFIED
            if "Loại máy" not in error_messages: error_messages.append("Loại máy (thiếu WMI)")
        # --- Kết thúc phần thêm mới ---

        # --- OS Info ---
        os_name = NOT_IDENTIFIED
        if wmi_service:
            try:
                os_info_list = wmi_service.ExecQuery("SELECT Caption FROM Win32_OperatingSystem")
                if os_info_list: os_name = _get_wmi_property(list(os_info_list)[0], "Caption", NOT_IDENTIFIED)
            except (pywintypes.com_error, Exception) as e: logging.warning(f"Lỗi lấy OS Caption từ WMI, thử platform: {e}")
        if os_name in [NOT_IDENTIFIED, NOT_AVAILABLE]:
             try: os_name = f"{platform.system()} {platform.release()}"
             except Exception as e:
                 logging.error(f"Lỗi lấy OS từ platform: {e}")
                 os_name = f"{ERROR_FETCHING_INFO} Hệ điều hành"
                 error_messages.append("Hệ điều hành (platform)")
        system_details_pc_data["Hệ điều hành"] = os_name # Key tiếng Việt

        try: system_details_pc_data["Phiên bản Windows"] = platform.version() # Key tiếng Việt
        except Exception as e:
            logging.error(f"Lỗi lấy Phiên bản Windows: {e}")
            system_details_pc_data["Phiên bản Windows"] = ERROR_FETCHING_INFO
            error_messages.append("Phiên bản Windows")

        # --- CPU (Gọi hàm đã sửa, truyền wmi_service) ---
        cpu_model_info = get_cpu_info(wmi_service)
        cores = NOT_AVAILABLE
        threads = NOT_AVAILABLE
        try:
            cores = psutil.cpu_count(logical=False) or NOT_AVAILABLE
            threads = psutil.cpu_count(logical=True) or NOT_AVAILABLE
        except Exception as e:
            logging.error(f"Lỗi lấy số Lõi/Luồng: {e}")
            error_messages.append("CPU Lõi/Luồng")

        system_details_pc_data["CPU"] = {
            "Kiểu máy": cpu_model_info, # Key tiếng Việt
            "Số lõi": cores,          # Key tiếng Việt
            "Số luồng": threads        # Key tiếng Việt
        }
        # Kiểm tra lỗi dựa trên kết quả trả về từ get_cpu_info
        # Check if ERROR_FETCHING_INFO is a substring
        if ERROR_FETCHING_INFO in str(cpu_model_info) or cpu_model_info == NOT_IDENTIFIED:
             error_messages.append("CPU Kiểu máy")

        # --- RAM ---
        try:
            ram = psutil.virtual_memory()
            total_ram_gb = round(ram.total / (1024 ** 3), 1)
            system_details_pc_data["Bộ nhớ RAM"] = f"{total_ram_gb} GB" # Key tiếng Việt
        except Exception as e:
            logging.error(f"Lỗi lấy thông tin RAM: {e}")
            system_details_pc_data["Bộ nhớ RAM"] = f"{ERROR_FETCHING_INFO} RAM"
            error_messages.append("RAM")

        # --- MAC Address ---
        try:
            best_mac = NOT_AVAILABLE
            interfaces = psutil.net_if_addrs()
            # Ưu tiên các interface có dây hoặc không dây đang hoạt động
            active_interfaces = []
            stats = psutil.net_if_stats()
            for name, snicaddr_list in interfaces.items():
                # Check if stats exist for the interface before accessing isup
                if name in stats and stats[name].isup:
                    for snicaddr in snicaddr_list:
                        if snicaddr.family == psutil.AF_LINK:
                            mac = snicaddr.address.upper().replace("-", ":")
                            # Check for valid MAC format (more robustly if needed)
                            if mac != "00:00:00:00:00:00" and len(mac) == 17:
                                # Prioritize Ethernet over Wi-Fi if both are active
                                if "ethernet" in name.lower() or "eth" in name.lower():
                                    active_interfaces.insert(0, mac) # Push to front
                                elif "wi-fi" in name.lower() or "wlan" in name.lower():
                                    active_interfaces.append(mac) # Add to end
                                else:
                                     active_interfaces.append(mac) # Other types
            if active_interfaces:
                best_mac = active_interfaces[0] # Get the highest priority MAC

            # Fallback using uuid.getnode() if psutil fails or finds no active interfaces
            if best_mac == NOT_AVAILABLE:
                 mac_num = uuid.getnode()
                 # Format MAC address correctly from getnode() result
                 mac_address = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
                 if mac_address != "00:00:00:00:00:00": best_mac = mac_address

            system_details_pc_data["Địa chỉ MAC"] = best_mac # Key tiếng Việt
            if best_mac == NOT_AVAILABLE: error_messages.append("Địa chỉ MAC (không tìm thấy)")

        except Exception as e:
            logging.error(f"Lỗi khi lấy địa chỉ MAC: {e}")
            system_details_pc_data["Địa chỉ MAC"] = f"{ERROR_FETCHING_INFO} MAC"
            error_messages.append("Địa chỉ MAC")

        # --- IP Address ---
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname) # Often returns the primary IP

            # Check if the IP is loopback, try to find a better one
            if ip_address.startswith("127."):
                 non_loopback_ip = None
                 try:
                     # Get all non-loopback IPv4 addresses from active interfaces
                     all_ips = [addr.address for intf, addrs in psutil.net_if_addrs().items()
                                for addr in addrs if addr.family == socket.AF_INET and not addr.address.startswith("127.")
                                and intf in psutil.net_if_stats() and psutil.net_if_stats()[intf].isup]
                     if all_ips:
                         non_loopback_ip = all_ips[0] # Take the first one found
                 except Exception as ip_e:
                     logging.warning(f"Không tìm được IP non-loopback qua psutil: {ip_e}")

                 # If still loopback or psutil failed, try connecting externally (last resort)
                 if not non_loopback_ip:
                     try:
                         # Connect to a known external address (doesn't send data)
                         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                             s.settimeout(1)
                             s.connect(("8.8.8.8", 80)) # Google DNS
                             non_loopback_ip = s.getsockname()[0]
                     except Exception:
                         pass # Ignore errors if external connection fails

                 if non_loopback_ip:
                     ip_address = non_loopback_ip # Use the found non-loopback IP

            system_details_pc_data["Địa chỉ IP"] = ip_address # Key tiếng Việt
        except socket.gaierror:
             system_details_pc_data["Địa chỉ IP"] = "Không thể phân giải hostname"
             error_messages.append("Địa chỉ IP (hostname resolution)")
        except Exception as e:
            logging.error(f"Lỗi khi lấy địa chỉ IP: {e}")
            system_details_pc_data["Địa chỉ IP"] = f"{ERROR_FETCHING_INFO} IP"
            error_messages.append("Địa chỉ IP")

        # --- Thông tin cần WMI ---
        if wmi_service:
            mainboard_info = get_mainboard_info(wmi_service)
            disk_details = get_disk_drive_details(wmi_service) # Corrected function name
            gpu_details = get_gpu_details(wmi_service)
            screen_details_list = get_screen_details(wmi_service)

            system_details_pc_data["Mainboard"] = mainboard_info # Key tiếng Việt
            system_details_pc_data["Ổ đĩa"] = disk_details      # Key tiếng Việt
            system_details_pc_data["Card đồ họa (GPU)"] = gpu_details # Key tiếng Việt
            system_details_screen_data = screen_details_list

            # Check for specific errors from WMI sub-functions (using "Lỗi" key)
            # Check if the result is a dict/list and contains the error key, excluding connection errors handled below
            if isinstance(mainboard_info, dict) and mainboard_info.get("Lỗi") and mainboard_info.get("Lỗi") != ERROR_WMI_CONNECTION:
                error_messages.append("Mainboard")
            if isinstance(disk_details, list) and disk_details and isinstance(disk_details[0], dict) and disk_details[0].get("Lỗi") and disk_details[0].get("Lỗi") != ERROR_WMI_CONNECTION: # <--- Hoặc đây cũng gây lỗi NameError nếu dòng gán ở trên thiếu
                 error_messages.append("Ổ đĩa")
            if isinstance(gpu_details, list) and gpu_details and isinstance(gpu_details[0], dict) and gpu_details[0].get("Lỗi") and gpu_details[0].get("Lỗi") != ERROR_WMI_CONNECTION:
                 error_messages.append("Card đồ họa (GPU)")
            if isinstance(screen_details_list, list) and screen_details_list and isinstance(screen_details_list[0], dict) and screen_details_list[0].get("Lỗi") and screen_details_list[0].get("Lỗi") != ERROR_WMI_CONNECTION:
                 error_messages.append("Màn hình")
        else:
            # If WMI connection failed, mark dependent sections with error
            wmi_error_msg = f"WMI ({ERROR_WMI_CONNECTION})"
            if wmi_error_msg not in error_messages: # Avoid duplicate WMI errors
                 error_messages.append(wmi_error_msg)
            system_details_pc_data["Mainboard"] = {"Lỗi": ERROR_WMI_CONNECTION}
            system_details_pc_data["Ổ đĩa"] = [{"Lỗi": ERROR_WMI_CONNECTION}]
            system_details_pc_data["Card đồ họa (GPU)"] = [{"Lỗi": ERROR_WMI_CONNECTION}]
            system_details_screen_data = [{"Lỗi": ERROR_WMI_CONNECTION}]
            # Ensure Machine Type also reflects WMI error if it relied on it (already handled above)

        # --- PC Check Utilities (for the separate menu/section) ---
        system_check_utilities_data = {}
        system_check_utilities_data["Thời gian hoạt động"] = get_system_uptime()
        system_check_utilities_data["Dung lượng ổ đĩa"] = get_disk_partitions_usage(wmi_service) # Logical partitions
        system_check_utilities_data["Tóm tắt Event Log gần đây"] = get_recent_event_log_summary(wmi_service) # Renamed key for clarity
        system_check_utilities_data["Nhiệt độ hệ thống"] = get_system_temperatures(wmi_service) # Pass wmi_service
        system_check_utilities_data["Tình trạng ổ cứng (S.M.A.R.T.)"] = get_disk_health_status(wmi_service)
        system_check_utilities_data["Chi tiết Pin (Laptop)"] = get_battery_details(wmi_service)

        # --- Đóng gói kết quả ---
        result = {
            "SystemInformation": {
                "PC": system_details_pc_data,
                "Màn hình": system_details_screen_data # Key tiếng Việt
            },
            "SystemCheckUtilities": system_check_utilities_data
        }

        # Consolidate and remove duplicate error messages
        unique_error_messages = sorted(list(set(error_messages)))
        if unique_error_messages:
            # Key tiếng Việt
            result["Lỗi gặp phải"] = f"Không thể lấy thông tin cho: {', '.join(unique_error_messages)}" # Remains top-level
            logging.warning(f"Các lỗi gặp phải khi thu thập thông tin: {', '.join(unique_error_messages)}")

        return result

    except Exception as e:
        # Catch-all for unexpected errors during info gathering
        logging.critical(f"Lỗi tổng quát nghiêm trọng khi thu thập thông tin PC: {e}", exc_info=True)
        # Return a consistent error structure
        return {
            "SystemInformation": {
                "PC": {"Lỗi": f"Lỗi tổng quát: {e}"},
                "Màn hình": [{"Lỗi": f"Lỗi tổng quát: {e}"}]
            },
            "SystemCheckUtilities": {"Lỗi": f"Lỗi tổng quát khi lấy tiện ích kiểm tra cơ bản: {e}"},
            "Lỗi gặp phải": f"Lỗi nghiêm trọng khi chạy get_pc_info: {e}"
        }
    finally:
        # Ensure COM is uninitialized if it was initialized in _connect_wmi
        if com_initialized:
            try:
                win32com.client.pythoncom.CoUninitialize()
                logging.info("Đã giải phóng COM.")
            except Exception as com_e:
                 logging.error(f"Lỗi khi giải phóng COM: {com_e}")

# --- Helper function to check for admin rights ---
def is_admin():
    """Kiểm tra xem script có đang chạy với quyền admin không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- Helper function to find MpCmdRun.exe ---
def _find_mpcmdrun_path():
    """Finds the path to MpCmdRun.exe, trying multiple common locations."""
    # Path 1: ProgramData (most reliable for MpCmdRun.exe's platform updates)
    platform_base = r"C:\ProgramData\Microsoft\Windows Defender\Platform"
    if os.path.exists(platform_base):
        versions = [d for d in os.listdir(platform_base) if os.path.isdir(os.path.join(platform_base, d)) and not d.lower().startswith("settings")]
        if versions:
            try:
                # Attempt robust version sorting if 'packaging' is available
                from packaging.version import parse as parse_version
                versions.sort(key=parse_version, reverse=True)
                latest_version = versions[0]
            except ImportError:
                latest_version = sorted(versions, reverse=True)[0] # Fallback to lexicographical sort (descending)
            
            path = os.path.join(platform_base, latest_version, "MpCmdRun.exe")
            if os.path.exists(path):
                logging.debug(f"Found MpCmdRun.exe at: {path}")
                return path

    # Path 2: Program Files (fallback)
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    path_pf = os.path.join(program_files, "Windows Defender", "MpCmdRun.exe")
    if os.path.exists(path_pf):
        logging.debug(f"Found MpCmdRun.exe at: {path_pf}")
        return path_pf
        
    logging.warning("MpCmdRun.exe not found in common locations. Assuming it's in PATH.")
    return "MpCmdRun.exe" # Assume it's in PATH as a last resort


# --- Menu 2: TIỆN ÍCH (UTILITIES) - Additional Functions ---

def run_windows_defender_scan(scan_type="QuickScan"):
    """
    Kích hoạt Windows Defender quét virus.
    scan_type có thể là "QuickScan", "FullScan", hoặc "CustomScan" (cần thêm path).
    Yêu cầu quyền Admin.
    Trả về dict với status và message.
    """
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để chạy quét virus."}
    try:
        defender_path = _find_mpcmdrun_path()

        command = [defender_path, "-Scan", f"-ScanType", "1" if scan_type == "QuickScan" else "2"] # 1 for Quick, 2 for Full
        if scan_type == "CustomScan": # Placeholder, custom scan needs path
            return {"status": "error", "message": "CustomScan cần chỉ định đường dẫn (chưa hỗ trợ)."}

        logging.info(f"Đang chạy lệnh: {' '.join(command)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Không đợi ở đây, GUI nên xử lý việc này không đồng bộ
        return {"status": "success", "message": f"Đã yêu cầu Windows Defender {scan_type}. Theo dõi trong Windows Security."}
    except Exception as e:
        logging.error(f"Lỗi khi chạy Windows Defender scan: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi: {e}"}

def update_windows_defender_definitions():
    """
    Kích hoạt cập nhật định nghĩa virus cho Windows Defender.
    Yêu cầu quyền Admin.
    Trả về dict với status và message.
    """
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để cập nhật định nghĩa virus."}
    try:
        defender_path = _find_mpcmdrun_path()

        command = [defender_path, "-SignatureUpdate"]
        logging.info(f"Đang chạy lệnh: {' '.join(command)}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # Không đợi
        return {"status": "success", "message": "Đã yêu cầu cập nhật định nghĩa virus. Theo dõi trong Windows Security."}
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật định nghĩa Windows Defender: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi: {e}"}

def _get_registry_value(key, subkey_name, value_name):
    """Helper để đọc một giá trị từ Registry một cách an toàn."""
    try:
        with winreg.OpenKey(key, subkey_name) as subkey:
            value, _ = winreg.QueryValueEx(subkey, value_name)
            return str(value).strip() if value is not None else None
    except FileNotFoundError:
        return None # Subkey hoặc value không tồn tại
    except OSError as e: # Bắt các lỗi OS khác, ví dụ như không có quyền
        logging.debug(f"Lỗi OS khi đọc registry value '{value_name}' từ '{subkey_name}': {e}")
        return None
    except Exception as e:
        logging.warning(f"Lỗi không xác định khi đọc registry value '{value_name}' từ '{subkey_name}': {e}")
        return None

def _get_installed_software_from_registry(hive, key_path, flags=0):
    """
    Đọc thông tin phần mềm đã cài đặt từ một nhánh Registry cụ thể.
    flags: ví dụ winreg.KEY_WOW64_32KEY cho view 32-bit trên OS 64-bit.
    """
    software_list = []
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | flags) as reg_key:
            for i in range(winreg.QueryInfoKey(reg_key)[0]): # Lặp qua các subkeys
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    app_key_path = os.path.join(key_path, subkey_name) # type: ignore
                    
                    display_name = _get_registry_value(hive, app_key_path, "DisplayName")
                    display_version = _get_registry_value(hive, app_key_path, "DisplayVersion")
                    publisher = _get_registry_value(hive, app_key_path, "Publisher")
                    install_source = _get_registry_value(hive, app_key_path, "InstallSource")
                    url_info = _get_registry_value(hive, app_key_path, "URLInfoAbout")
                    system_component = _get_registry_value(hive, app_key_path, "SystemComponent")

                    if display_name and not (system_component == "1" and "Update" in display_name): # Bỏ qua system components và updates
                        source_info = "Registry"
                        if install_source:
                            source_info = f"Nguồn cài đặt: {install_source[:50]}{'...' if len(install_source) > 50 else ''}"
                        elif url_info:
                            source_info = f"Web: {url_info[:50]}{'...' if len(url_info) > 50 else ''}"
                        
                        software_list.append({
                            "Tên": display_name,
                            "Phiên bản": display_version or NOT_IDENTIFIED,
                            "Nhà sản xuất": publisher or NOT_IDENTIFIED,
                            "Nguồn": source_info
                        })
                except OSError: # Lỗi khi EnumKey hoặc OpenKey subkey
                    continue # Bỏ qua subkey này
    except FileNotFoundError:
        logging.debug(f"Registry path không tìm thấy: {key_path}")
    except Exception as e:
        logging.error(f"Lỗi khi đọc software từ Registry path '{key_path}': {e}", exc_info=True)
    return software_list

def get_installed_software_versions(wmi_service=None):
    """Lấy danh sách phần mềm đã cài đặt và phiên bản của chúng (qua Registry và winget)."""
    software_list = []
    processed_names = set() # Để tránh trùng lặp từ các nguồn khác nhau

    # --- Đọc từ Registry ---
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    # Trên hệ thống 64-bit, cũng kiểm tra view 32-bit của HKLM
    if platform.machine().endswith('64'):
        registry_paths.append((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"))
    for hive, path in registry_paths:
        # Simplified flags: OS handles redirection for explicit WOW6432Node paths. Default access is sufficient.
        apps_from_reg = _get_installed_software_from_registry(hive, path, flags=0)
        for app in apps_from_reg:
            if app["Tên"] not in processed_names:
                software_list.append(app)
                processed_names.add(app["Tên"])
    logging.info(f"Đã lấy {len(software_list)} ứng dụng từ Registry.")

    # --- Bổ sung/Cập nhật từ winget list ---
    try:
        process = subprocess.run(["winget", "list"], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode == 0:
            lines = process.stdout.strip().splitlines()
            if len(lines) > 2: # Header lines
                for line in lines[2:]: # Skip headers
                    parts = [p.strip() for p in line.split("  ") if p.strip()] # Split by multiple spaces
                    if len(parts) >= 3: # Name, Id, Version. Source is often the last part.
                        name = parts[0]
                        version = parts[2] if len(parts) >2 else NOT_IDENTIFIED
                        winget_source = parts[-1] if len(parts) > 3 and parts[-1].lower() in ["winget", "msstore"] else "winget"
                        
                        # Cập nhật nếu đã có từ Registry, hoặc thêm mới
                        existing_app = next((app for app in software_list if app["Tên"] == name), None)
                        if existing_app:
                            existing_app["Nguồn"] = f"Winget ({winget_source})" # Ưu tiên nguồn từ winget
                            if version != NOT_IDENTIFIED: existing_app["Phiên bản"] = version # Cập nhật phiên bản nếu winget có
                        elif name not in processed_names: # Thêm mới nếu chưa có
                            software_list.append({"Tên": name, "Phiên bản": version, "Nhà sản xuất": NOT_IDENTIFIED, "Nguồn": f"Winget ({winget_source})"})
                            processed_names.add(name)
                logging.info("Đã bổ sung/cập nhật danh sách phần mềm từ winget.")
        else:
            logging.warning(f"Lệnh 'winget list' thất bại hoặc không khả dụng. Code: {process.returncode}, Lỗi: {process.stderr}")
    except FileNotFoundError:
        logging.warning("'winget' không được tìm thấy. Không thể lấy danh sách phần mềm qua winget.")
    except (subprocess.TimeoutExpired, Exception) as e:
        logging.error(f"Lỗi khi chạy 'winget list': {e}", exc_info=True)

    if not software_list:
        return [{"Lỗi": "Không thể lấy danh sách phần mềm từ Registry hoặc winget."}]
    return sorted(software_list, key=lambda x: x['Tên'])

def check_windows_activation_status():
    """Kiểm tra trạng thái kích hoạt Windows."""
    try:
        process = subprocess.run(["cscript", "//Nologo", os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "slmgr.vbs"), "/dlv"],
                                 capture_output=True, text=True, encoding='oem', errors='ignore', timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode == 0:
            output = process.stdout
            if "License Status: Licensed" in output or "Trạng thái Giấy phép: Đã cấp phép" in output: # Check for Vietnamese too
                return {"status": "success", "message": "Windows đã được kích hoạt.", "details": output}
            elif "Error" in output or "Lỗi" in output: # Check for specific error codes if needed
                return {"status": "error", "message": "Windows chưa được kích hoạt hoặc có lỗi.", "details": output}
            else: # Partial info or unknown status
                return {"status": "warning", "message": "Không thể xác định rõ trạng thái kích hoạt Windows.", "details": output}
        else:
            return {"status": "error", "message": f"Lỗi khi chạy slmgr.vbs: {process.stderr}", "details": process.stderr}
    except Exception as e:
        logging.error(f"Lỗi kiểm tra kích hoạt Windows: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi: {e}"}

def check_office_activation_status():
    """Kiểm tra trạng thái kích hoạt Microsoft Office."""
    # Path to ospp.vbs varies by Office version (Office14, Office15, Office16)
    # Common paths:
    office_paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Microsoft Office", "Office16", "OSPP.VBS"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Microsoft Office", "Office16", "OSPP.VBS"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Microsoft Office", "Office15", "OSPP.VBS"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Microsoft Office", "Office15", "OSPP.VBS"),
    ]
    ospp_script_path = None
    for p in office_paths:
        if os.path.exists(p):
            ospp_script_path = p
            break
    if not ospp_script_path:
        return {"status": "info", "message": "Không tìm thấy script OSPP.VBS. Không thể kiểm tra Office cũ. (Office 365/M365 dùng cơ chế khác)."}

    try:
        process = subprocess.run(["cscript", "//Nologo", ospp_script_path, "/dstatus"],
                                 capture_output=True, text=True, encoding='oem', errors='ignore', timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode == 0:
            output = process.stdout
            if "LICENSE STATUS:  ---LICENSED---" in output:
                return {"status": "success", "message": "Microsoft Office (phiên bản cũ) đã được kích hoạt.", "details": output}
            elif "LICENSE STATUS" in output: # Contains status but might not be fully licensed
                return {"status": "warning", "message": "Trạng thái kích hoạt Office (phiên bản cũ) không rõ hoặc chưa kích hoạt.", "details": output}
            else: # No clear status found
                 return {"status": "info", "message": "Không tìm thấy thông tin kích hoạt Office (phiên bản cũ).", "details": output}
        else:
            return {"status": "error", "message": f"Lỗi khi chạy OSPP.VBS: {process.stderr}", "details": process.stderr}
    except Exception as e:
        logging.error(f"Lỗi kiểm tra kích hoạt Office: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi: {e}"}

def generate_battery_report():
    """Tạo và tùy chọn mở báo cáo tình trạng pin (cho laptop)."""
    report_path = os.path.join(os.path.expanduser("~"), "battery_report.html")
    try:
        # powercfg requires admin to run from some contexts, but often works for /batteryreport without it.
        process = subprocess.run(["powercfg", "/batteryreport", "/output", report_path, "/duration", "1"],
                                 capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode == 0 and os.path.exists(report_path):
            # os.startfile(report_path) # GUI should handle opening the file
            return {"status": "success", "message": f"Báo cáo pin đã được tạo tại: {report_path}. Vui lòng mở file này để xem.", "path": report_path}
        else:
            error_details = process.stderr or process.stdout or "Không có thông tin lỗi cụ thể."
            logging.error(f"Lỗi khi tạo báo cáo pin: {error_details}")
            return {"status": "error", "message": f"Không thể tạo báo cáo pin. Lỗi: {error_details}"}
    except Exception as e:
        logging.error(f"Lỗi nghiêm trọng khi tạo báo cáo pin: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi: {e}"}

def get_recent_event_logs(wmi_service, hours_ago=24, max_events_per_log=25):
    """
    Lấy danh sách chi tiết các lỗi (Error) và cảnh báo (Warning) gần đây từ System và Application event logs.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể truy cập Event Logs."}]

    all_events_collected = []
    try:
        from datetime import timezone as dt_timezone # Import timezone
        threshold_utc_dt = datetime.now(dt_timezone.utc) - timedelta(hours=hours_ago)
        event_type_map_display = {1: "Lỗi", 2: "Cảnh báo"}

        for logfile_name in ["System", "Application"]:
            # Modified Query: Remove TimeGenerated filter and ORDER BY from WQL
            query = (f"SELECT Logfile, SourceName, EventType, TimeGenerated, Message FROM Win32_NTLogEvent "
                     f"WHERE Logfile = '{logfile_name}' AND (EventType = 1 OR EventType = 2)")
            
            raw_events = wmi_service.ExecQuery(query)
            
            for event in raw_events:
                time_generated_str = _get_wmi_property(event, "TimeGenerated", None)
                event_time_pywintypes = None
                if time_generated_str:
                    try:
                        # Extract the main datetime part (YYYYMMDDHHMMSS)
                        if '.' in time_generated_str:
                            parsable_time_str_detail = time_generated_str.split('.')[0]
                        else:
                            parsable_time_str_detail = time_generated_str[:14]
                        
                        # Assume WMI time is UTC, make the datetime object UTC-aware
                        dt_object_for_pywintypes_detail = datetime.strptime(parsable_time_str_detail, "%Y%m%d%H%M%S").replace(tzinfo=dt_timezone.utc)
                        event_time_pywintypes = pywintypes.Time(dt_object_for_pywintypes_detail) # type: ignore
                        
                        
                        if event_time_pywintypes < threshold_utc_dt:
                            continue # Skip if older than threshold
                    except (pywintypes.error, ValueError) as e_time: # type: ignore
                        logging.warning(f"Không thể phân tích TimeGenerated '{time_generated_str}' cho log {logfile_name}: {e_time}")
                        # Continue processing event but time might be displayed as raw string

                event_type_code = _get_wmi_property(event, "EventType", 0)
                time_display = NOT_AVAILABLE
                if event_time_pywintypes: # If successfully parsed and within range
                    try:
                        # Format to a more readable local time string (or keep UTC if preferred)
                        # For simplicity, using strftime; for true local time, convert timezone
                        time_display = event_time_pywintypes.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception: # Fallback if strftime fails on pywintypes.datetime
                        time_display = str(event_time_pywintypes)
                elif time_generated_str: # If parsing failed but string exists
                    time_display = time_generated_str

                all_events_collected.append({
                    "Log": _get_wmi_property(event, "Logfile", logfile_name),
                    "Nguồn": _get_wmi_property(event, "SourceName", NOT_IDENTIFIED),
                    "Loại": event_type_map_display.get(event_type_code, "Không xác định"),
                    "Thời gianObj": event_time_pywintypes, # Store for sorting
                    "Thời gian": time_display, # For display
                    "Thông điệp": _get_wmi_property(event, "Message", NOT_AVAILABLE)[:200] + "..."
                })

        # Sort events in Python by time (descending)
        # Filter out events where TimeObj is None (due to parsing error) before sorting if necessary
        sorted_events = sorted(
            [e for e in all_events_collected if e["Thời gianObj"] is not None],
            key=lambda x: x["Thời gianObj"],
            reverse=True
        )

        # Limit to max_events_per_log (overall, not per log file as before)
        # Or, if you want per log, the limiting logic needs to be inside the logfile_name loop
        # For now, this is an overall limit after collecting from all specified logs.
        final_event_list = []
        for event_data in sorted_events[:max_events_per_log]:
            del event_data["Thời gianObj"] # Remove helper object before returning
            final_event_list.append(event_data)

        if not final_event_list:
            # Check if all_events_collected was also empty (meaning no events at all in timeframe)
            # or if parsing failed for all.
            # This message might need adjustment based on why final_event_list is empty.
            if not any(e["Thời gianObj"] for e in all_events_collected if "Thời gianObj" in e): # Check if any event had valid time
                 return [{"Thông tin": f"Không có lỗi/cảnh báo nào trong System/Application logs ({hours_ago} giờ qua) hoặc không thể phân tích thời gian sự kiện."}]
            return [{"Thông tin": f"Không có lỗi hoặc cảnh báo nào được tìm thấy trong System/Application logs ({hours_ago} giờ qua)."}]
        return final_event_list

    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.error(f"Lỗi khi lấy chi tiết Event Log: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} Event Logs: {str(e)}"}]

# --- Old code for get_recent_event_logs, for reference during merge/review ---
    # event_list = []
    # try:
    #     threshold_utc_dt = datetime.utcnow() - timedelta(hours=hours_ago)
    #     wmi_time_filter = get_wmi_utc_datetime_str(threshold_utc_dt)
    #     event_type_map_display = {1: "Lỗi", 2: "Cảnh báo"}

    #     for logfile_name in ["System", "Application"]:
    #         query = (f"SELECT Logfile, SourceName, EventType, TimeGenerated, Message FROM Win32_NTLogEvent "
    #                  f"WHERE Logfile = '{logfile_name}' AND (EventType = 1 OR EventType = 2) "
    #                  f"AND TimeGenerated >= '{wmi_time_filter}' ORDER BY TimeGenerated DESC")
            
    #         events_retrieved_count = 0
    #         # WMI ExecQuery might not directly support TOP or LIMIT, so we limit after fetching
    #         raw_events = wmi_service.ExecQuery(query)
            
    #         for event in raw_events:
    #             if events_retrieved_count >= max_events_per_log:
    #                 break # Reached max for this log file

    #             event_type_code = _get_wmi_property(event, "EventType", 0)
    #             time_generated_wmi = _get_wmi_property(event, "TimeGenerated", None) # DMTF format
                
    #             # Convert WMI DMTF datetime to Python datetime object then to readable string
    #             # Example DMTF: 20230715103000.000000+420 (offset in minutes)
    #             # We need to parse it carefully. For simplicity, we'll assume UTC from WMI if no offset or handle basic cases.
    #             # A more robust parser would be needed for all DMTF variations.
    #             # For now, let's try a simpler approach if TimeGenerated is already somewhat formatted by WMI.
    #             # If it's a string like '20230715103000.xxxxxx+-xxx'
    #             time_display = NOT_AVAILABLE
    #             if time_generated_wmi and isinstance(time_generated_wmi, str) and len(time_generated_wmi) >=14 :
    #                 try:
    #                     # Basic parsing of YYYYMMDDHHMMSS part
    #                     dt_obj = datetime.strptime(time_generated_wmi[:14], "%Y%m%d%H%M%S")
    #                     time_display = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    #                 except ValueError:
    #                     time_display = time_generated_wmi # Fallback to raw if parsing fails

    #             event_list.append({
    #                 "Log": _get_wmi_property(event, "Logfile", logfile_name),
    #                 "Nguồn": _get_wmi_property(event, "SourceName", NOT_IDENTIFIED),
    #                 "Loại": event_type_map_display.get(event_type_code, "Không xác định"),
    #                 "Thời gian": time_display,
    #                 "Thông điệp": _get_wmi_property(event, "Message", NOT_AVAILABLE)[:200] + "..." # Truncate long messages
    #             })
    #             events_retrieved_count += 1
            
    #         if events_retrieved_count == 0 and not raw_events: # Check if query itself returned nothing
    #              event_list.append({"Thông tin": f"Không có lỗi/cảnh báo nào trong {logfile_name} log ({hours_ago} giờ qua)."})

    #     if not event_list:
    #         return [{"Thông tin": f"Không có lỗi hoặc cảnh báo nào được tìm thấy trong System/Application logs ({hours_ago} giờ qua)."}]
    #     return event_list
    # except (pywintypes.com_error, Exception) as e: # type: ignore
    #     logging.error(f"Lỗi khi lấy chi tiết Event Log: {e}", exc_info=True)
    #     return [{"Lỗi": f"{ERROR_FETCHING_INFO} Event Logs: {str(e)}"}]

def get_wifi_connection_info(wmi_service=None): # wmi_service can be optional if using netsh
    """Lấy thông tin về kết nối Wi-Fi hiện tại."""
    try:
        # Using netsh is often more straightforward for Wi-Fi details
        process = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        if process.returncode == 0:
            output = process.stdout
            wifi_details = {}
            current_interface_details = {}
            interface_count = output.count("Name") # Count occurrences of "Name" to detect interfaces

            if interface_count == 0:
                return {"Thông tin": "Không tìm thấy card Wi-Fi nào."}
            
            lines = output.splitlines()
            for line in lines:
                if not line.strip(): continue
                if "Name" in line: # Start of a new interface block
                    if current_interface_details: # Save previous interface if exists
                        wifi_details[current_interface_details.get("Tên Card", "Unknown Interface")] = current_interface_details
                    current_interface_details = {}
                    current_interface_details["Tên Card"] = line.split(":",1)[1].strip()
                elif "SSID" in line and "BSSID" not in line: current_interface_details["SSID"] = line.split(":",1)[1].strip()
                elif "BSSID" in line: current_interface_details["BSSID"] = line.split(":",1)[1].strip()
                elif "Signal" in line: current_interface_details["Tín hiệu"] = line.split(":",1)[1].strip()
                elif "Radio type" in line: current_interface_details["Loại Radio"] = line.split(":",1)[1].strip()
                elif "Authentication" in line: current_interface_details["Xác thực"] = line.split(":",1)[1].strip()
                elif "Cipher" in line: current_interface_details["Mã hóa"] = line.split(":",1)[1].strip()
                elif "State" in line: current_interface_details["Trạng thái Kết nối"] = line.split(":",1)[1].strip()
            
            if current_interface_details: # Save the last interface
                 wifi_details[current_interface_details.get("Tên Card", "Unknown Interface")] = current_interface_details

            if not wifi_details:
                return {"Thông tin": "Không có kết nối Wi-Fi nào đang hoạt động hoặc không lấy được thông tin."}
            return wifi_details # Returns a dict of dicts, GUI can format this
        else:
            return {"Lỗi": f"Lệnh 'netsh wlan show interfaces' thất bại. Code: {process.returncode}", "Chi tiết": process.stderr}
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin Wi-Fi: {e}", exc_info=True)
        return {"Lỗi": f"{ERROR_FETCHING_INFO} Wi-Fi: {str(e)}"}

def get_system_temperatures(wmi_service=None): # Add wmi_service=None to match calls from WorkerThread
    """
    Cố gắng lấy thông tin nhiệt độ hệ thống qua WMI (MSAcpi_ThermalZoneTemperature).
    Manages its own WMI connection to root\WMI.
    """
    temps = []
    _local_com_init_temp = False
    service_root_wmi_temp = None
    try:
        try:
            win32com.client.pythoncom.CoInitialize()
            _local_com_init_temp = True
        except pywintypes.com_error:
            logging.debug("COM already initialized for get_system_temperatures or different model.")

        wmi_locator_temp = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service_root_wmi_temp = wmi_locator_temp.ConnectServer(".", "root\\WMI")
        logging.info("Successfully connected to WMI namespace root\\WMI for temperature check.")

        if service_root_wmi_temp:
            thermal_zones = service_root_wmi_temp.ExecQuery("SELECT InstanceName, CurrentTemperature FROM MSAcpi_ThermalZoneTemperature")
            for zone in thermal_zones:
                name = _get_wmi_property(zone, "InstanceName", "Vùng không xác định")
                temp_kelvin_tenths = _get_wmi_property(zone, "CurrentTemperature", 0)
                temp_celsius = round(temp_kelvin_tenths / 10 - 273.15, 1) if temp_kelvin_tenths > 0 else NOT_AVAILABLE
                temps.append({"Vùng": name, "Nhiệt độ (°C)": temp_celsius})
            
        if not temps:
            return [{"Thông tin": "Không tìm thấy thông tin nhiệt độ từ MSAcpi_ThermalZoneTemperature. Có thể không được hỗ trợ bởi phần cứng/driver."}]
    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.warning(f"Lỗi khi lấy nhiệt độ hệ thống: {e}", exc_info=True)
        if "Invalid class" in str(e) or "Invalid namespace" in str(e):
            temps = [{"Lỗi": "Không thể truy cập WMI class cho nhiệt độ (MSAcpi_ThermalZoneTemperature). Driver có thể không hỗ trợ."}]
        else:
            temps = [{"Lỗi": f"{ERROR_FETCHING_INFO} nhiệt độ: {str(e)}"}]
    finally:
        if _local_com_init_temp:
            win32com.client.pythoncom.CoUninitialize()
            logging.debug("COM uninitialized for get_system_temperatures.")
    return temps

def get_running_processes(wmi_service=None): # wmi_service is optional as psutil is preferred
    """Lấy danh sách các tiến trình đang chạy sử dụng psutil."""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'cpu_percent', 'status']):
            try:
                mem_rss_mb = round(proc.info['memory_info'].rss / (1024 * 1024), 2) if proc.info['memory_info'] else NOT_AVAILABLE
                processes.append({
                    "PID": proc.info['pid'],
                    "Tên tiến trình": proc.info['name'],
                    "Người dùng": proc.info['username'] if proc.info['username'] else NOT_IDENTIFIED,
                    "Bộ nhớ (MB)": mem_rss_mb,
                    "CPU (%)": proc.info['cpu_percent'] if proc.info['cpu_percent'] is not None else NOT_AVAILABLE,
                    "Trạng thái": proc.info['status'] if proc.info['status'] else NOT_IDENTIFIED
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue # Bỏ qua các tiến trình đã kết thúc hoặc không truy cập được
        if not processes:
            return [{"Thông tin": "Không có tiến trình nào được liệt kê hoặc không thể truy cập."}]
        # Sắp xếp theo tên tiến trình
        return sorted(processes, key=lambda p: str(p.get("Tên tiến trình","")).lower())
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách tiến trình: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} tiến trình: {str(e)}"}]

def open_resource_monitor():
    """Mở Resource Monitor của Windows."""
    try:
        subprocess.Popen("resmon.exe")
        return {"status": "success", "message": "Đang mở Resource Monitor..."}
    except Exception as e:
        logging.error(f"Lỗi khi mở Resource Monitor: {e}", exc_info=True)
        return {"status": "error", "message": f"Không thể mở Resource Monitor: {e}"}

def clear_temporary_files():
    """Xóa các file tạm, prefetch và dọn dẹp thùng rác."""
    results = {"deleted_count": 0, "skipped_count": 0, "errors": [], "admin_rights": is_admin()}

    if not results["admin_rights"]:
        results["errors"].append("Một số file có thể không xóa được do thiếu quyền Administrator.")
        logging.warning("clear_temporary_files: Chạy không có quyền Administrator.")

    # Temp folders
    temp_folders = [os.environ.get('TEMP'), os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')]
    if os.name == 'nt': temp_folders.append(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch'))
    
    for folder in temp_folders:
        if folder and os.path.isdir(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        results["deleted_count"] += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        results["deleted_count"] += 1 # Count folder as one item
                except Exception as e:
                    # Check for common errors like "in use" or "access denied"
                    if isinstance(e, (PermissionError, OSError)) and (e.winerror == 32 or e.winerror == 5):
                        results["skipped_count"] += 1
                        logging.warning(f"Bỏ qua file đang sử dụng hoặc bị từ chối truy cập: {file_path} - {e}")
                    else:
                        results["errors"].append(f"Không thể xóa {file_path}: {e}")
                        logging.warning(f"Không thể xóa {file_path}: {e}")
                        
    # Recycle Bin (requires winshell or similar, or complex native calls - this is a placeholder)
    # For simplicity, this example omits direct recycle bin emptying.
    # Consider using:
    # try:
    #   import winshell
    #   winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    #   results["recycle_bin"] = "Đã dọn dẹp Thùng rác (nếu winshell được cài đặt)."
    # except ImportError:
    #   results["recycle_bin"] = "Thư viện winshell không được cài đặt, không thể dọn Thùng rác tự động."
    # except Exception as e:
    #   results["errors"].append(f"Lỗi dọn Thùng rác: {e}")

    message = f"Đã xóa {results['deleted_count']} mục tạm."
    if results["skipped_count"] > 0:
        message += f" Đã bỏ qua {results['skipped_count']} mục đang sử dụng hoặc bị từ chối truy cập."
    if results["errors"]: # Only count actual unexpected errors here
        message += f" Gặp {len(results['errors'])} lỗi không mong muốn khác."
    
    return {"status": "success" if not results["errors"] and results["skipped_count"] == 0 else "warning", "message": message, "details": {"deleted": results["deleted_count"], "skipped": results["skipped_count"], "errors_list": results["errors"], "admin": results["admin_rights"]}}

def reset_internet_connection():
    """Thực hiện các lệnh để reset cài đặt mạng. Yêu cầu quyền Admin."""
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để reset kết nối Internet."}
    
    commands = [
        ("netsh winsock reset", "Reset Winsock Catalog"),
        ("netsh int ip reset", "Reset IP Configuration"), # Có thể cần file log, nhưng thường không bắt buộc
        ("ipconfig /release", "Release IP Address (có thể gây mất kết nối tạm thời)"),
        ("ipconfig /renew", "Renew IP Address (có thể mất vài giây)"),
        ("ipconfig /flushdns", "Flush DNS Resolver Cache")
    ]
    results = []
    overall_success = True

    for cmd, desc in commands:
        try:
            logging.info(f"Đang chạy: {cmd} ({desc})")
            process = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30, check=False, creationflags=subprocess.CREATE_NO_WINDOW, encoding='oem', errors='ignore')
            if process.returncode == 0:
                results.append(f"Thành công: {desc}")
            else:
                results.append(f"Thất bại (code {process.returncode}): {desc}. Lỗi: {process.stderr.strip() or process.stdout.strip()}")
                overall_success = False
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            results.append(f"Lỗi khi chạy '{desc}': {e}")
            overall_success = False
            logging.error(f"Lỗi khi chạy {cmd}: {e}", exc_info=True)

    final_message = "Quá trình reset kết nối Internet hoàn tất. "
    if not overall_success:
        final_message += "Một số lệnh có thể đã thất bại. "
    final_message += "Bạn có thể cần khởi động lại máy tính để các thay đổi có hiệu lực hoàn toàn."
    
    return {"status": "success" if overall_success else "warning", "message": final_message, "details": "\n".join(results)}

def run_sfc_scan():
    """Chạy System File Checker (sfc /scannow). Yêu cầu quyền Admin."""
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để chạy SFC scan."}
    try:
        logging.info("Đang khởi chạy SFC /scannow...")
        # SFC /scannow cần chạy trong cửa sổ console riêng và không nên bị Popen quản lý chặt chẽ stdout/stderr
        # vì nó có thể tương tác với người dùng hoặc cần quyền đặc biệt.
        # CREATE_NEW_CONSOLE để nó chạy trong cửa sổ riêng (có thể ẩn nếu muốn nhưng khó theo dõi)
        subprocess.Popen(["sfc", "/scannow"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"status": "success", "message": "Đã yêu cầu chạy SFC /scannow. Quá trình này có thể mất nhiều thời gian. Vui lòng theo dõi cửa sổ Command Prompt và kiểm tra kết quả sau khi hoàn tất. Bạn có thể cần khởi động lại máy."}
    except Exception as e:
        logging.error(f"Lỗi khi khởi chạy SFC scan: {e}", exc_info=True)
        return {"status": "error", "message": f"Không thể khởi chạy SFC scan: {e}"}

def update_all_winget_packages():
    """Sử dụng winget để cập nhật tất cả các gói phần mềm. Yêu cầu quyền Admin."""
    if not is_admin(): # Winget upgrade thường cần admin
        return {"status": "error", "message": "Yêu cầu quyền Administrator để cập nhật phần mềm qua winget."}
    try:
        logging.info("Đang chạy winget upgrade --all...")
        # Tương tự SFC, winget upgrade có thể cần cửa sổ riêng hoặc xử lý tương tác
        subprocess.Popen(["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"status": "success", "message": "Đã yêu cầu winget cập nhật tất cả các gói. Quá trình này có thể mất thời gian. Vui lòng theo dõi cửa sổ Command Prompt (nếu xuất hiện) hoặc kiểm tra lại sau."}
    except FileNotFoundError:
        return {"status": "error", "message": "'winget' không được tìm thấy. Vui lòng cài đặt App Installer từ Microsoft Store."}
    except Exception as e:
        logging.error(f"Lỗi khi chạy winget upgrade: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi khi chạy winget upgrade: {e}"}

def get_firewall_status():
    """Kiểm tra trạng thái của Windows Firewall cho các profile (Domain, Private, Public)."""
    profiles = {"Domain", "Private", "Public"} # Sử dụng set để tránh trùng lặp
    status_report = {}
    all_profiles_off = True
    any_profile_error = False

    for profile_name in profiles:
        try:
            # Lệnh netsh advfirewall show {profile_name} state (thay thế {profile_name} bằng DomainProfile, PrivateProfile, PublicProfile)
            # Tuy nhiên, để đơn giản hơn, ta có thể dùng `show allprofiles` và parse
            process = subprocess.run(["netsh", "advfirewall", "show", f"{profile_name.lower()}profile", "state"],
                                     capture_output=True, text=True, encoding='oem', errors='ignore', timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            if process.returncode == 0:
                output = process.stdout.lower() # Chuyển sang chữ thường để dễ so sánh
                if "state on" in output or "trạng thái on" in output : # Kiểm tra cả tiếng Việt
                    status_report[f"Tường lửa ({profile_name})"] = "Đang BẬT"
                    all_profiles_off = False
                elif "state off" in output or "trạng thái off" in output:
                    status_report[f"Tường lửa ({profile_name})"] = "Đang TẮT"
                else:
                    status_report[f"Tường lửa ({profile_name})"] = "Không xác định"
                    any_profile_error = True
            else:
                status_report[f"Tường lửa ({profile_name})"] = f"Lỗi (code {process.returncode})"
                any_profile_error = True
        except Exception as e:
            status_report[f"Tường lửa ({profile_name})"] = f"Lỗi: {e}"
            any_profile_error = True
            logging.error(f"Lỗi khi kiểm tra trạng thái tường lửa cho profile {profile_name}: {e}", exc_info=True)

    overall_status = "Không xác định"
    if not any_profile_error:
        if all_profiles_off:
            overall_status = "Tất cả profile tường lửa đang TẮT."
        else:
            overall_status = "Ít nhất một profile tường lửa đang BẬT."

    return {"status": "info", "message": f"Trạng thái tường lửa: {overall_status}", "details": status_report}

def toggle_firewall(enable=True):
    """Bật hoặc tắt Windows Firewall cho tất cả các profile. Yêu cầu quyền Admin."""
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để thay đổi cài đặt tường lửa."}
    action = "on" if enable else "off"
    profile_types = ["allprofiles"] # Áp dụng cho tất cả các profile
    results = []
    overall_success = True
    for profile in profile_types:
        try:
            command = ["netsh", "advfirewall", "set", profile, "state", action]
            process = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False, creationflags=subprocess.CREATE_NO_WINDOW, encoding='oem', errors='ignore')
            if process.returncode == 0:
                results.append(f"Đã {'BẬT' if enable else 'TẮT'} tường lửa cho profile: {profile}.")
            else:
                results.append(f"Lỗi khi {'bật' if enable else 'tắt'} tường lửa cho {profile} (code {process.returncode}): {process.stderr.strip() or process.stdout.strip()}")
                overall_success = False
        except Exception as e:
            results.append(f"Lỗi nghiêm trọng khi thay đổi tường lửa cho {profile}: {e}")
            overall_success = False
            logging.error(f"Lỗi khi thay đổi tường lửa cho {profile}: {e}", exc_info=True)

    action_text = "bật" if enable else "tắt"
    if overall_success:
        return {"status": "success", "message": f"Đã {'BẬT' if enable else 'TẮT'} Windows Firewall thành công cho tất cả các profile.", "details": "\n".join(results)}
    else:
        return {"status": "error", "message": f"Có lỗi xảy ra khi cố gắng {action_text} Windows Firewall.", "details": "\n".join(results)}

# --- Các hàm mới được thêm (Placeholders) ---
def _get_startup_items_from_registry(hive, key_path, architecture_flag=0):
    """Helper to read startup items from a specific registry key."""
    items = []
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | architecture_flag) as reg_key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(reg_key, i)
                    # Pre-calculate the string for the "Nguồn" field to avoid complex f-string parsing issues
                    # The string 'SOFTWARE\\\\' evaluates to 'SOFTWARE\'
                    split_token = 'SOFTWARE\\\\' 
                    
                    path_segment_for_display = key_path # Default to full key_path
                    if split_token in key_path:
                        # This replicates the original logic: take the part after 'SOFTWARE\'
                        path_segment_for_display = key_path.split(split_token, 1)[1] if len(key_path.split(split_token, 1)) > 1 else ""

                    source_description = f"Registry: {path_segment_for_display}"
                    items.append({"Tên": name, "Lệnh": str(value), "Nguồn": source_description})
                    i += 1
                except OSError: # No more values
                    break
    except FileNotFoundError:
        logging.debug(f"Startup registry key not found: {key_path}")
    except Exception as e:
        logging.warning(f"Error reading startup items from registry {key_path}: {e}")
    return items

def _get_startup_items_from_folder(folder_path, source_name):
    """Helper to read startup items from a specific folder."""
    items = []
    if not os.path.isdir(folder_path):
        logging.debug(f"Startup folder not found: {folder_path}")
        return items
    try:
        for item_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item_name)
            # Lấy target của shortcut nếu là file .lnk
            if item_name.lower().endswith(".lnk"):
                try:
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(full_path)
                    target_path = shortcut.TargetPath
                    arguments = shortcut.Arguments
                    command = f'"{target_path}" {arguments}'.strip()
                except Exception as e_lnk:
                    logging.warning(f"Could not resolve shortcut {full_path}: {e_lnk}")
                    command = full_path # Fallback to lnk path
            else:
                command = full_path
            items.append({"Tên": item_name, "Lệnh": command, "Nguồn": source_name})
    except Exception as e:
        logging.warning(f"Error reading startup items from folder {folder_path}: {e}")
    return items

def get_startup_programs(wmi_service=None):
    """
    Lấy danh sách các chương trình khởi động cùng Windows.
    Bao gồm Registry (Run, RunOnce) và thư mục Startup.
    """
    startup_items = []
    processed_commands = set() # Để tránh trùng lặp lệnh từ các nguồn khác nhau

    # Registry paths
    reg_paths = [
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
    ]
    if platform.machine().endswith('64'): # Check 32-bit view on 64-bit OS for HKLM
        reg_paths.append((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"))
        reg_paths.append((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce"))

    for hive, path in reg_paths:
        items = _get_startup_items_from_registry(hive, path)
        for item in items:
            if item["Lệnh"] not in processed_commands:
                startup_items.append(item)
                processed_commands.add(item["Lệnh"])

    # Startup folders
    user_startup_path = os.path.join(os.environ['APPDATA'], r"Microsoft\Windows\Start Menu\Programs\Startup")
    common_startup_path = os.path.join(os.environ['ALLUSERSPROFILE'], r"Microsoft\Windows\Start Menu\Programs\Startup")

    folder_sources = [
        (user_startup_path, "Thư mục Startup (Người dùng)"),
        (common_startup_path, "Thư mục Startup (Chung)"),
    ]
    for folder_path, source_name in folder_sources:
        items = _get_startup_items_from_folder(folder_path, source_name)
        for item in items:
            # Lọc bớt desktop.ini
            if item["Tên"].lower() == "desktop.ini":
                continue
            # Kiểm tra trùng lặp lệnh một cách đơn giản hơn cho folder items
            # (vì target của shortcut có thể giống nhau dù tên file .lnk khác)
            # Đây là một kiểm tra cơ bản, có thể cần cải thiện nếu muốn độ chính xác cao hơn
            is_duplicate = False
            for existing_item in startup_items:
                if existing_item["Lệnh"] == item["Lệnh"] and existing_item["Nguồn"].startswith("Thư mục Startup"):
                    is_duplicate = True
                    break
            if not is_duplicate:
                 startup_items.append(item)

    if not startup_items:
        return [{"Thông tin": "Không tìm thấy chương trình nào khởi động cùng Windows từ các nguồn phổ biến."}]
    return sorted(startup_items, key=lambda x: x['Tên'])

def run_ping_test(host="google.com", count=4):
    """
    Thực hiện ping đến một host cụ thể.
    """
    logging.info(f"Thực hiện ping đến host={host}, count={count}.")

    if not isinstance(host, str):
        err_msg = f"Lỗi: Đối số 'host' cho ping phải là một chuỗi (string), nhận được: {host} (kiểu: {type(host).__name__})."
        logging.error(err_msg)
        return {"status": "error", "message": err_msg}

    if not isinstance(count, int) or count <= 0:
        err_msg = f"Lỗi: Đối số 'count' cho ping phải là một số nguyên dương hợp lệ, nhận được: {count}."
        logging.error(err_msg)
        return {"status": "error", "message": err_msg}

    try:
        # Xác định tham số ping cho Windows (-n) hoặc Linux/macOS (-c)
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, str(count), str(host)] # Ensure host is also a string

        # Sử dụng CREATE_NO_WINDOW để ẩn cửa sổ console
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        # Use system's preferred encoding for potentially more robust output decoding
        preferred_encoding = locale.getpreferredencoding(False)
        if not preferred_encoding: # Fallback if locale.getpreferredencoding returns None
            preferred_encoding = 'utf-8'
            logging.warning("locale.getpreferredencoding(False) returned None, falling back to utf-8 for ping.")

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding=preferred_encoding, errors='ignore', startupinfo=startupinfo)
        stdout, stderr = process.communicate(timeout=30) # Tăng timeout cho ping

        if process.returncode == 0:
            return {"status": "success", "message": f"Ping đến {host} thành công.", "details": stdout.strip()}
        else:
            error_details = f"Lỗi ping (code {process.returncode}):\n"
            if stdout.strip(): error_details += f"Output:\n{stdout.strip()}\n"
            if stderr.strip(): error_details += f"Error Stream:\n{stderr.strip()}\n"
            return {"status": "error", "message": f"Ping đến {host} thất bại hoặc có lỗi.", "details": error_details.strip()}
    except subprocess.TimeoutExpired:
        logging.error(f"Ping đến {host} timeout.")
        return {"status": "error", "message": f"Ping đến {host} timeout sau 30 giây."}
    except Exception as e:
        logging.error(f"Lỗi khi thực hiện ping đến {host}: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi không xác định khi ping: {str(e)}"}

def get_network_configuration_details(wmi_service):
    """
    Lấy thông tin cấu hình mạng chi tiết cho các adapter IPEnabled.
    Bao gồm IP, Subnet, Gateway, DNS, MAC, DHCP status.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể truy cập cấu hình mạng."}]

    adapters_details = []
    try:
        query = "SELECT * FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled = True"
        adapters_config = wmi_service.ExecQuery(query)
        
        if not list(adapters_config): # Check if the query returned any results
            return [{"Thông tin": "Không tìm thấy card mạng nào có IP được kích hoạt."}]

        for adapter in adapters_config:
            ip_addresses = _get_wmi_property(adapter, "IPAddress", [])
            ip_subnets = _get_wmi_property(adapter, "IPSubnet", [])
            default_gateways = _get_wmi_property(adapter, "DefaultIPGateway", [])
            dns_servers = _get_wmi_property(adapter, "DNSServerSearchOrder", [])

            details = {
                "Card mạng": _get_wmi_property(adapter, "Description", NOT_IDENTIFIED),
                "Địa chỉ MAC": _get_wmi_property(adapter, "MACAddress", NOT_IDENTIFIED),
                "DHCP được bật": _get_wmi_property(adapter, "DHCPEnabled", NOT_AVAILABLE),
                "Máy chủ DHCP": _get_wmi_property(adapter, "DHCPServer", NOT_AVAILABLE) if _get_wmi_property(adapter, "DHCPEnabled") else "Không áp dụng",
                "Địa chỉ IP": ip_addresses if ip_addresses else [NOT_AVAILABLE],
                "Subnet Mask": ip_subnets if ip_subnets else [NOT_AVAILABLE],
                "Cổng mặc định": default_gateways if default_gateways else [NOT_AVAILABLE],
                "Máy chủ DNS": dns_servers if dns_servers else [NOT_AVAILABLE]
            }
            # WMI returns single items not in lists, ensure they are for consistent processing
            for key in ["Địa chỉ IP", "Subnet Mask", "Cổng mặc định", "Máy chủ DNS"]:
                if not isinstance(details[key], list):
                    details[key] = [details[key]] if details[key] is not None else [NOT_AVAILABLE]
            
            adapters_details.append(details)
        
        if not adapters_details: # Should be caught by the earlier check, but as a safeguard
            return [{"Thông tin": "Không có thông tin cấu hình mạng chi tiết nào được tìm thấy."}]
        return adapters_details

    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.error(f"Lỗi khi lấy thông tin cấu hình mạng: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} cấu hình mạng: {str(e)}"}]

def create_system_restore_point(description="Điểm khôi phục tự động bởi PcInfoApp"):
    """
    Tạo một điểm khôi phục hệ thống. Yêu cầu quyền Admin.
    Sử dụng WMI SystemRestore class.
    """
    logging.info(f"Yêu cầu tạo điểm khôi phục hệ thống với mô tả: {description}")
    if not is_admin():
        return {"status": "error", "message": "Yêu cầu quyền Administrator để tạo điểm khôi phục hệ thống."}

    com_initialized_rp = False
    try:
        win32com.client.pythoncom.CoInitialize()
        com_initialized_rp = True
        wmi_locator_rp = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        # SystemRestore class is in root\default
        service_rp = wmi_locator_rp.ConnectServer(".", r"root\default")
        system_restore = service_rp.Get("SystemRestore")

        # RPType: 0 (APPLICATION_INSTALL), 10 (MODIFY_SETTINGS), 12 (CANCELLED_OPERATION), etc.
        # EventType: 100 (BEGIN_SYSTEM_CHANGE), 101 (END_SYSTEM_CHANGE)
        # Using 0 for a generic application-triggered restore point.
        result = system_restore.CreateRestorePoint(description, 0, 100)
        return {"status": "success", "message": f"Đã yêu cầu tạo điểm khôi phục hệ thống. Kết quả: {result}. Kiểm tra System Restore để xác nhận."}
    except (pywintypes.com_error, Exception) as e: # type: ignore
        logging.error(f"Lỗi khi tạo điểm khôi phục hệ thống: {e}", exc_info=True)
        return {"status": "error", "message": f"Không thể tạo điểm khôi phục: {str(e)}"}
    finally:
        if com_initialized_rp:
            win32com.client.pythoncom.CoUninitialize()

# --- Các hàm tiện ích mạng mới ---
def lookup_dns_address(hostname):
    """
    Tra cứu địa chỉ IP của một hostname.
    """
    if not isinstance(hostname, str):
        return {"status": "error", "message": f"Hostname phải là một chuỗi, nhận được: {type(hostname).__name__}"}
    try:
        # gethostbyname_ex trả về (hostname, aliaslist, ipaddrlist)
        name, aliases, ipaddrs = socket.gethostbyname_ex(hostname)
        result = {
            "Hostname Chính": name,
            "Địa chỉ IP": ipaddrs if ipaddrs else [NOT_AVAILABLE],
        }
        if aliases:
            result["Tên Bí Danh (Aliases)"] = aliases
        return {"status": "success", "message": f"Tra cứu DNS cho '{hostname}' thành công.", "details": result}
    except socket.gaierror as e:
        logging.error(f"Lỗi tra cứu DNS cho {hostname}: {e}", exc_info=True)
        return {"status": "error", "message": f"Không thể phân giải hostname '{hostname}': {e}"}
    except Exception as e:
        logging.error(f"Lỗi không xác định khi tra cứu DNS cho {hostname}: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi không xác định: {e}"}

def get_active_network_connections():
    """
    Lấy danh sách các kết nối mạng đang hoạt động (tương tự netstat).
    """
    connections = []
    try:
        # kind='inet' bao gồm cả TCP và UDP, IPv4 và IPv6
        # Bạn có thể lọc cụ thể hơn nếu muốn, ví dụ: kind='tcp4'
        for conn in psutil.net_connections(kind='inet'):
            conn_info = {
                "Loại": conn.type, # SOCK_STREAM (TCP), SOCK_DGRAM (UDP)
                "Địa chỉ Cục bộ": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else NOT_AVAILABLE,
                "Địa chỉ Từ xa": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else NOT_AVAILABLE,
                "Trạng thái": conn.status if conn.status else NOT_IDENTIFIED,
                "PID": conn.pid if conn.pid else NOT_AVAILABLE
            }
            connections.append(conn_info)
        
        if not connections:
            return [{"Thông tin": "Không có kết nối mạng nào đang hoạt động hoặc không thể truy cập."}]
        return connections # Trả về list các dict
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách kết nối mạng: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} kết nối mạng: {str(e)}"}]

def flush_dns_cache():
    """
    Xóa cache DNS của hệ thống (ipconfig /flushdns).
    Yêu cầu quyền Admin để có hiệu lực.
    """
    if not is_admin():
        return {"status": "warning", "message": "Yêu cầu quyền Administrator để xóa cache DNS. Lệnh có thể không thành công."}
    try:
        process = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=15, check=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='oem', errors='ignore')
        return {"status": "success", "message": "Đã thực hiện lệnh xóa cache DNS thành công.", "details": process.stdout.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"Lỗi khi xóa cache DNS (CalledProcessError): {e.stderr or e.stdout}", exc_info=True)
        return {"status": "error", "message": f"Lỗi khi chạy ipconfig /flushdns (code {e.returncode}). Chi tiết: {e.stderr.strip() or e.stdout.strip()}"}
    except Exception as e:
        logging.error(f"Lỗi không xác định khi xóa cache DNS: {e}", exc_info=True)
        return {"status": "error", "message": f"Lỗi không xác định: {e}"}

# --- Hàm kiểm tra (nếu cần) ---
# Đặt đoạn code này vào file: c:\Users\vankh\Documents\GetInfoPCNew\core\pc_info_functions.py
# (Thêm vào cuối file, trước dòng "if __name__ == "__main__":" nếu có)
# import wmi # Đảm bảo wmi đã được import ở đầu file pc_info_functions.py
# import logging # Đảm bảo logging đã được import

def set_dns_servers(wmi_service, primary_dns, secondary_dns=None):
    """
    Đặt máy chủ DNS cho card mạng đang hoạt động.
    Yêu cầu quyền Administrator.
    Sử dụng đối tượng wmi_service (SWbemServices) được cung cấp.
    """
    if not wmi_service:
        return {"status": "Lỗi", "message": "Đối tượng WMI service không được cung cấp."}
    try:
        # Tìm card mạng đang hoạt động (có IP và Default Gateway)
        # Query for adapters using SWbemServices
        adapters_query = wmi_service.ExecQuery("SELECT * FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled=True")
        adapters = list(adapters_query) # adapters is a list of SWbemObject

        if not adapters:
            return {"status": "Lỗi", "message": "Không tìm thấy card mạng nào có IP được kích hoạt."}

        active_adapter = None
        # Ưu tiên card mạng có Default Gateway
        for adapter_obj in adapters: # adapter_obj is an SWbemObject
            default_ip_gateway_prop = adapter_obj.Properties_.Item("DefaultIPGateway")
            if default_ip_gateway_prop.IsArray and default_ip_gateway_prop.Value is not None and len(default_ip_gateway_prop.Value) > 0:
                active_adapter = adapter_obj
                logging.info(f"Tìm thấy card mạng hoạt động (có gateway): {adapter_obj.Properties_.Item('Description').Value} [{adapter_obj.Properties_.Item('SettingID').Value}]")
                break

        # Nếu không có card nào có gateway, thử tìm card đầu tiên có địa chỉ IP
        if not active_adapter:
            for adapter_obj in adapters:
                ip_address_prop = adapter_obj.Properties_.Item("IPAddress")
                if ip_address_prop.IsArray and ip_address_prop.Value is not None and len(ip_address_prop.Value) > 0:
                    active_adapter = adapter_obj
                    logging.info(f"Không có card mạng nào có gateway. Sử dụng card (có IP): {adapter_obj.Properties_.Item('Description').Value} [{adapter_obj.Properties_.Item('SettingID').Value}]")
                    break

        if not active_adapter:
             return {"status": "Lỗi", "message": "Không tìm thấy card mạng phù hợp để cấu hình DNS."}

        dns_servers_to_set = [primary_dns.strip()]
        if secondary_dns and secondary_dns.strip():
            dns_servers_to_set.append(secondary_dns.strip())

        adapter_description = active_adapter.Properties_.Item('Description').Value
        logging.info(f"Đang cố gắng đặt DNS cho {adapter_description}: {dns_servers_to_set}")

        # Use ExecMethod_ for a more robust WMI method call
        method_definition = active_adapter.Methods_.Item("SetDNSServerSearchOrder")
        in_params_instance = None
        if method_definition.InParameters:
            in_params_instance = method_definition.InParameters.SpawnInstance_()
            in_params_instance.DNSServerSearchOrder = dns_servers_to_set
        else: # Should not happen for SetDNSServerSearchOrder as it has InParameters
            return {"status": "Lỗi", "message": "Không tìm thấy định nghĩa tham số đầu vào cho SetDNSServerSearchOrder."}

        out_params_instance = active_adapter.ExecMethod_(method_definition.Name, in_params_instance)
        result_code = out_params_instance.ReturnValue # The WMI method's return code

        # Kiểm tra mã trả về từ WMI
        # Tham khảo: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/aa393295(v=vs.85)
        if result_code == 0: # Thành công
            return {"status": "Thành công",
                    "message": f"Đã đặt DNS thành công cho card mạng '{adapter_description}'.\nDNS chính: {primary_dns}\nDNS phụ: {secondary_dns if secondary_dns and secondary_dns.strip() else 'Không có'}"}
        elif result_code == 1: # Thành công, cần khởi động lại
             return {"status": "Thành công (cần khởi động lại)",
                     "message": f"Đã đặt DNS cho card mạng '{adapter_description}', nhưng cần khởi động lại máy để áp dụng hoàn toàn."}
        else:
            # Xử lý các mã lỗi phổ biến khác
            error_messages = {
                65: "Truy cập bị từ chối. Cần quyền Administrator.", # Privilege not held
                70: "Địa chỉ IP không hợp lệ.", # Invalid IP Address
                # Thêm các mã lỗi khác nếu cần từ tài liệu của Microsoft
            }
            msg = error_messages.get(result_code, f"Mã lỗi không xác định: {result_code}")
            logging.error(f"Lỗi khi đặt DNS cho {adapter_description}. Mã trả về: {result_code} - {msg}")
            return {"status": "Lỗi", "message": f"Không thể đặt DNS cho card mạng '{adapter_description}'. {msg}"}

    except pywintypes.com_error as e: # Bắt lỗi COM cụ thể
        logging.exception("Lỗi COM khi cấu hình DNS:")
        # Thử lấy thông tin lỗi chi tiết hơn từ com_error
        excepinfo = getattr(e, 'excepinfo', None)
        error_text = str(e)
        if excepinfo and excepinfo[2]: # Description
            error_text = excepinfo[2]

        # Kiểm tra xem có phải lỗi từ chối truy cập không
        if "WBEM_E_ACCESS_DENIED" in error_text.upper() or "ACCESS IS DENIED" in error_text.upper() or \
           (hasattr(e, 'hresult') and e.hresult == -2147024891): # 0x80070005 Access Denied
             return {"status": "Lỗi", "message": "Lỗi WMI/COM: Truy cập bị từ chối. Vui lòng chạy ứng dụng với quyền Administrator."}
        return {"status": "Lỗi", "message": f"Lỗi WMI/COM: {error_text}"}
    except Exception as e:
        logging.exception("Lỗi không xác định khi cấu hình DNS:")
        return {"status": "Lỗi", "message": f"Lỗi không mong muốn: {str(e)}"}

    # --- Hàm lấy tình trạng ổ cứng (S.M.A.R.T. cơ bản) ---
def get_disk_health_status(wmi_service):
    """
    Lấy trạng thái sức khỏe cơ bản của các ổ đĩa vật lý.
    Sử dụng Win32_DiskDrive.Status và thử MSStorageDriver_FailurePredictStatus.
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kiểm tra tình trạng ổ cứng."}]

    disk_health_details = []
    try:
        # 1. Lấy thông tin từ Win32_DiskDrive
        # Thêm PnPDeviceID để khớp với S.M.A.R.T. status
        disks_w32 = wmi_service.ExecQuery("SELECT DeviceID, Model, Index, Status, Size, PnPDeviceID FROM Win32_DiskDrive")
        disk_w32_list = list(disks_w32)
        if not disk_w32_list:
            return [{"Thông tin": f"{NOT_FOUND} ổ cứng vật lý nào."}]

        for disk_w32 in disk_w32_list:
            model = _get_wmi_property(disk_w32, "Model")
            device_id_w32 = _get_wmi_property(disk_w32, "DeviceID")
            pnp_device_id = _get_wmi_property(disk_w32, "PnPDeviceID", None) # Lấy PnPDeviceID
            status_w32 = _get_wmi_property(disk_w32, "Status", NOT_IDENTIFIED) # "OK", "Error", "Degraded", etc.
            disk_index = _get_wmi_property(disk_w32, "Index", -1)
            size_gb = int(_get_wmi_property(disk_w32, "Size", 0)) // (1024**3)

            # Mặc định tình trạng dự đoán là không có
            predict_failure = NOT_AVAILABLE
            reason_code = NOT_AVAILABLE

            # 2. Thử lấy thông tin dự đoán lỗi từ MSStorageDriver_FailurePredictStatus (root\wmi)
            _local_com_init_smart = False
            service_root_wmi_smart = None
            
            try:
                try:
                    win32com.client.pythoncom.CoInitialize()
                    _local_com_init_smart = True
                except pywintypes.com_error: pass

                wmi_locator_smart = win32com.client.Dispatch("WbemScripting.SWbemLocator")
                service_root_wmi_smart = wmi_locator_smart.ConnectServer(".", r"root\wmi")

                if service_root_wmi_smart and pnp_device_id:
                    try:
                        # Escape backslashes and percent signs for WQL LIKE
                        pnp_device_id_escaped = pnp_device_id.replace("\\", "\\\\").replace("%", "[%]")
                        # Truy vấn S.M.A.R.T. status cho PnPDeviceID cụ thể
                        query_smart = f"SELECT PredictFailure, Reason FROM MSStorageDriver_FailurePredictStatus WHERE InstanceName LIKE '{pnp_device_id_escaped}%'"
                        smart_status_items = service_root_wmi_smart.ExecQuery(query_smart)
                        
                        matched_smart_item = None
                        if list(smart_status_items): # Kiểm tra nếu truy vấn trả về kết quả
                            matched_smart_item = list(smart_status_items)[0] # Lấy mục đầu tiên khớp

                        if matched_smart_item:
                            is_failing = _get_wmi_property(matched_smart_item, "PredictFailure") # Boolean
                            if is_failing is True:
                                predict_failure = "Có thể sắp lỗi"
                                reason_code = _get_wmi_property(matched_smart_item, "Reason", NOT_AVAILABLE)
                            elif is_failing is False:
                                predict_failure = "Không dự đoán lỗi"
                                # reason_code không áp dụng nếu không dự đoán lỗi
                        # Nếu không khớp, predict_failure vẫn là NOT_AVAILABLE
                    except (pywintypes.com_error, Exception) as e_smart_item:
                        logging.warning(f"Lỗi khi truy vấn MSStorageDriver_FailurePredictStatus cho PnPDeviceID {pnp_device_id}: {e_smart_item}")
                elif not pnp_device_id:
                    logging.debug(f"PnPDeviceID không khả dụng cho ổ đĩa {model}, không thể truy vấn S.M.A.R.T. cụ thể.")
            except (pywintypes.com_error, Exception) as e_smart:
                logging.warning(f"Không thể truy vấn MSStorageDriver_FailurePredictStatus: {e_smart}")
            finally:
                if _local_com_init_smart: win32com.client.pythoncom.CoUninitialize()

            disk_health_details.append({
                "Model": model, "Kích thước (GB)": size_gb,
                "DeviceID": device_id_w32, "Trạng thái (Win32)": status_w32,
                "Dự đoán Lỗi (S.M.A.R.T.)": predict_failure,
                "Mã lý do (S.M.A.R.T.)": reason_code if predict_failure == "Có thể sắp lỗi" else NOT_AVAILABLE
            })
        return disk_health_details
    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy tình trạng ổ cứng: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} tình trạng ổ cứng: {str(e)}"}]

def get_battery_details(wmi_service):
    """
    Lấy thông tin chi tiết về pin (cho laptop).
    """
    if not wmi_service:
        return [{"Lỗi": ERROR_WMI_CONNECTION, "Chi tiết": "Không thể kiểm tra thông tin pin."}]

    battery_details_list = []
    try:
        batteries = wmi_service.ExecQuery("SELECT * FROM Win32_Battery")
        battery_list_wmi = list(batteries)
        if not battery_list_wmi:
            return [{"Thông tin": "Không tìm thấy pin nào (có thể là PC hoặc không có pin)."}]

        for battery in battery_list_wmi:
            name = _get_wmi_property(battery, "Name", NOT_IDENTIFIED)
            status_code = _get_wmi_property(battery, "BatteryStatus") # 1: Discharging, 2: On AC, 3: Fully Charged, etc.
            estimated_charge = _get_wmi_property(battery, "EstimatedChargeRemaining", NOT_AVAILABLE) # Percentage
            design_capacity_mwh = _get_wmi_property(battery, "DesignCapacity", 0) # mWh
            full_charge_capacity_mwh = _get_wmi_property(battery, "FullChargeCapacity", 0) # mWh

            status_text_map = {
                1: "Đang xả (Discharging)", 2: "Đang sạc (On AC / Charging)", 3: "Sạc đầy (Fully Charged)",
                4: "Thấp (Low)", 5: "Nghiêm trọng (Critical)", 6: "Đang sạc (Charging)", # Duplicate of 2 for some systems
                7: "Đang sạc & Cao (Charging and High)", 8: "Đang sạc & Thấp (Charging and Low)",
                9: "Đang sạc & Nghiêm trọng (Charging and Critical)", 10: "Không xác định (Unknown)",
                11: "Hỏng một phần (Partially Charged)"
            }
            status_text = status_text_map.get(status_code, f"Mã trạng thái: {status_code}")

            health_percent = NOT_AVAILABLE
            if design_capacity_mwh and full_charge_capacity_mwh and int(design_capacity_mwh) > 0:
                try:
                    health_percent = round((int(full_charge_capacity_mwh) / int(design_capacity_mwh)) * 100, 1)
                except (ValueError, TypeError, ZeroDivisionError):
                    health_percent = NOT_AVAILABLE

            battery_details_list.append({
                "Tên Pin": name,
                "Trạng thái": status_text,
                "Mức pin ước tính (%)": estimated_charge,
                "Sức khỏe Pin Ước tính (%)": f"{health_percent}%" if health_percent != NOT_AVAILABLE else NOT_AVAILABLE,
                "Dung lượng Thiết kế (mWh)": design_capacity_mwh if design_capacity_mwh else NOT_AVAILABLE,
                "Dung lượng Sạc đầy (mWh)": full_charge_capacity_mwh if full_charge_capacity_mwh else NOT_AVAILABLE,
            })
        return battery_details_list
    except (pywintypes.com_error, Exception) as e:
        logging.error(f"Lỗi khi lấy thông tin pin: {e}", exc_info=True)
        return [{"Lỗi": f"{ERROR_FETCHING_INFO} pin: {str(e)}"}]

# --- Placeholder Functions for New Features ---
def run_cpu_benchmark():
    """Placeholder for CPU benchmarking."""
    logging.info("Chức năng Đánh giá CPU được gọi (chưa triển khai đầy đủ).")
    # A real benchmark might return scores like PassMark, Geekbench (synthetic), or time for specific tasks.
    return {"status": "info", "message": "Chức năng Đánh giá CPU hiện chưa được triển khai đầy đủ. Một bài kiểm tra CPU thực tế có thể đo hiệu năng đơn nhân và đa nhân, ví dụ, bằng cách tính toán số Pi hoặc nén dữ liệu."}

def run_gpu_benchmark():
    """Placeholder for GPU benchmarking."""
    logging.info("Chức năng Đánh giá GPU được gọi (chưa triển khai đầy đủ).")
    # A real benchmark might render complex 3D scenes and report FPS.
    return {"status": "info", "message": "Chức năng Đánh giá GPU hiện chưa được triển khai đầy đủ. Một bài kiểm tra GPU thực tế thường bao gồm việc render đồ họa 3D để đo số khung hình mỗi giây (FPS)."}

def run_memory_speed_test():
    """Placeholder for Memory Speed Test."""
    logging.info("Chức năng Kiểm tra Tốc độ Bộ nhớ được gọi (chưa triển khai đầy đủ).")
    # A real test would measure read/write/copy speeds of RAM.
    return {"status": "info", "message": "Chức năng Kiểm tra Tốc độ Bộ nhớ hiện chưa được triển khai đầy đủ. Một bài kiểm tra tốc độ bộ nhớ thực tế sẽ đo băng thông đọc, ghi và sao chép của RAM."}

def run_disk_speed_test(file_size_mb=100, block_size_kb=1024):
    """
    Performs a basic disk speed test for each local fixed drive.
    Returns a list of dictionaries, each representing a drive's test results.
    """
    logging.info(f"Running basic disk speed test: file_size_MB={file_size_mb}, block_size_KB={block_size_kb}")
    results_list = []
    
    # Get list of local fixed drives (DriveType=3)
    # Use psutil as it's simpler than WMI for this
    try:
        partitions = psutil.disk_partitions(all=False) # Only physical partitions
        # Filter for fixed drives (type='local' and fstype in typical Windows file systems)
        # More robust check might involve WMI Win32_LogicalDisk DriveType=3
        local_drives = [p.mountpoint for p in partitions if p.fstype in ['NTFS', 'FAT32', 'exFAT'] and 'fixed' in p.opts]
        
        if not local_drives:
            logging.warning("No local fixed drives found for disk speed test.")
            return [{"Thông báo": "Không tìm thấy ổ đĩa cứng cục bộ nào để kiểm tra tốc độ."}]
            
    except Exception as e:
        logging.error(f"Lỗi khi lấy danh sách ổ đĩa: {e}", exc_info=True)
        return [{"Lỗi": f"Lỗi khi lấy danh sách ổ đĩa: {e}"}]

    bytes_to_test = file_size_mb * 1024 * 1024
    block_bytes = block_size_kb * 1024
    if block_bytes <= 0:
        return [{"Lỗi": "Kích thước khối phải là số dương."}]
    
    # Generate a single data block to reuse
    try:
        data_block = os.urandom(block_bytes)
    except Exception as e:
        logging.error(f"Lỗi tạo dữ liệu kiểm tra: {e}", exc_info=True)
        return [{"Lỗi": f"Không thể tạo dữ liệu kiểm tra: {e}"}]

    temp_file_path = None # Initialize to ensure it's defined for finally

    for drive_path in local_drives:
        temp_file_path = None
        drive_result = {
            "Ổ đĩa": drive_path,
            "Kích thước File Test (MB)": file_size_mb, # Đổi tên key cho rõ ràng hơn trong bảng
            "Kích thước Khối (KB)": block_size_kb,    # Đổi tên key
            "Tốc độ Ghi (MB/s)": NOT_AVAILABLE,
            "Tốc độ Đọc (MB/s)": NOT_AVAILABLE,
            "Trạng thái": "Chưa kiểm tra"
        }
        
        try:
            temp_file_descriptor, temp_file_path = tempfile.mkstemp(suffix=".tmp", prefix="disk_speed_test_", dir=drive_path)
            os.close(temp_file_descriptor)

            logging.info(f"Testing drive {drive_path}, temporary file: {temp_file_path}")

            # --- Write Test ---
            write_start_time = time.perf_counter()
            bytes_written = 0
            with open(temp_file_path, "wb") as f:
                while bytes_written < bytes_to_test:
                    write_size = min(block_bytes, bytes_to_test - bytes_written)
                    # Adjust last block if smaller, or ensure data_block is used correctly
                    current_block_to_write = data_block[:write_size] if write_size < block_bytes else data_block
                    f.write(current_block_to_write)
                    bytes_written += write_size
            write_duration = time.perf_counter() - write_start_time

            write_speed_mbps = NOT_AVAILABLE
            if write_duration > 0:
                write_speed_mbps = round((bytes_written / (1024 * 1024)) / write_duration, 2)
            drive_result["Tốc độ Ghi (MB/s)"] = write_speed_mbps

            # --- Read Test ---
            read_start_time = time.perf_counter()
            bytes_read = 0
            with open(temp_file_path, "rb") as f:
                while True:
                    chunk = f.read(block_bytes)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
            read_duration = time.perf_counter() - read_start_time

            read_speed_mbps = NOT_AVAILABLE
            if read_duration > 0:
                read_speed_mbps = round((bytes_read / (1024 * 1024)) / read_duration, 2)
            drive_result["Tốc độ Đọc (MB/s)"] = read_speed_mbps
            drive_result["Trạng thái"] = "Hoàn thành"

            logging.info(f"Disk speed test for {drive_path} completed: Write={write_speed_mbps} MB/s, Read={read_speed_mbps} MB/s")

        except Exception as e:
            logging.error(f"Error during disk speed test for {drive_path}: {e}", exc_info=True)
            drive_result["Tốc độ Ghi (MB/s)"] = NOT_AVAILABLE # Đảm bảo các trường tốc độ là NOT_AVAILABLE khi lỗi
            drive_result["Tốc độ Đọc (MB/s)"] = NOT_AVAILABLE
            drive_result["Trạng thái"] = f"Lỗi - {str(e)}"
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logging.info(f"Temporary file {temp_file_path} deleted.")
                except Exception as e_del:
                    logging.error(f"Failed to delete temporary file {temp_file_path}: {e_del}")
        results_list.append(drive_result)
        
    return results_list # Trả về danh sách các dictionary


def get_service_status_display(service_name):
    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1] # dwCurrentState
        startup_type = win32serviceutil.QueryServiceConfig(service_name)[1] # dwStartType

        status_map = {
            win32service.SERVICE_STOPPED: "Đã dừng", win32service.SERVICE_START_PENDING: "Đang khởi động",
            win32service.SERVICE_STOP_PENDING: "Đang dừng", win32service.SERVICE_RUNNING: "Đang chạy",
            win32service.SERVICE_CONTINUE_PENDING: "Đang tiếp tục", win32service.SERVICE_PAUSE_PENDING: "Đang tạm dừng",
            win32service.SERVICE_PAUSED: "Đã tạm dừng",
        }
        startup_map = {
            win32service.SERVICE_AUTO_START: "Tự động", win32service.SERVICE_DEMAND_START: "Thủ công",
            win32service.SERVICE_DISABLED: "Vô hiệu hóa", win32service.SERVICE_BOOT_START: "Boot Start",
            win32service.SERVICE_SYSTEM_START: "System Start"
        }
        return f"Hiện tại: {status_map.get(status, 'Không rõ')}, Khởi động: {startup_map.get(startup_type, 'Không rõ')}"
    except Exception: # pywintypes.error or other exceptions
        # logging.warning(f"Không thể truy vấn dịch vụ '{service_name}': {e}")
        return "Không thể truy vấn (cần Admin hoặc dịch vụ không tồn tại)"

def optimize_windows_services():
    """
    Provides *suggestions* for optimizing Windows services.
    DOES NOT actually change any service settings.
    """
    logging.info("Chức năng Tối ưu Dịch Vụ Windows được gọi (chỉ cung cấp gợi ý).")

    suggested_optimizations = [
        {"Tên Dịch vụ": "DiagTrack", "Tên Hiển thị": "Connected User Experiences and Telemetry", "Trạng thái Hiện tại": get_service_status_display("DiagTrack"), "Gợi ý Tối ưu": "Vô hiệu hóa (Disabled)", "Mô tả / Rủi ro": "Gửi dữ liệu chẩn đoán về Microsoft. Tắt có thể tăng quyền riêng tư."},
        {"Tên Dịch vụ": "dmwappushservice", "Tên Hiển thị": "Device Management Wireless Application Protocol (WAP) Push message Routing Service", "Trạng thái Hiện tại": get_service_status_display("dmwappushservice"), "Gợi ý Tối ưu": "Vô hiệu hóa (Disabled)", "Mô tả / Rủi ro": "Thường không cần thiết cho người dùng gia đình."},
        {"Tên Dịch vụ": "PrintSpoole", "Tên Hiển thị": "Print Spooler", "Trạng thái Hiện tại": get_service_status_display("PrintSpoole"), "Gợi ý Tối ưu": "Thủ công (Manual) nếu không thường xuyên in", "Mô tả / Rủi ro": "Quản lý in ấn. Tắt sẽ không thể in."}, # Tên dịch vụ đúng là PrintSpoole
        {"Tên Dịch vụ": "RemoteRegistry", "Tên Hiển thị": "Remote Registry", "Trạng thái Hiện tại": get_service_status_display("RemoteRegistry"), "Gợi ý Tối ưu": "Vô hiệu hóa (Disabled)", "Mô tả / Rủi ro": "Cho phép sửa đổi Registry từ xa. Tắt để tăng bảo mật."},
        {"Tên Dịch vụ": "Fax", "Tên Hiển thị": "Fax", "Trạng thái Hiện tại": get_service_status_display("Fax"), "Gợi ý Tối ưu": "Vô hiệu hóa (Disabled)", "Mô tả / Rủi ro": "Hỗ trợ fax. Tắt nếu không sử dụng."},
    ]
    
    admin_note = "" if is_admin() else "Lưu ý: Một số thông tin trạng thái dịch vụ có thể không hiển thị đầy đủ do thiếu quyền Administrator.\n"

    return {
        "status": "info",
        "message": f"{admin_note}Đây là các gợi ý tối ưu dịch vụ. Việc thay đổi cài đặt dịch vụ hệ thống có thể ảnh hưởng đến hoạt động của Windows. Hãy tìm hiểu kỹ trước khi thực hiện.",
        "details": suggested_optimizations
    }

def clean_registry_with_backup():
    """
    *Simulates* cleaning registry entries and *simulates* creating a backup.
    DOES NOT actually delete any registry keys or values or create a real backup.
    """
    logging.info("Chức năng Dọn Dẹp Registry (Có Sao Lưu) được gọi (chỉ mô phỏng và cung cấp ví dụ).")
    results = {
        "Trạng thái Sao lưu": NOT_AVAILABLE, "Đường dẫn Sao lưu (Mô phỏng)": NOT_AVAILABLE,
        "Khu vực có thể kiểm tra (Ví dụ)": [],
        "Hành động Thực hiện": "Không có thay đổi nào được thực hiện (chỉ mô phỏng).", "Lỗi": []
    }
    admin_note = ""
    if not is_admin():
        admin_note = "Cảnh báo: Chức năng sao lưu và truy cập Registry đầy đủ yêu cầu quyền Administrator. Hoạt động ở chế độ mô phỏng hạn chế.\n"
        results["Lỗi"].append("Thiếu quyền Administrator.")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        simulated_backup_folder = os.path.join(os.path.expanduser("~"), "Documents", "Registry_Backups_PcInfoApp_Simulated")
        os.makedirs(simulated_backup_folder, exist_ok=True)
        simulated_backup_path = os.path.join(simulated_backup_folder, f"simulated_registry_backup_{timestamp}.reg")
        with open(simulated_backup_path, "w", encoding="utf-8") as f:
            f.write(f"; Simulated Registry Backup by PcInfoApp at {datetime.now()}\n; NO ACTUAL DATA IS BACKED UP IN SIMULATION MODE.\n")
        results["Trạng thái Sao lưu"] = "Sao lưu Registry ĐƯỢC MÔ PHỎNG thành công."
        results["Đường dẫn Sao lưu (Mô phỏng)"] = simulated_backup_path
    except Exception as e_backup:
        results["Trạng thái Sao lưu"] = "Mô phỏng sao lưu Registry thất bại."
        results["Lỗi"].append(f"Lỗi mô phỏng sao lưu: {str(e_backup)}")

    results["Khu vực có thể kiểm tra (Ví dụ)"] = [
        {"Khu vực": "Lịch sử lệnh Run (RunMRU)", "Đường dẫn": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", "Mô tả": "Lưu các lệnh đã gõ trong Run. Xóa tăng riêng tư."},
        {"Khu vực": "File đã mở gần đây (RecentDocs)", "Đường dẫn": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs", "Mô tả": "Lưu danh sách tài liệu mở gần đây. Xóa tăng riêng tư."},
    ]

    final_message = f"{admin_note}Mô phỏng dọn dẹp Registry hoàn tất. {results['Hành động Thực hiện']}"
    if results["Lỗi"]:
        final_message += " Đã xảy ra lỗi trong quá trình mô phỏng."

    return { "status": "warning" if results["Lỗi"] else "info", "message": final_message, "details": results }
# --- Hàm kiểm tra (nếu cần) ---
if __name__ == "__main__":
    print("Đang thu thập thông tin PC...")
    pc_info_data = get_detailed_system_information() # Changed to new main function name
    print("\n--- Kết quả thu thập (dạng dictionary) ---")
    # Print nicely formatted JSON to check structure and data
    try:
        print(json.dumps(pc_info_data, indent=4, ensure_ascii=False))
    except TypeError as e:
        print(f"Lỗi khi JSON dump (có thể do đối tượng không thể serialize): {e}")
        print("Dữ liệu thô:", pc_info_data)
    print("\nQuá trình thu thập hoàn tất.")

    print("\n--- Kiểm tra tiện ích bổ sung ---")
    # print("Kiểm tra kích hoạt Windows:", check_windows_activation_status())
    # print("Kiểm tra kích hoạt Office:", check_office_activation_status())
    # print("Tạo báo cáo pin:", generate_battery_report())
    # print("Mở Resource Monitor:", open_resource_monitor())
    # wmi_service_test, com_initialized_test = _connect_wmi()
    # if wmi_service_test:
    #     print("RAM Details:", get_ram_details(wmi_service_test))
    # if com_initialized_test:
    #     try: win32com.client.pythoncom.CoUninitialize()
    #     except: pass
    # print("Startup Programs:", get_startup_programs())
    # print("Ping Test (google.com):", run_ping_test("google.com"))
    # print("Create Restore Point:", create_system_restore_point("Test Restore Point by PcInfoApp")) # Requires Admin
