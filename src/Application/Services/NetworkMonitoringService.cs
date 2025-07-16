using InfoPCTools.Application.Services;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public class NetworkMonitoringService : INetworkMonitoringService
    {
        public Task<List<string>> GetNetworkAdaptersAsync()
        {
            return Task.FromResult(new List<string> { "Ethernet (Placeholder)", "Wi-Fi (Placeholder)" });
        }

        public Task<double> TestNetworkSpeedAsync()
        {
            return Task.FromResult(100.0); // Placeholder Mbps
        }

        public Task<List<int>> ScanOpenPortsAsync(string ipAddress)
        {
            return Task.FromResult(new List<int> { 80, 443 }); // Placeholder
        }

        public Task<long> GetTrafficDataAsync()
        {
            return Task.FromResult(1024 * 1024 * 100L); // Placeholder 100 MB
        }
    }
}