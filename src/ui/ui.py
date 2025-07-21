import customtkinter as ctk
from PIL import Image
from logic import localization
from .views.dashboard_view import DashboardView
from .views.hardware_info_view import HardwareInfoView
from .views.applications_view import ApplicationsView
from .views.security_view import SecurityView
from .views.network_view import NetworkView
from .views.repair_restore_view import RepairRestoreView
from .views.settings_view import SettingsView
from .views.detail_view import DetailView

class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(localization.get_text("app_title"))
        self.geometry("1100x700")
        self.resizable(False, False)

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.content_frames = {}
        self.current_view = None

        self.create_sidebar()
        self.create_content_frames()
        
        self.show_frame("Dashboard")

    def create_sidebar(self):
        logo_image = ctk.CTkImage(Image.open("assets/logo/hpc-logo.png"), size=(50, 50))
        logo_label = ctk.CTkLabel(self.sidebar, image=logo_image, text="", compound="left", font=("Arial", 16, "bold"))
        logo_label.pack(pady=(10, 5))

        menu_buttons = [
            (localization.get_text("Dashboard"), "assets/icons/dashboard.png", lambda: self.show_frame("Dashboard")),
            (localization.get_text("Hardware Info"), "assets/icons/system.png", lambda: self.show_frame("Hardware Info")),
            (localization.get_text("Applications"), "assets/icons/utilities.png", lambda: self.show_frame("Applications")),
            (localization.get_text("Security"), "assets/icons/security.png", lambda: self.show_frame("Security")),
            (localization.get_text("Network"), "assets/icons/network.png", lambda: self.show_frame("Network")),
            (localization.get_text("Repair & Restore"), "assets/icons/system_fix.png", lambda: self.show_frame("Repair & Restore")),
            (localization.get_text("Settings"), "assets/icons/optimize.png", lambda: self.show_frame("Settings"))
        ]

        for text, icon_path, command in menu_buttons:
            image = ctk.CTkImage(Image.open(icon_path), size=(24, 24))
            button = ctk.CTkButton(self.sidebar, text=text, image=image, anchor="w", command=command)
            button.pack(fill="x", padx=10, pady=5)

        

    def create_content_frames(self):
        self.content_frames["Dashboard"] = DashboardView(self.main_container, app_instance=self)
        self.content_frames["Hardware Info"] = HardwareInfoView(self.main_container)
        self.content_frames["Applications"] = ApplicationsView(self.main_container)
        self.content_frames["Security"] = SecurityView(self.main_container)
        self.content_frames["Network"] = NetworkView(self.main_container)
        self.content_frames["Repair & Restore"] = RepairRestoreView(self.main_container)
        self.content_frames["Settings"] = SettingsView(self.main_container, app=self)

    def show_frame(self, name):
        if name.startswith("Detail -"):
            if name not in self.content_frames:
                self.content_frames[name] = DetailView(self.main_container, title=name.replace("Detail - ", ""))
        
        if self.current_view:
            self.current_view.cancel_updates()
            self.current_view.pack_forget()

        self.current_view = self.content_frames[name]
        self.current_view.pack(fill="both", expand=True)
        # If the view has updates, it will start them in its own __init__ or a dedicated method
        if hasattr(self.current_view, 'update_dashboard'):
            self.current_view.update_dashboard()
        if hasattr(self.current_view, 'update_connections'):
            self.current_view.update_connections()


    def recreate_ui(self):
        current_frame_name = None
        for name, frame in self.content_frames.items():
            if frame == self.current_view:
                current_frame_name = name
            frame.destroy()

        self.sidebar.destroy()

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.create_sidebar()
        self.create_content_frames()
        
        if current_frame_name:
            self.show_frame(current_frame_name)
        else:
            self.show_frame("Dashboard")
