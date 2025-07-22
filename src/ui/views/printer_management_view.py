import customtkinter as ctk
from logic import actions, localization

class PrinterManagementView(ctk.CTkFrame):
    STYLE = {
        "font_info": ("Roboto", 11),
        "font_info_bold": ("Roboto", 11, "bold"),
    }

    def _set_colors(self):
        if ctk.get_appearance_mode() == "Dark":
            self.text_color = "#F8F8F2"
            self.card_fg_color = "#282C34"
        else:
            self.text_color = "#23272E"
            self.card_fg_color = "#FFFFFF"

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._set_colors()
        self.configure(fg_color=self.card_fg_color)

        self.grid_columnconfigure(0, weight=1) # Function Name
        self.grid_columnconfigure(1, weight=3) # Description
        self.grid_columnconfigure(2, weight=1) # Action Button

        # Header Row
        ctk.CTkLabel(self, text=localization.get_text("Function Name"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self, text=localization.get_text("Description"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ctk.CTkLabel(self, text=localization.get_text("Action"), font=self.STYLE["font_info_bold"], anchor="w", text_color=self.text_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        printer_options = [
            (localization.get_text("Add a Printer"), "add_printer_desc", actions.install_printer, "Run"),
            (localization.get_text("Remove a Printer"), "remove_printer_desc", actions.delete_printer, "Run"),
            (localization.get_text("Troubleshoot Printer"), "troubleshoot_printer_desc", actions.fix_printer, "Run"),
            (localization.get_text("Open Print Management"), "open_print_management_desc", actions.open_print_management, "Open"),
        ]

        for i, (text, desc_key, command, button_text) in enumerate(printer_options):
            row_num = i + 1 # Start from row 1 after header

            ctk.CTkLabel(
                self,
                text=text,
                font=self.STYLE["font_info"],
                anchor="w",
                text_color=self.text_color
            ).grid(row=row_num, column=0, sticky="nw", padx=(5, 10), pady=2)

            ctk.CTkLabel(
                self,
                text=localization.get_text(desc_key),
                font=self.STYLE["font_info"],
                anchor="w",
                wraplength=300,
                justify="left",
                text_color=self.text_color
            ).grid(row=row_num, column=1, sticky="ew", padx=(0, 5), pady=2)

            action_button = ctk.CTkButton(
                self,
                text=localization.get_text(button_text),
                command=command,
                font=self.STYLE["font_info"],
                width=80
            )
            action_button.grid(row=row_num, column=2, sticky="nsew", padx=5, pady=2)

    def cancel_updates(self, *args, **kwargs):
        pass
