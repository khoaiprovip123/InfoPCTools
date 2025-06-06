# main.py (Đặt ở thư mục gốc GetInfoPCNew)
import sys
import os
import logging
import atexit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

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


from gui.gui_qt import PcInfoAppQt, resource_path # Import từ file gui_qt.py

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Đặt icon cho ứng dụng (tùy chọn)
    try:
        icon_path = resource_path(os.path.join("assets", "logo", "hpc-logo.ico"))
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback hoặc không đặt icon nếu không tìm thấy
            print(f"Warning: Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Error setting window icon: {e}")

     # Thiết lập logging và đăng ký hàm dọn dẹp
    setup_global_logging()
    atexit.register(cleanup_log_file_on_exit)

    logging.info("Khởi tạo ứng dụng PcInfoAppQt.")


    main_window = PcInfoAppQt()
    main_window.show()
    logging.info("Ứng dụng PcInfoAppQt đã hiển thị. Bắt đầu vòng lặp sự kiện.")
    sys.exit(app.exec_())
