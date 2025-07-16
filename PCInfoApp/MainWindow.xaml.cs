using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace PCInfoApp;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    private bool _isDarkMode = false; // Default to light mode

    public MainWindow()
    {
        InitializeComponent();
        ApplyTheme(); // Apply initial theme
        // Set initial view to Dashboard
        ShowView(new DashboardView());
    }

    private void ShowView(UserControl view)
    {
        if (MainContentControl.Content != null)
        {
            // Fade out current content
            Storyboard fadeOut = (Storyboard)FindResource("FadeOut");
            fadeOut.Completed += (s, e) =>
            {
                MainContentControl.Content = view;
                // Fade in new content
                Storyboard fadeIn = (Storyboard)FindResource("FadeIn");
                fadeIn.Begin();
            };
            fadeOut.Begin();
        }
        else
        {
            // If no content, just set and fade in
            MainContentControl.Content = view;
            Storyboard fadeIn = (Storyboard)FindResource("FadeIn");
            fadeIn.Begin();
        }
    }

    private void ToggleTheme_Click(object sender, RoutedEventArgs e)
    {
        _isDarkMode = !_isDarkMode;
        ApplyTheme();
    }

    private void ApplyTheme()
    {
        ResourceDictionary newTheme = new ResourceDictionary();
        newTheme.Source = new Uri("pack://application:,,,/PCInfoApp;component/Styles.xaml", UriKind.Absolute);

        if (_isDarkMode)
        {
            Application.Current.Resources["PrimaryBlue"] = (SolidColorBrush)newTheme["PrimaryBlue_Dark"];
            Application.Current.Resources["SuccessGreen"] = (SolidColorBrush)newTheme["SuccessGreen_Dark"];
            Application.Current.Resources["WarningOrange"] = (SolidColorBrush)newTheme["WarningOrange_Dark"];
            Application.Current.Resources["ErrorRed"] = (SolidColorBrush)newTheme["ErrorRed_Dark"];
            Application.Current.Resources["BackgroundColor"] = (SolidColorBrush)newTheme["BackgroundColor_Dark"];
            Application.Current.Resources["SurfaceColor"] = (SolidColorBrush)newTheme["SurfaceColor_Dark"];
            Application.Current.Resources["TextPrimaryColor"] = (SolidColorBrush)newTheme["TextPrimaryColor_Dark"];
            Application.Current.Resources["TextSecondaryColor"] = (SolidColorBrush)newTheme["TextSecondaryColor_Dark"];
            Application.Current.Resources["BorderColor"] = (SolidColorBrush)newTheme["BorderColor_Dark"];
            Application.Current.Resources["WarningOrangeDark"] = (SolidColorBrush)newTheme["WarningOrangeDark_Dark"];
            Application.Current.Resources["WarningOrangeSoft"] = (SolidColorBrush)newTheme["WarningOrangeSoft_Dark"];
            Application.Current.Resources["ErrorRedSoft"] = (SolidColorBrush)newTheme["ErrorRedSoft_Dark"];
        }
        else
        {
            Application.Current.Resources["PrimaryBlue"] = (SolidColorBrush)newTheme["PrimaryBlue"];
            Application.Current.Resources["SuccessGreen"] = (SolidColorBrush)newTheme["SuccessGreen"];
            Application.Current.Resources["WarningOrange"] = (SolidColorBrush)newTheme["WarningOrange"];
            Application.Current.Resources["ErrorRed"] = (SolidColorBrush)newTheme["ErrorRed"];
            Application.Current.Resources["BackgroundColor"] = (SolidColorBrush)newTheme["BackgroundColor"];
            Application.Current.Resources["SurfaceColor"] = (SolidColorBrush)newTheme["SurfaceColor"];
            Application.Current.Resources["TextPrimaryColor"] = (SolidColorBrush)newTheme["TextPrimaryColor"];
            Application.Current.Resources["TextSecondaryColor"] = (SolidColorBrush)newTheme["TextSecondaryColor"];
            Application.Current.Resources["BorderColor"] = (SolidColorBrush)newTheme["BorderColor"];
            Application.Current.Resources["WarningOrangeDark"] = (SolidColorBrush)newTheme["WarningOrangeDark"];
            Application.Current.Resources["WarningOrangeSoft"] = (SolidColorBrush)newTheme["WarningOrangeSoft"];
            Application.Current.Resources["ErrorRedSoft"] = (SolidColorBrush)newTheme["ErrorRedSoft"];
        }
    }

    private void DashboardButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new DashboardView());
    }

    private void SystemInfoButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new SystemInfoView());
    }

    private void ProcessManagerButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new ProcessManagerView());
    }

    private void CleanupButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new CleanupView());
    }

    private void PerformanceTuningButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new PerformanceTuningView());
    }

    private void BenchmarkButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new BenchmarkView());
    }

    private void RemoteMonitoringButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new RemoteMonitoringView());
    }

    private void AIIntegrationButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new AIIntegrationView());
    }

    private void ReportingButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new ReportingView());
    }

    private void DataManagementButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new DataManagementView());
    }

    private void FinalPolishButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new FinalPolishView());
    }

    private void DistributionButton_Click(object sender, RoutedEventArgs e)
    {
        ShowView(new DistributionView());
    }
}