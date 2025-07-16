using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Interfaces
{
    public interface IBackupRepository
    {
        Task<BackupInfo> GetByIdAsync(Guid id);
        Task AddAsync(BackupInfo backupInfo);
        Task UpdateAsync(BackupInfo backupInfo);
        Task DeleteAsync(Guid id);
    }
}