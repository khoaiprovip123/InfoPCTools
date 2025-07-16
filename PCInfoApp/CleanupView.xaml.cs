using System;
using System.IO;
using System.Windows.Controls;
using System.Windows;

namespace PCInfoApp
{
    /// <summary>
    /// Interaction logic for CleanupView.xaml
    /// </summary>
    public partial class CleanupView : UserControl
    {
        public CleanupView()
        {
            InitializeComponent();
        }

        private void StartCleanup_Click(object sender, RoutedEventArgs e)
        {
            CleanupStatusTextBlock.Text = "Đang dọn dẹp...";

            if (TempFilesCheckBox.IsChecked == true)
            {
                CleanupTemporaryFiles();
            }

            if (CacheFilesCheckBox.IsChecked == true)
            {
                CleanupCacheFiles();
            }

            if (RecycleBinCheckBox.IsChecked == true)
            {
                CleanupRecycleBin();
            }

            CleanupStatusTextBlock.Text = "Dọn dẹp hoàn tất!";
        }

        private void CleanupTemporaryFiles()
        {
            try
            {
                string tempPath = Path.GetTempPath();
                DirectoryInfo di = new DirectoryInfo(tempPath);
                foreach (FileInfo file in di.GetFiles())
                {
                    try { file.Delete(); } catch (Exception) { /* Ignore errors */ }
                }
                foreach (DirectoryInfo dir in di.GetDirectories())
                {
                    try { dir.Delete(true); } catch (Exception) { /* Ignore errors */ }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi khi dọn dẹp tệp tạm thời: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CleanupCacheFiles()
        {
            // This is a simplified example. Real cache cleanup is more complex and application-specific.
            // For example, browser caches, Windows Update cache, etc.
            // For now, we'll just target a common temporary internet files location.
            try
            {
                string internetCachePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.InternetCache));
                if (Directory.Exists(internetCachePath))
                {
                    DirectoryInfo di = new DirectoryInfo(internetCachePath);
                    foreach (FileInfo file in di.GetFiles())
                    {
                        try { file.Delete(); } catch (Exception) { /* Ignore errors */ }
                    }
                    foreach (DirectoryInfo dir in di.GetDirectories())
                    {
                        try { dir.Delete(true); } catch (Exception) { /* Ignore errors */ }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi khi dọn dẹp tệp bộ nhớ cache: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CleanupRecycleBin()
        {
            try
            {
                // Requires Microsoft.VisualBasic.dll reference for FileSystem.RecycleBin.Empty()
                // For simplicity, we'll use Shell32.dll via COM Interop, which is more complex.
                // A simpler approach for .NET Core/.NET 5+ is to use P/Invoke with SHEmptyRecycleBin.

                // For now, we'll just show a message indicating it's not implemented directly.
                MessageBox.Show("Dọn dẹp thùng rác không được triển khai trực tiếp trong phiên bản này. Vui lòng dọn dẹp thủ công.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi khi dọn dẹp thùng rác: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void OptimizeMemory_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng tối ưu hóa bộ nhớ chưa được triển khai đầy đủ trong phiên bản này.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void CleanupRegistry_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Dọn dẹp Registry là một tác vụ phức tạp và tiềm ẩn rủi ro. Tính năng này không được khuyến nghị hoặc chưa được triển khai đầy đủ trong phiên bản này.", "Cảnh báo", MessageBoxButton.OK, MessageBoxImage.Warning);
        }

        private void FindDuplicateFiles_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Tính năng tìm kiếm tệp trùng lặp chưa được triển khai đầy đủ trong phiên bản này.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}