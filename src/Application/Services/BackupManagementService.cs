using InfoPCTools.Application.Services;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public class BackupManagementService : IBackupManagementService
    {
        public Task ConfigureBackupAsync(string location, string frequency)
        {
            return Task.CompletedTask; // Placeholder
        }

        public Task PerformBackupAsync()
        {
            return Task.CompletedTask; // Placeholder
        }

        public Task PerformRestoreAsync()
        {
            return Task.CompletedTask; // Placeholder
        }

        public Task ScheduleBackupAsync(string frequency)
        {
            return Task.CompletedTask; // Placeholder
        }
    }
}