using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public interface IPerformanceMonitoringService
    {
        Task<double> GetCpuUsageAsync();
        Task<double> GetRamUsageAsync();
        Task<double> GetTemperatureAsync();
        Task<double> GetDiskUsageAsync();
    }
}