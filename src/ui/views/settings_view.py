import customtkinter as ctk
from logic import actions, localization

class SettingsView(ctk.CTkFrame):
    STYLE = {
        "font_family": "Roboto",
        "font_title": ("Roboto", 24, "bold"),
        "font_card_header": ("Roboto", 14, "bold"),
        "font_info": ("Roboto", 11),
        "font_info_bold": ("Roboto", 11, "bold"),
    }

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
            self.border_color = "#5C6370"
            self.hover_color = "#3E3E3E"
            self.tab_text_color = "#FFD700"
            self.tab_selected_text_color = "#00BFFF"
            self.segmented_button_unselected_color = "#44475a"
            self.segmented_button_selected_color = "#00BFFF"
            self.status_ok_color = "#50FA7B"
            self.status_bad_color = "#FF5555"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"
            self.border_color = "#DCE4EE"
            self.hover_color = "#CFCFCF"
            self.tab_text_color = "#FF8C00"
            self.tab_selected_text_color = "#0078D7"
            self.segmented_button_unselected_color = "#F0F0F0"
            self.segmented_button_selected_color = "#0078D7"
            self.status_ok_color = "#28A745"
            self.status_bad_color = "#DC3545"

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self._set_colors()
        self.configure(fg_color="transparent")

        ctk.CTkLabel(self, text=localization.get_text("Settings"), font=self.STYLE["font_title"], text_color=self.text_color).pack(pady=10)

        # Application Info
        app_info_frame = ctk.CTkFrame(self, fg_color=self.card_fg_color)
        app_info_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Application Information"), font=self.STYLE["font_card_header"], text_color=self.text_color).pack(anchor="w", pady=5)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("app_info_desc"), font=self.STYLE["font_info"], text_color=self.text_color, wraplength=400, justify="left").pack(anchor="w", padx=10)
        ctk.CTkLabel(app_info_frame, text=f"{localization.get_text('Version')}: 1.1", text_color=self.text_color).pack(anchor="w", padx=10)
        ctk.CTkLabel(app_info_frame, text=localization.get_text("Developed by Gemini AI from Google."), text_color=self.text_color).pack(anchor="w", padx=10)

        # Theme Settings
        theme_frame = ctk.CTkFrame(self, fg_color=self.card_fg_color)
        theme_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(theme_frame, text=localization.get_text("Theme Settings"), font=self.STYLE["font_card_header"], text_color=self.text_color).pack(anchor="w", pady=5)
        ctk.CTkLabel(theme_frame, text=localization.get_text("theme_settings_desc"), font=self.STYLE["font_info"], text_color=self.text_color, wraplength=400, justify="left").pack(anchor="w", padx=10)
        self.theme_switch = ctk.CTkSwitch(theme_frame, text=localization.get_text("Dark Mode"), command=self.toggle_theme)
        self.theme_switch.pack(anchor="w", padx=10, pady=5)
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()

        # Language Settings
        lang_frame = ctk.CTkFrame(self, fg_color=self.card_fg_color)
        lang_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(lang_frame, text=localization.get_text("Language Settings"), font=self.STYLE["font_card_header"], text_color=self.text_color).pack(anchor="w", pady=5)
        ctk.CTkLabel(lang_frame, text=localization.get_text("language_settings_desc"), font=self.STYLE["font_info"], text_color=self.text_color, wraplength=400, justify="left").pack(anchor="w", padx=10)
        self.language_optionmenu = ctk.CTkOptionMenu(lang_frame, values=localization.get_available_languages(), command=self.change_language)
        self.language_optionmenu.set(localization.get_current_language_name())
        self.language_optionmenu.pack(anchor="w", padx=10, pady=5)

        # About Section
        about_frame = ctk.CTkFrame(self, fg_color=self.card_fg_color)
        about_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(about_frame, text=localization.get_text("About"), font=self.STYLE["font_card_header"], text_color=self.text_color).pack(anchor="w", pady=5)
        ctk.CTkLabel(about_frame, text=localization.get_text("about_desc"), font=self.STYLE["font_info"], text_color=self.text_color, wraplength=400, justify="left").pack(anchor="w", padx=10)
        about_text = localization.get_text("about_text")
        ctk.CTkLabel(about_frame, text=about_text, font=("Arial", 14), justify="left", text_color=self.text_color).pack(pady=5, padx=10, anchor="w")
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

    def cancel_updates(self, *args, **kwargs):
        # This view has no scheduled updates
        pass