import sys
import os
import logging

# Configure logging to a file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pc_app.log")
if os.path.exists(log_file):
    os.remove(log_file) # remove old log file
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Application starting")

try:
    sys.path.append(os.path.abspath('src'))
    logging.info("Appended src to sys.path")
    from src.ui.ui import SystemMonitorApp
    logging.info("Imported SystemMonitorApp")

    if __name__ == "__main__":
        logging.info("Inside __main__ block")
        app = SystemMonitorApp()
        logging.info("SystemMonitorApp instantiated")
        app.mainloop()
        logging.info("mainloop finished")
except Exception as e:
    logging.error("An exception occurred: %s", str(e), exc_info=True)

logging.info("Application finished")