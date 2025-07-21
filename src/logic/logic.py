# This file acts as a facade for the logic modules.
# The UI will import functions from this file.

from .info.system import (
    get_system_summary,
    get_local_ip,
    get_firewall_status,
    get_antivirus_info,
    get_windows_defender_status,
    get_uac_status,
    get_bitlocker_status,
    get_windows_defender_realtime_protection_status,
)

from .info.hardware import (
    get_cpu_usage,
    get_cpu_name,
    get_ram_usage,
    get_physical_disk_usage,
    get_network_io_counters,
    get_hardware_info,
    get_network_config,
    get_cpu_speed,
    get_public_ip,
    get_ping,
    get_cpu_speed,
    get_public_ip,
    get_ping,
    get_disk_io,
    get_cpu_temperature,
    get_ram_cache,
    get_system_qr_data,
    get_active_connections,
)

from .info.software import (
    get_installed_apps,
    get_startup_apps,
    set_startup_app_status,
    get_running_processes,
)

from .info.qr_code import (
    generate_qr_code_for_hardware_info,
)
