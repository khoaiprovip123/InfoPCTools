using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public interface IBackupManagementService
    {
        Task ConfigureBackupAsync(string location, string frequency);
        Task PerformBackupAsync();
        Task PerformRestoreAsync();
        Task ScheduleBackupAsync(string frequency);
    }
}