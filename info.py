# File: info.py (hoặc tên file chính của bạn)

import logging
from gui.pc_info_gui import PcInfoApp # <-- Import class PcInfoApp

# --- Cấu hình Logging (Nếu bạn muốn cấu hình ở đây) ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Hoặc bạn có thể giữ cấu hình logging trong pc_info_gui.py

if __name__ == "__main__":
    # Tạo một instance của ứng dụng GUI
    app = PcInfoApp()
    # Chạy vòng lặp chính của Tkinter
    app.mainloop()
