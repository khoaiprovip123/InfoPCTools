# main.py (Đặt ở thư mục gốc GetInfoPCNew)
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Thêm thư mục gốc vào sys.path để Python tìm thấy các module core và gui
# Cách này hữu ích khi chạy trực tiếp main.py từ thư mục gốc
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

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


    main_window = PcInfoAppQt()
    main_window.show()
    sys.exit(app.exec_())
