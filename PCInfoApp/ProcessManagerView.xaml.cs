using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Windows.Controls;
using System.Windows.Threading;
using Microsoft.Win32;

namespace PCInfoApp
{
    public partial class ProcessManagerView : UserControl
    {
        public ObservableCollection<ProcessInfo> Processes { get; set; }
        public ObservableCollection<StartupProgramInfo> StartupPrograms { get; set; }
        private DispatcherTimer _timer;

        public ProcessManagerView()
        {
            InitializeComponent();
            Processes = new ObservableCollection<ProcessInfo>();
            StartupPrograms = new ObservableCollection<StartupProgramInfo>();
            ProcessListView.ItemsSource = Processes;
            StartupProgramsListView.ItemsSource = StartupPrograms;

            _timer = new DispatcherTimer();
            _timer.Interval = TimeSpan.FromSeconds(1); // Update every 1 second
            _timer.Tick += Timer_Tick;
            _timer.Start();

            LoadProcesses();
            LoadStartupPrograms();
        }

        private void LoadProcesses()
        {
            Processes.Clear();
            foreach (Process process in Process.GetProcesses())
            {
                try
                {
                    // Get CPU usage (requires a bit more work for accurate real-time)
                    // For simplicity, we'll just get the current CPU time for now.
                    // A more accurate approach would involve PerformanceCounter.
                    double cpuUsage = 0; // Placeholder

                    // Get RAM usage
                    double ramUsageMB = process.WorkingSet64 / (1024.0 * 1024.0);

                    Processes.Add(new ProcessInfo
                    {
                        ProcessName = process.ProcessName,
                        Id = process.Id,
                        CpuUsage = cpuUsage,
                        RamUsageMB = ramUsageMB
                    });
                }
                catch (Exception) { /* Ignore processes that cannot be accessed */ }
            }
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            LoadProcesses(); // Reload processes to update data
        }

        private void KillProcess_Click(object sender, System.Windows.RoutedEventArgs e)
        {
            if (ProcessListView.SelectedItem is ProcessInfo selectedProcess)
            {
                try
                {
                    Process processToKill = Process.GetProcessById(selectedProcess.Id);
                    processToKill.Kill();
                    processToKill.WaitForExit(); // Wait for the process to exit
                    LoadProcesses(); // Refresh the list
                    System.Windows.MessageBox.Show($"Process {selectedProcess.ProcessName} (ID: {selectedProcess.Id}) killed successfully.", "Success", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    System.Windows.MessageBox.Show($"Failed to kill process {selectedProcess.ProcessName} (ID: {selectedProcess.Id}): {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                }
            }
            else
            {
                System.Windows.MessageBox.Show("Please select a process to kill.", "Warning", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
            }
        }

        private void ProcessListView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ProcessListView.SelectedItem is ProcessInfo selectedProcess)
            {
                try
                {
                    Process process = Process.GetProcessById(selectedProcess.Id);
                    string details = $"Process Name: {process.ProcessName}\n";
                    details += $"ID: {process.Id}\n";
                    details += $"Start Time: {process.StartTime}\n";
                    details += $"Total Processor Time: {process.TotalProcessorTime}\n";
                    details += $"Working Set: {process.WorkingSet64 / (1024.0 * 1024.0):F2} MB\n";
                    details += $"Threads: {process.Threads.Count}\n";
                    details += $"Base Priority: {process.BasePriority}\n";
                    details += $"File Name: {process.MainModule?.FileName ?? "N/A"}\n";

                    ProcessDetailsTextBlock.Text = details;
                }
                catch (Exception ex)
                {
                    ProcessDetailsTextBlock.Text = $"Error getting process details: {ex.Message}";
                }
            }
            else
            {
                ProcessDetailsTextBlock.Text = "Select a process to view details.";
            }
        }

        private void LoadStartupPrograms()
        {
            StartupPrograms.Clear();

            // Current User Run key
            using (RegistryKey key = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"))
            {
                if (key != null)
                {
                    foreach (string valueName in key.GetValueNames())
                    {
                        string path = key.GetValue(valueName)?.ToString() ?? "N/A";
                        StartupPrograms.Add(new StartupProgramInfo { Name = valueName, Path = path, Status = "Enabled" });
                    }
                }
            }

            // Local Machine Run key
            using (RegistryKey key = Registry.LocalMachine.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"))
            {
                if (key != null)
                {
                    foreach (string valueName in key.GetValueNames())
                    {
                        string path = key.GetValue(valueName)?.ToString() ?? "N/A";
                        StartupPrograms.Add(new StartupProgramInfo { Name = valueName, Path = path, Status = "Enabled" });
                    }
                }
            }

            // Add more registry locations or startup folders as needed
        }
    }

    public class ProcessInfo : INotifyPropertyChanged
    {
        private string _processName;
        private int _id;
        private double _cpuUsage;
        private double _ramUsageMB;

        public string ProcessName
        {
            get { return _processName; }
            set
            {
                _processName = value;
                OnPropertyChanged(nameof(ProcessName));
            }
        }

        public int Id
        {
            get { return _id; }
            set
            {
                _id = value;
                OnPropertyChanged(nameof(Id));
            }
        }

        public double CpuUsage
        {
            get { return _cpuUsage; }
            set
            {
                _cpuUsage = value;
                OnPropertyChanged(nameof(CpuUsage));
            }
        }

        public double RamUsageMB
        {
            get { return _ramUsageMB; }
            set
            {
                _ramUsageMB = value;
                OnPropertyChanged(nameof(RamUsageMB));
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public class StartupProgramInfo : INotifyPropertyChanged
    {
        private string _name;
        private string _path;
        private string _status;

        public string Name
        {
            get { return _name; }
            set
            {
                _name = value;
                OnPropertyChanged(nameof(Name));
            }
        }

        public string Path
        {
            get { return _path; }
            set
            {
                _path = value;
                OnPropertyChanged(nameof(Path));
            }
        }

        public string Status
        {
            get { return _status; }
            set
            {
                _status = value;
                OnPropertyChanged(nameof(Status));
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}