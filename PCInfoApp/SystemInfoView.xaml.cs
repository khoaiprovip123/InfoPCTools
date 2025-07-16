using System;
using System.Management;
using System.Windows;
using System.Windows.Controls;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for SystemInfoView.xaml
    /// </summary>
    public partial class SystemInfoView : UserControl
    {
        public SystemInfoView()
        {
            InitializeComponent();
            LoadSystemInformation();
        }

        private void LoadSystemInformation()
        {
            GetCpuInfo();
            GetRamInfo();
            GetDiskInfo();
            GetOsInfo();
        }

        private void GetCpuInfo()
        {
            try
            {
                ManagementObjectSearcher searcher = new ManagementObjectSearcher("select * from Win32_Processor");
                foreach (ManagementObject mo in searcher.Get())
                {
                    CpuNameTextBlock.Text = $"Name: {mo["Name"]}";
                    CpuArchitectureTextBlock.Text = $"Architecture: {GetProcessorArchitecture(mo["Architecture"])}";
                    CpuSocketTextBlock.Text = $"Socket: {mo["SocketDesignation"]}";
                    CpuCoresTextBlock.Text = $"Cores: {mo["NumberOfCores"]}";
                    CpuThreadsTextBlock.Text = $"Logical Processors: {mo["NumberOfLogicalProcessors"]}";
                    CpuBaseClockTextBlock.Text = $"Base Clock: {mo["CurrentClockSpeed"]} MHz";
                    CpuBoostClockTextBlock.Text = $"Max Clock: {mo["MaxClockSpeed"]} MHz";

                    string cacheInfo = "";
                    if (mo["L2CacheSize"] != null) cacheInfo += $"L2 Cache: {mo["L2CacheSize"]} KB ";
                    if (mo["L3CacheSize"] != null) cacheInfo += $"L3 Cache: {mo["L3CacheSize"]} KB";
                    CpuCacheTextBlock.Text = $"Cache: {cacheInfo.Trim()}";

                    // Instruction sets are not directly available via Win32_Processor in a simple string format.
                    // This would require more complex WMI queries or external libraries.
                    CpuInstructionSetsTextBlock.Text = "Instruction Sets: N/A (Complex to retrieve)";

                    break; // Assuming one CPU for simplicity
                }
            }
            catch (Exception ex)
            {
                CpuNameTextBlock.Text = $"Error getting CPU info: {ex.Message}";
                CpuArchitectureTextBlock.Text = "Architecture: Error";
                CpuSocketTextBlock.Text = "Socket: Error";
                CpuCoresTextBlock.Text = "Cores: Error";
                CpuThreadsTextBlock.Text = "Logical Processors: Error";
                CpuBaseClockTextBlock.Text = "Base Clock: Error";
                CpuBoostClockTextBlock.Text = "Max Clock: Error";
                CpuCacheTextBlock.Text = "Cache: Error";
                CpuInstructionSetsTextBlock.Text = "Instruction Sets: Error";
            }
        }

        private string GetProcessorArchitecture(object architectureValue)
        {
            if (architectureValue == null) return "Unknown";
            ushort architecture = (ushort)architectureValue;
            switch (architecture)
            {
                case 0: return "x86";
                case 1: return "MIPS";
                case 2: return "Alpha";
                case 3: return "PowerPC";
                case 5: return "ARM";
                case 6: return "ia64";
                case 9: return "x64";
                case 12: return "ARM64";
                default: return "Unknown";
            }
        }

        private void GetRamInfo()
        {
            try
            {
                // Get total physical memory
                ManagementObjectSearcher searcher = new ManagementObjectSearcher("select * from Win32_ComputerSystem");
                foreach (ManagementObject mo in searcher.Get())
                {
                    ulong totalRamBytes = (ulong)mo["TotalPhysicalMemory"];
                    RamTotalTextBlock.Text = $"Total RAM: {(totalRamBytes / (1024.0 * 1024 * 1024)):F2} GB";
                    break;
                }

                // Get available physical memory
                searcher = new ManagementObjectSearcher("select * from Win32_OperatingSystem");
                foreach (ManagementObject mo in searcher.Get())
                {
                    ulong freeRamBytes = (ulong)mo["FreePhysicalMemory"] * 1024; // FreePhysicalMemory is in KB
                    RamAvailableTextBlock.Text = $"Available RAM: {(freeRamBytes / (1024.0 * 1024 * 1024)):F2} GB";
                    ulong totalVirtualMemory = (ulong)mo["TotalVirtualMemorySize"] * 1024; // in bytes
                    ulong freeVirtualMemory = (ulong)mo["FreeVirtualMemory"] * 1024; // in bytes
                    RamVirtualMemoryTextBlock.Text = $"Virtual Memory: {(totalVirtualMemory - freeVirtualMemory) / (1024.0 * 1024 * 1024):F2} GB used of {totalVirtualMemory / (1024.0 * 1024 * 1024):F2} GB";
                    break;
                }

                // Get detailed memory module information
                searcher = new ManagementObjectSearcher("select * from Win32_PhysicalMemory");
                string speed = "", formFactor = "", manufacturer = "", partNumber = "";
                foreach (ManagementObject mo in searcher.Get())
                {
                    if (mo["Speed"] != null) speed += $"{mo["Speed"]} MT/s ";
                    if (mo["FormFactor"] != null) formFactor += $"{GetFormFactor(mo["FormFactor"])} ";
                    if (mo["Manufacturer"] != null) manufacturer += $"{mo["Manufacturer"]} ";
                    if (mo["PartNumber"] != null) partNumber += $"{mo["PartNumber"]} ";
                }
                RamSpeedTextBlock.Text = $"Speed: {speed.Trim()}";
                RamFormFactorTextBlock.Text = $"Form Factor: {formFactor.Trim()}";
                RamManufacturerTextBlock.Text = $"Manufacturer: {manufacturer.Trim()}";
                RamPartNumberTextBlock.Text = $"Part Number: {partNumber.Trim()}";
            }
            catch (Exception ex)
            {
                RamTotalTextBlock.Text = $"Error getting RAM info: {ex.Message}";
                RamAvailableTextBlock.Text = "Available RAM: Error";
                RamSpeedTextBlock.Text = "Speed: Error";
                RamFormFactorTextBlock.Text = "Form Factor: Error";
                RamManufacturerTextBlock.Text = "Manufacturer: Error";
                RamPartNumberTextBlock.Text = "Part Number: Error";
                RamVirtualMemoryTextBlock.Text = "Virtual Memory: Error";
            }
        }

        private string GetFormFactor(object formFactorValue)
        {
            if (formFactorValue == null) return "Unknown";
            ushort formFactor = (ushort)formFactorValue;
            switch (formFactor)
            {
                case 1: return "Other";
                case 2: return "SIP";
                case 3: return "DIP";
                case 4: return "ZIP";
                case 5: return "SOJ";
                case 6: return "Proprietary";
                case 7: return "SIMM";
                case 8: return "DIMM";
                case 9: return "TSOP";
                case 10: return "PGA";
                case 11: return "RIMM";
                case 12: return "SODIMM";
                case 13: return "SRIMM";
                case 14: return "FB-DIMM";
                default: return "Unknown";
            }
        }

        private void GetDiskInfo()
        {
            try
            {
                DiskInfoPanel.Children.Clear(); // Clear previous entries

                ManagementObjectSearcher diskSearcher = new ManagementObjectSearcher("select * from Win32_DiskDrive");
                foreach (ManagementObject diskMo in diskSearcher.Get())
                {
                    string model = diskMo["Model"]?.ToString() ?? "Unknown Model";
                    string mediaType = GetMediaType(diskMo["MediaType"]);

                    StackPanel diskPanel = new StackPanel { Margin = new Thickness(0, 0, 0, 10) };
                    diskPanel.Children.Add(new TextBlock { Text = $"Drive: {model} ({mediaType})", Style = (Style)FindResource("InfoTextStyle") });

                    // Get logical disks associated with this physical disk
                    ManagementObjectSearcher partitionSearcher = new ManagementObjectSearcher($"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID=\"{diskMo["DeviceID"]}\"}} WHERE AssocClass = Win32_DiskDriveToDiskPartition");
                    foreach (ManagementObject partitionMo in partitionSearcher.Get())
                    {
                        ManagementObjectSearcher logicalDiskSearcher = new ManagementObjectSearcher($"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID=\"{partitionMo["DeviceID"]}\"}} WHERE AssocClass = Win32_LogicalDiskToPartition");
                        foreach (ManagementObject logicalDiskMo in logicalDiskSearcher.Get())
                        {
                            string driveLetter = logicalDiskMo["DeviceID"]?.ToString() ?? "N/A";
                            ulong totalSize = (ulong?)logicalDiskMo["Size"] ?? 0;
                            ulong freeSpace = (ulong?)logicalDiskMo["FreeSpace"] ?? 0;

                            double totalGB = totalSize / (1024.0 * 1024 * 1024);
                            double freeGB = freeSpace / (1024.0 * 1024 * 1024);

                            diskPanel.Children.Add(new TextBlock { Text = $"  Partition {driveLetter}: {totalGB:F2} GB Total, {freeGB:F2} GB Free", Style = (Style)FindResource("SmallTextStyle") });
                        }
                    }

                    diskPanel.Children.Add(new TextBlock { Text = "  SMART Status: Not readily available via WMI", Style = (Style)FindResource("SmallTextStyle") });
                    diskPanel.Children.Add(new TextBlock { Text = "  Read/Write Speeds: Complex to retrieve via WMI", Style = (Style)FindResource("SmallTextStyle") });
                    diskPanel.Children.Add(new TextBlock { Text = "  Fragmentation: Requires defragmentation tool integration", Style = (Style)FindResource("SmallTextStyle") });

                    DiskInfoPanel.Children.Add(diskPanel);
                }
            }
            catch (Exception ex)
            {
                TextBlock errorTextBlock = new TextBlock { Text = $"Error getting Disk info: {ex.Message}", Style = (Style)FindResource("InfoTextStyle") };
                DiskInfoPanel.Children.Add(errorTextBlock);
            }
        }

        private string GetMediaType(object mediaTypeValue)
        {
            if (mediaTypeValue == null) return "Unknown";
            ushort mediaType = (ushort)mediaTypeValue;
            switch (mediaType)
            {
                case 0: return "Unknown";
                case 1: return "Other";
                case 3: return "HDD"; // Fixed hard disk media
                case 4: return "SSD"; // Solid state disk media
                // Add more cases as needed based on Win32_DiskDrive MediaType values
                default: return "Other";
            }
        }

        private void GetOsInfo()
        {
            try
            {
                ManagementObjectSearcher searcher = new ManagementObjectSearcher("select * from Win32_OperatingSystem");
                foreach (ManagementObject mo in searcher.Get())
                {
                    OsNameTextBlock.Text = $"OS Name: {mo["Caption"]}";
                    OsVersionTextBlock.Text = $"Version: {mo["Version"]}";
                    OsArchitectureTextBlock.Text = $"Architecture: {mo["OSArchitecture"]}";

                    // Get system uptime
                    TimeSpan uptime = TimeSpan.FromMilliseconds(Environment.TickCount);
                    SystemUptimeTextBlock.Text = $"System Uptime: {uptime.Days} days, {uptime.Hours} hours, {uptime.Minutes} minutes";
                    break;
                }
            }
            catch (Exception ex)
            {
                OsNameTextBlock.Text = $"Error getting OS info: {ex.Message}";
            }
        }
    }
}