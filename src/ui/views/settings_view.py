import customtkinter as ctk
from logic import actions, localization

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app

        # Application Info
        app_info_frame = ctk.CTkFrame(self)
        app_info_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Application Information"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        ctk.CTkLabel(app_info_frame, text=f"{localization.get_text('Version')}: 1.0").pack(anchor="w", padx=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Developed by Gemini AI from Google.")).pack(anchor="w", padx=10)

        # Theme Settings
        theme_frame = ctk.CTkFrame(self)
        theme_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(theme_frame, text=localization.get_text("Theme Settings"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        self.theme_switch = ctk.CTkSwitch(theme_frame, text=localization.get_text("Dark Mode"), command=self.toggle_theme)
        self.theme_switch.pack(anchor="w", padx=10, pady=5)
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

        # Language Settings
        lang_frame = ctk.CTkFrame(self)
        lang_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(lang_frame, text=localization.get_text("Language Settings"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        self.language_optionmenu = ctk.CTkOptionMenu(lang_frame, values=localization.get_available_languages(), command=self.change_language)
        self.language_optionmenu.set(localization.get_current_language_name())
        self.language_optionmenu.pack(anchor="w", padx=10, pady=5)

        # About Section
        about_frame = ctk.CTkFrame(self)
        about_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(about_frame, text=localization.get_text("About"), font=("Arial", 18, "bold")).pack(anchor="w", pady=5)
        about_text = localization.get_text("about_text")
        ctk.CTkLabel(about_frame, text=about_text, font=("Arial", 14), justify="left").pack(pady=5, padx=10, anchor="w")
        github_link = ctk.CTkLabel(about_frame, text=localization.get_text("github_repo"), text_color="cyan", cursor="hand2")
        github_link.pack(pady=5, padx=10, anchor="w")
        github_link.bind("<Button-1>", lambda e: actions.open_github())

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
        self.app.recreate_ui()

    def change_language(self, new_language_name):
        localization.set_language_by_name(new_language_name)
        self.app.recreate_ui()

    def cancel_updates(self):
        # This view has no scheduled updates
        pass
