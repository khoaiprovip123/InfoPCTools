import qrcode
import platform
from . import hardware

def get_simplified_hardware_info(user_info: dict = None):
    info, error = hardware.get_hardware_info()
    if error:
        return None, error

    if not info:
        return None, "No hardware information available."

    simplified_info = {}

    if user_info:
        for key, value in user_info.items():
            if value:
                simplified_info[key] = value

    simplified_info.update({
        "PC Name": info["System"].get("Hostname", "N/A"),
        "CPU": info["CPU"].get("Name", "N/A"),
        "RAM": info["RAM"].get("Total", "N/A"),
        "WIN": f"{platform.system()} {platform.release()}",
        "Disk": "N/A",
        "GPU": "N/A",
        "MAC Address": "N/A",
        "Serial Number": info["System"].get("Serial Number", "N/A")
    })

    # Calculate total disk size
    total_disk_size_gb = 0
    for disk_name, disk_details in info["Storage"].items():
        size_str = disk_details.get("Size", "0 GB").replace(" GB", "")
        try:
            total_disk_size_gb += float(size_str)
        except ValueError:
            pass
    simplified_info["Disk"] = f"{total_disk_size_gb:.2f} GB"

    # Get GPU Name
    if info["GPU"]:
        simplified_info["GPU"] = ", ".join(info["GPU"].keys())

    # Get MAC Address
    if info["Network Adapters"]:
        for adapter, details in info["Network Adapters"].items():
            if details.get("MAC Address"):
                simplified_info["MAC Address"] = details["MAC Address"]
                break

    return simplified_info, None

def generate_qr_code_for_hardware_info(user_info: dict = None, download: bool = False):
    simplified_info, error = get_simplified_hardware_info(user_info)
    if error:
        return None, f"Error getting simplified hardware info: {error}"
    
    if simplified_info:
        try:
            # Add user info if it's for download
            if download and user_info:
                simplified_info["Full Name"] = user_info.get("Full Name", "N/A")
                simplified_info["Department"] = user_info.get("Department", "N/A")

            # Convert the dictionary to a formatted string for QR code
            qr_data = ""
            for key, value in simplified_info.items():
                qr_data += f"{key}: {value}\n"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10 if download else 5, # Larger box size for download
                border=4 if download else 2,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            return img, None
        except Exception as e:
            return None, f"Error generating QR code: {e}"
    return None, "No simplified hardware information to generate QR code."
