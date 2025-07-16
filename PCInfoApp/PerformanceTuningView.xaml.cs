using System.Windows.Controls;
using System.Windows;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for PerformanceTuningView.xaml
    /// </summary>
    public partial class PerformanceTuningView : UserControl
    {
        public PerformanceTuningView()
        {
            InitializeComponent();
        }

        private void EnableAutoOptimization_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng tự động tối ưu hóa chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void SetGamingProfile_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Hồ sơ chơi game chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void SetWorkProfile_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Hồ sơ làm việc chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void SetPowerSaveProfile_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Hồ sơ tiết kiệm năng lượng chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ManageBackgroundProcesses_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng quản lý tiến trình nền chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void OptimizePowerPlan_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng tối ưu hóa gói năng lượng chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}