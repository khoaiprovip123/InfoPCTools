import logging
import win32com.client
from PyQt5.QtCore import QThread, pyqtSignal

# Import hằng số lỗi từ core (nếu cần thiết cho thông báo lỗi cụ thể)
# Hoặc có thể truyền thông báo lỗi như một tham số
from core.pc_info_functions import ERROR_WMI_CONNECTION # type: ignore

class WorkerThread(QThread):
    task_completed = pyqtSignal(str, object) # task_name, result_data
    task_error = pyqtSignal(str, str)       # task_name, error_message

    def __init__(self, task_function, task_name, needs_wmi=False, wmi_namespace="root\\CIMV2", *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.task_name = task_name
        self.needs_wmi = needs_wmi
        self.button_to_manage = kwargs.pop('button_to_manage', None) # Get the button
        self.original_button_text = kwargs.pop('original_button_text', "")
        self.wmi_namespace = wmi_namespace # Namespace WMI cần thiết cho tác vụ
        self.args = args
        self.kwargs = kwargs
        self.wmi_service_local = None
        self.com_initialized_local = False

    def run(self):
        if self.button_to_manage:
            self.button_to_manage.setEnabled(False)
            self.button_to_manage.setText("Đang xử lý...")

        result_data = None
        try:
            if self.needs_wmi:
                win32com.client.pythoncom.CoInitialize()
                self.com_initialized_local = True
                wmi_locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
                self.wmi_service_local = wmi_locator.ConnectServer(".", self.wmi_namespace)
                logging.info(f"WMI connected to {self.wmi_namespace} in thread for task: {self.task_name}")

                if not self.wmi_service_local:
                    self.task_error.emit(self.task_name, f"{ERROR_WMI_CONNECTION} for task {self.task_name}")
                    return
                result_data = self.task_function(self.wmi_service_local, *self.args, **self.kwargs)
            else:
                result_data = self.task_function(*self.args, **self.kwargs)

            self.task_completed.emit(self.task_name, result_data)

        except Exception as e:
            logging.exception(f"Error in worker thread for task {self.task_name}:")
            self.task_error.emit(self.task_name, str(e))
        finally:
            if self.com_initialized_local:
                try:
                    win32com.client.pythoncom.CoUninitialize()
                    logging.info(f"COM uninitialized in thread for task: {self.task_name}")
                except Exception as com_e:
                    logging.error(f"Error uninitializing COM in thread for {self.task_name}: {com_e}")
            if self.button_to_manage:
                self.button_to_manage.setText(self.original_button_text)
                self.button_to_manage.setEnabled(True)