using InfoPCTools.Application.Services;
using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public class SystemInfoService : ISystemInfoService
    {
        public Task<SystemInfo> GetSystemInfoAsync()
        {
            // Placeholder for actual system information collection
            var systemInfo = new SystemInfo
            {
                OSName = "Windows 10 (Placeholder)",
                OSVersion = "10.0.19045 (Placeholder)",
                CPUName = "Intel(R) Core(TM) i7 (Placeholder)",
                NumberOfCores = 8,
                NumberOfLogicalProcessors = 16,
                TotalPhysicalMemory = 16 * 1024 * 1024 * 1024, // 16 GB
                ComputerName = "MYPC (Placeholder)",
                UserName = "User (Placeholder)",
                CaptureDate = System.DateTime.Now
            };
            return Task.FromResult(systemInfo);
        }
    }
}