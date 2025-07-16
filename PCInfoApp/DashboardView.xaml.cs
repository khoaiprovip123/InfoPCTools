using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Net.NetworkInformation;
using System.Media;
using System.Windows.Controls;
using System.Windows.Threading;
using LiveCharts.Defaults;
using Notifications.Wpf;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for DashboardView.xaml
    /// </summary>
    public partial class DashboardView : UserControl, INotifyPropertyChanged
    {
        private ObservableCollection<double> _cpuValues;
        private ObservableCollection<double> _ramValues;
        private ObservableCollection<double> _diskValues;
        private ObservableCollection<double> _cpuTempValues;
        private ObservableCollection<double> _gpuTempValues;
        private ObservableCollection<double> _uploadValues;
        private ObservableCollection<double> _downloadValues;
        private string[] _labels;
        private Func<double, string> _formatter;
        private Func<double, string> _tempFormatter;
        private Func<double, string> _networkFormatter;

        private PerformanceCounter _cpuCounter;
        private PerformanceCounter _ramCounter;
        private PerformanceCounter _diskCounter;
        private PerformanceCounter _cpuTempCounter; 
        private PerformanceCounter _gpuTempCounter; 
        private PerformanceCounter _uploadCounter;
        private PerformanceCounter _downloadCounter;
        private DispatcherTimer _timer;

        private DateTime _lastCpuAlertTime = DateTime.MinValue;
        private DateTime _lastRamAlertTime = DateTime.MinValue;
        private DateTime _lastDiskAlertTime = DateTime.MinValue;
        private DateTime _lastCpuTempAlertTime = DateTime.MinValue;
        private DateTime _lastGpuTempAlertTime = DateTime.MinValue;
        private readonly TimeSpan _alertInterval = TimeSpan.FromMinutes(5);

        public double CpuTempThreshold { get; set; } = 70; // Default threshold
        public double GpuTempThreshold { get; set; } = 75; // Default threshold

        public double CpuUsageThreshold { get; set; } = 80; // Default threshold
        public double RamUsageThreshold { get; set; } = 85; // Default threshold
        public double DiskUsageThreshold { get; set; } = 90; // Default threshold

        private System.Windows.Media.SolidColorBrush _cpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#EF4444");
        private System.Windows.Media.SolidColorBrush _gpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#F59E0B");

        public System.Windows.Media.SolidColorBrush CpuTempColor
        {
            get { return _cpuTempColor; }
            set
            {
                _cpuTempColor = value;
                OnPropertyChanged(nameof(CpuTempColor));
            }
        }

        public System.Windows.Media.SolidColorBrush GpuTempColor
        {
            get { return _gpuTempColor; }
            set
            {
                _gpuTempColor = value;
                OnPropertyChanged(nameof(GpuTempColor));
            }
        }

        private System.Windows.Media.SolidColorBrush _cpuUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#2563EB");
        private System.Windows.Media.SolidColorBrush _ramUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#10B981");
        private System.Windows.Media.SolidColorBrush _diskUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FFC107");

        public System.Windows.Media.SolidColorBrush CpuUsageColor
        {
            get { return _cpuUsageColor; }
            set
            {
                _cpuUsageColor = value;
                OnPropertyChanged(nameof(CpuUsageColor));
            }
        }

        public System.Windows.Media.SolidColorBrush RamUsageColor
        {
            get { return _ramUsageColor; }
            set
            {
                _ramUsageColor = value;
                OnPropertyChanged(nameof(RamUsageColor));
            }
        }

        public System.Windows.Media.SolidColorBrush DiskUsageColor
        {
            get { return _diskUsageColor; }
            set
            {
                _diskUsageColor = value;
                OnPropertyChanged(nameof(DiskUsageColor));
            }
        }

        public DashboardView()
        {
            InitializeComponent();

            _cpuValues = new ObservableCollection<double>();
            _ramValues = new ObservableCollection<double>();
            _diskValues = new ObservableCollection<double>();
            _cpuTempValues = new ObservableCollection<double>();
            _gpuTempValues = new ObservableCollection<double>();
            _uploadValues = new ObservableCollection<double>();
            _downloadValues = new ObservableCollection<double>();
            _labels = new string[10]; // Display last 10 seconds/minutes
            _formatter = value => value.ToString("N0") + "%";
            _tempFormatter = value => value.ToString("N0") + "°C";
            _networkFormatter = value => value.ToString("N2") + " KB/s";

            // Initialize Performance Counters
            _cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
            _ramCounter = new PerformanceCounter("Memory", "% Committed Bytes In Use");
            _diskCounter = new PerformanceCounter("PhysicalDisk", "% Disk Time", "_Total");

            // Attempt to initialize CPU Temperature Counter (often not available via PerformanceCounter)
            try
            {
                _cpuTempCounter = new PerformanceCounter("Thermal Zone Information", "_CurrentTemperature", "\\_SB.PCI0.LPCB.EC0.THRM"); // Example path, highly system-dependent
            }
            catch (Exception) { /* Counter not found, will use dummy data or indicate error */ }

            // GPU Temperature is almost never available via PerformanceCounter. Requires external libraries.
            // For now, we'll use dummy data.

            // Initialize Network Performance Counters
            string networkInterfaceName = GetActiveNetworkInterfaceName();
            if (!string.IsNullOrEmpty(networkInterfaceName))
            {
                _uploadCounter = new PerformanceCounter("Network Interface", "Bytes Sent/sec", networkInterfaceName);
                _downloadCounter = new PerformanceCounter("Network Interface", "Bytes Received/sec", networkInterfaceName);
            }
            else
            {
                // Handle case where no active network interface is found
                _uploadCounter = null;
                _downloadCounter = null;
            }

            // Initialize and start timer
            _timer = new DispatcherTimer();
            _timer.Interval = TimeSpan.FromSeconds(1); // Update every 1 second
            _timer.Tick += Timer_Tick;
            _timer.Start();

            // Set initial values
            for (int i = 0; i < 10; i++)
            {
                _cpuValues.Add(0);
                _ramValues.Add(0);
                _diskValues.Add(0);
                _cpuTempValues.Add(0);
                _gpuTempValues.Add(0);
                _uploadValues.Add(0);
                _downloadValues.Add(0);
                _labels[i] = ""; // Empty labels initially
            }

            DataContext = this;
        }

        public ObservableCollection<double> CpuValues
        {
            get { return _cpuValues; }
            set
            {
                _cpuValues = value;
                OnPropertyChanged(nameof(CpuValues));
            }
        }

        public ObservableCollection<double> RamValues
        {
            get { return _ramValues; }
            set
            {
                _ramValues = value;
                OnPropertyChanged(nameof(RamValues));
            }
        }

        public ObservableCollection<double> DiskValues
        {
            get { return _diskValues; }
            set
            {
                _diskValues = value;
                OnPropertyChanged(nameof(DiskValues));
            }
        }

        public ObservableCollection<double> CpuTempValues
        {
            get { return _cpuTempValues; }
            set
            {
                _cpuTempValues = value;
                OnPropertyChanged(nameof(CpuTempValues));
            }
        }

        public ObservableCollection<double> GpuTempValues
        {
            get { return _gpuTempValues; }
            set
            {
                _gpuTempValues = value;
                OnPropertyChanged(nameof(GpuTempValues));
            }
        }

        public ObservableCollection<double> UploadValues
        {
            get { return _uploadValues; }
            set
            {
                _uploadValues = value;
                OnPropertyChanged(nameof(UploadValues));
            }
        }

        public ObservableCollection<double> DownloadValues
        {
            get { return _downloadValues; }
            set
            {
                _downloadValues = value;
                OnPropertyChanged(nameof(DownloadValues));
            }
        }

        public string[] Labels
        {
            get { return _labels; }
            set
            {
                _labels = value;
                OnPropertyChanged(nameof(Labels));
            }
        }

        public Func<double, string> Formatter
        {
            get { return _formatter; }
            set
            {
                _formatter = value;
                OnPropertyChanged(nameof(Formatter));
            }
        }

        public Func<double, string> TempFormatter
        {
            get { return _tempFormatter; }
            set
            {
                _tempFormatter = value;
                OnPropertyChanged(nameof(TempFormatter));
            }
        }

        public Func<double, string> NetworkFormatter
        {
            get { return _networkFormatter; }
            set
            {
                _networkFormatter = value;
                OnPropertyChanged(nameof(NetworkFormatter));
            }
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            // Get current usage values
            double cpuUsage = _cpuCounter.NextValue();
            double ramUsage = _ramCounter.NextValue();
            double diskActivity = _diskCounter.NextValue();

            // Check CPU Usage Threshold
            if (cpuUsage > CpuUsageThreshold)
            {
                CpuUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FF0000"); // Red for warning
                if (DateTime.Now - _lastCpuAlertTime > _alertInterval)
                {
                    ShowToastNotification("Cảnh báo CPU", $"Sử dụng CPU cao: {cpuUsage:N0}%!");
                    _lastCpuAlertTime = DateTime.Now;
                }
            }
            else
            {
                CpuUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#2563EB"); // Original color
            }

            // Check RAM Usage Threshold
            if (ramUsage > RamUsageThreshold)
            {
                RamUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FF0000"); // Red for warning
                if (DateTime.Now - _lastRamAlertTime > _alertInterval)
                {
                    ShowToastNotification("Cảnh báo RAM", $"Sử dụng RAM cao: {ramUsage:N0}%!");
                    _lastRamAlertTime = DateTime.Now;
                }
            }
            else
            {
                RamUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#10B981"); // Original color
            }

            // Check Disk Usage Threshold
            if (diskActivity > DiskUsageThreshold)
            {
                DiskUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FF0000"); // Red for warning
                if (DateTime.Now - _lastDiskAlertTime > _alertInterval)
                {
                    ShowToastNotification("Cảnh báo Đĩa", $"Sử dụng Đĩa cao: {diskActivity:N0}%!");
                    _lastDiskAlertTime = DateTime.Now;
                }
            }
            else
            {
                DiskUsageColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FFC107"); // Original color
            }

            // Get current temperature values
            double cpuTemp = 0;
            if (_cpuTempCounter != null) { try { cpuTemp = (_cpuTempCounter.NextValue() - 273.15); } catch { /* ignore */ } } // Convert Kelvin to Celsius
            double gpuTemp = 0; // Dummy data for GPU temp, as it's hard to get via PerformanceCounter

            // Check CPU Temperature Threshold
            if (cpuTemp > CpuTempThreshold)
            {
                CpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FF0000"); // Red for warning
                if (DateTime.Now - _lastCpuTempAlertTime > _alertInterval)
                {
                    ShowToastNotification("Cảnh báo Nhiệt độ CPU", $"Nhiệt độ CPU cao: {cpuTemp:N0}°C!");
                    _lastCpuTempAlertTime = DateTime.Now;
                }
            }
            else
            {
                CpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#EF4444"); // Original color
            }

            // Check GPU Temperature Threshold
            if (gpuTemp > GpuTempThreshold)
            {
                GpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#FF0000"); // Red for warning
                if (DateTime.Now - _lastGpuTempAlertTime > _alertInterval)
                {
                    ShowToastNotification("Cảnh báo Nhiệt độ GPU", $"Nhiệt độ GPU cao: {gpuTemp:N0}°C!");
                    _lastGpuTempAlertTime = DateTime.Now;
                }
            }
            else
            {
                GpuTempColor = (System.Windows.Media.SolidColorBrush)new System.Windows.Media.BrushConverter().ConvertFromString("#F59E0B"); // Original color
            }

            // Get current network values
            double uploadSpeed = 0;
            double downloadSpeed = 0;
            if (_uploadCounter != null) { try { uploadSpeed = _uploadCounter.NextValue() / 1024; } catch { /* ignore */ } } // Convert bytes/sec to KB/sec
            if (_downloadCounter != null) { try { downloadSpeed = _downloadCounter.NextValue() / 1024; } catch { /* ignore */ } } // Convert bytes/sec to KB/sec

            // Add new values and remove old ones
            CpuValues.Add(cpuUsage);
            RamValues.Add(ramUsage);
            DiskValues.Add(diskActivity);
            CpuTempValues.Add(cpuTemp);
            GpuTempValues.Add(gpuTemp);
            UploadValues.Add(uploadSpeed);
            DownloadValues.Add(downloadSpeed);

            if (CpuValues.Count > 10) CpuValues.RemoveAt(0);
            if (RamValues.Count > 10) RamValues.RemoveAt(0);
            if (DiskValues.Count > 10) DiskValues.RemoveAt(0);
            if (CpuTempValues.Count > 10) CpuTempValues.RemoveAt(0);
            if (GpuTempValues.Count > 10) GpuTempValues.RemoveAt(0);
            if (UploadValues.Count > 10) UploadValues.RemoveAt(0);
            if (DownloadValues.Count > 10) DownloadValues.RemoveAt(0);

            // Update labels (e.g., current time)
            for (int i = 0; i < Labels.Length; i++)
            {
                if (i == Labels.Length - 1)
                {
                    Labels[i] = DateTime.Now.ToString("HH:mm:ss");
                }
                else
                {
                    Labels[i] = ""; // Clear previous labels
                }
            }
            OnPropertyChanged(nameof(Labels)); // Notify Labels changed
        }

        private string GetActiveNetworkInterfaceName()
        {
            foreach (NetworkInterface ni in NetworkInterface.GetAllNetworkInterfaces())
            {
                // Consider only operational Ethernet or Wireless interfaces
                if (ni.OperationalStatus == OperationalStatus.Up &&
                    (ni.NetworkInterfaceType == NetworkInterfaceType.Ethernet ||
                     ni.NetworkInterfaceType == NetworkInterfaceType.Wireless80211))
                {
                    // Exclude virtual or loopback adapters
                    if (!ni.Description.ToLower().Contains("virtual") &&
                        !ni.Description.ToLower().Contains("loopback"))
                    {
                        return ni.Description; // Or ni.Name, depending on what PerformanceCounter expects
                    }
                }
            }
            return null;
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private void ShowToastNotification(string title, string message)
        {
            var notificationManager = new NotificationManager();
            notificationManager.Show(new NotificationContent
            {
                Title = title,
                Message = message,
                Type = NotificationType.Information // Can be Information, Success, Warning, Error
            });
        }
    }
}