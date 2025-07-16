using System.ComponentModel;
using System.Runtime.CompilerServices;
using InfoPCTools.Application.Services;
using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Presentation.ViewModels
{
    public class DashboardViewModel : INotifyPropertyChanged
    {
        private SystemInfo _systemInfo;
        private readonly ISystemInfoService _systemInfoService;

        public SystemInfo SystemInfo
        {
            get => _systemInfo;
            set
            {
                _systemInfo = value;
                OnPropertyChanged();
            }
        }

        public DashboardViewModel(ISystemInfoService systemInfoService)
        {
            _systemInfoService = systemInfoService;
            LoadSystemInfo();
        }

        private async Task LoadSystemInfo()
        {
            SystemInfo = await _systemInfoService.GetSystemInfoAsync();
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}