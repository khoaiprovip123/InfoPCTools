import customtkinter as ctk
from logic import localization
from .update_view import UpdateView

class UpdateSecurityView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")

        self.update_view = UpdateView(self)
        self.update_view.pack(expand=True, fill="both")

    def cancel_updates(self, *args, **kwargs):
        # Pass the cancel command to child views if they have it
        if hasattr(self.update_view, 'cancel_updates'):
            self.update_view.cancel_updates(*args, **kwargs)