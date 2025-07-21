import customtkinter as ctk
from logic import logic, localization

class NetworkView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.active_after_ids = {}

        config_frame = ctk.CTkFrame(self)
        config_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(config_frame, text=localization.get_text("Network Configuration"), font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        for config in logic.get_network_config():
            ctk.CTkLabel(config_frame, text=f"{localization.get_text('Interface')}: {config['interface']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(config_frame, text=f"  {localization.get_text('IP Address')}: {config['address']}").pack(anchor="w", padx=10)
            ctk.CTkLabel(config_frame, text=f"  {localization.get_text('Netmask')}: {config['netmask']}").pack(anchor="w", padx=10)

        connections_frame = ctk.CTkFrame(self)
        connections_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(connections_frame, text=localization.get_text("Active Network Connections"), font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        self.scrollable_connections = ctk.CTkScrollableFrame(connections_frame)
        self.scrollable_connections.pack(fill="both", expand=True)

        self.update_connections()

    def update_connections(self):
        for widget in self.scrollable_connections.winfo_children():
            widget.destroy()
        for conn_info in logic.get_active_connections():
            ctk.CTkLabel(self.scrollable_connections, text=conn_info).pack(anchor="w")
        self.active_after_ids["network_update"] = self.after(5000, self.update_connections)

    def cancel_updates(self):
        for after_id in self.active_after_ids.values():
            self.after_cancel(after_id)
        self.active_after_ids.clear()
