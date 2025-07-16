using System.Windows.Controls;
using System.Windows;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for ReportingView.xaml
    /// </summary>
    public partial class ReportingView : UserControl
    {
        public ReportingView()
        {
            InitializeComponent();
        }

        private void GenerateSystemHealthReport_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tạo báo cáo sức khỏe hệ thống chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void GeneratePerformanceAnalysisReport_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tạo báo cáo phân tích hiệu suất chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void GenerateHardwareInventoryReport_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tạo báo cáo kiểm kê phần cứng chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void GenerateMaintenanceRecommendationsReport_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tạo báo cáo đề xuất bảo trì chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ExportToPdf_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Xuất sang PDF chưa được triển khai đầy đủ. Yêu cầu thư viện bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ExportToExcelCsv_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Xuất sang Excel/CSV chưa được triển khai đầy đủ. Yêu cầu thư viện bên ngoài.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void ScheduleReportGeneration_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Thiết lập lịch trình báo cáo chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void SetupEmailDelivery_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Thiết lập gửi báo cáo qua email chưa được triển khai đầy đủ.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}