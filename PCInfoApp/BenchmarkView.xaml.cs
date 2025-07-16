using System.Windows.Controls;
using System.Windows;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for BenchmarkView.xaml
    /// </summary>
    public partial class BenchmarkView : UserControl
    {
        public BenchmarkView()
        {
            InitializeComponent();
        }

        private void CpuStressTest_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Kiểm tra căng thẳng CPU chưa được triển khai đầy đủ. Yêu cầu công cụ bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void RamSpeedTest_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Kiểm tra tốc độ RAM chưa được triển khai đầy đủ. Yêu cầu công cụ bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void DiskPerformanceTest_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Kiểm tra hiệu suất đĩa chưa được triển khai đầy đủ. Yêu cầu công cụ bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void GpuBenchmark_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Benchmark GPU chưa được triển khai đầy đủ. Yêu cầu công cụ bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ComparePerformance_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng so sánh hiệu suất chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void HistoricalPerformanceTrends_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng xu hướng hiệu suất lịch sử chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void TrackImprovements_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng theo dõi cải tiến chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}