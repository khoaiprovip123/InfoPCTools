using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace InfoPCTools.Presentation.ViewModels
{
    public class BackupInfoViewModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }
}