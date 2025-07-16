using System.Collections.Generic;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public interface INetworkMonitoringService
    {
        Task<List<string>> GetNetworkAdaptersAsync();
        Task<double> TestNetworkSpeedAsync();
        Task<List<int>> ScanOpenPortsAsync(string ipAddress);
        Task<long> GetTrafficDataAsync();
    }
}