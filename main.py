# main.py (Đặt ở thư mục gốc GetInfoPCNew)
import sys
import os
import logging

# Đảm bảo output console sử dụng UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import atexit
import atexit
import os
import logging
import sys

# Đảm bảo output console sử dụng UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào sys.path để Python tìm thấy các module core và gui
# Cách này hữu ích khi chạy trực tiếp main.py từ thư mục gốc
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
# --- Cấu hình Logging và Đường dẫn File Log ---
LOG_DIR_NAME = "logs" # Tên thư mục log
LOG_FILENAME = "app_pc_info.log"
# Đường dẫn tuyệt đối đến thư mục gốc của dự án (nơi main.py tọa lạc)
PROJECT_ROOT_DIR = current_dir # current_dir đã được định nghĩa ở trên
LOG_DIR_PATH = os.path.join(PROJECT_ROOT_DIR, LOG_DIR_NAME)
LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, LOG_FILENAME)

def setup_global_logging():
    """Thiết lập logging toàn cục cho ứng dụng, ghi ra file và console."""
    if not os.path.exists(LOG_DIR_PATH):
        os.makedirs(LOG_DIR_PATH)
    logging.basicConfig(
        level=logging.DEBUG, # Changed to DEBUG to capture more details
        format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout) # Ghi ra console
        ]
    )
    logging.info(f"Logging được thiết lập. File log: {LOG_FILE_PATH}")

def cleanup_log_file_on_exit():
    """Xóa file log khi chương trình thoát."""
    logging.info("Ứng dụng đang thoát. Thực hiện dọn dẹp file log...")
    logging.shutdown() # Đảm bảo tất cả các handler đã đóng file
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
        print(f"INFO: File log '{LOG_FILE_PATH}' đã được xóa.") # Dùng print vì logging có thể đã shutdown


import flet as ft
from gui.pc_info_gui_flet_new import main as main_flet

if __name__ == "__main__":
    # Thiết lập logging và đăng ký hàm dọn dẹp
    setup_global_logging()
    atexit.register(cleanup_log_file_on_exit)

    logging.info("Khởi tạo ứng dụng PcInfoAppFlet.")

    ft.app(target=main_flet)
    logging.info("Ứng dụng PcInfoAppFlet đã hiển thị. Bắt đầu vòng lặp sự kiện.")

