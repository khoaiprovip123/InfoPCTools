using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public interface ISecurityAssessmentService
    {
        Task<bool> IsFirewallEnabledAsync();
        Task<bool> IsAntivirusEnabledAsync();
        Task<bool> IsWindowsDefenderEnabledAsync();
        Task<int> ScanForVulnerabilitiesAsync();
    }
}