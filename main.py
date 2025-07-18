import sys
import os
sys.path.append(os.path.abspath('src'))
from ui.ui import SystemMonitorApp

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()