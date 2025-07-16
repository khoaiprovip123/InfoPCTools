using System.Configuration;
using System.Data;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using InfoPCTools.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using InfoPCTools.Application.Services;

namespace InfoPCTools.Presentation;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : System.Windows.Application
{
    private ServiceProvider serviceProvider;

    public App()
    {
        ServiceCollection services = new ServiceCollection();
        ConfigureServices(services);
        serviceProvider = services.BuildServiceProvider();
    }

    private void ConfigureServices(ServiceCollection services)
    {
        IConfiguration configuration = new ConfigurationBuilder()
            .SetBasePath(AppDomain.CurrentDomain.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
            .Build();

        services.AddSingleton(configuration);

        services.AddDbContext<ApplicationDbContext>(options =>
        {
            options.UseSqlServer(configuration.GetConnectionString("DefaultConnection"));
        });

        services.AddTransient<ISystemInfoService, SystemInfoService>();
        services.AddTransient<IPerformanceMonitoringService, PerformanceMonitoringService>();
        services.AddTransient<ISecurityAssessmentService, SecurityAssessmentService>();
        services.AddTransient<INetworkMonitoringService, NetworkMonitoringService>();
        services.AddTransient<IBackupManagementService, BackupManagementService>();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        using (var scope = serviceProvider.CreateScope())
        {
            var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            SeedData.Initialize(context);
        }
    }
}