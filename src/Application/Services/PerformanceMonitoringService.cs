using InfoPCTools.Application.Services;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public class PerformanceMonitoringService : IPerformanceMonitoringService
    {
        public Task<double> GetCpuUsageAsync()
        {
            return Task.FromResult(0.5); // Placeholder
        }

        public Task<double> GetRamUsageAsync()
        {
            return Task.FromResult(0.0); // Placeholder
        }

        public Task<double> GetTemperatureAsync()
        {
            return Task.FromResult(0.0); // Placeholder
        }

        public Task<double> GetDiskUsageAsync()
        {
            return Task.FromResult(0.0); // Placeholder
        }
    }
}