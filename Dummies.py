import random
import time

# Dummy data and functions to mimic the real logic.py

def get_text(key):
    return key # Just return the key for simplicity

class logic:
    @staticmethod
    def get_cpu_usage():
        return random.uniform(10, 50)

    @staticmethod
    def get_cpu_name():
        return "12th Gen Intel(R) Core(TM) i5-12600K (3.70 GHz)"

    @staticmethod
    def get_ram_usage():
        total_gb = 16.0
        used_gb = random.uniform(4, 12)
        percent = (used_gb / total_gb) * 100
        return percent, f"{used_gb:.1f}/{total_gb:.1f} GB"

    @staticmethod
    def get_system_summary():
        return {
            'os': 'Windows 11 Pro',
            'hostname': 'DESKTOP-GEMINI',
            'uptime': '10 days, 5:30:01'
        }

    @staticmethod
    def get_local_ip():
        return "192.168.1.101"

    @staticmethod
    def get_network_io_counters():
        # Simulate increasing byte counts
        t = time.time() * 1000
        bytes_sent = t * 0.5 + random.randint(0, 1000)
        bytes_recv = t * 1.5 + random.randint(0, 1000)
        return bytes_recv, bytes_sent

    @staticmethod
    def get_disk_usage():
        return [
            {
                'device': 'C:',
                'fstype': 'NTFS',
                'total': 512 * (1024**3),
                'percent': random.uniform(40, 60)
            },
            {
                'device': 'D:',
                'fstype': 'NTFS',
                'total': 1024 * (1024**3),
                'percent': random.uniform(70, 85)
            }
        ]

class localization:
    @staticmethod
    def get_text(key):
        return key.replace("_", " ").title()