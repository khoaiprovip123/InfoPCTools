using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Interfaces
{
    public interface ISystemInfoRepository
    {
        Task<SystemInfo> GetByIdAsync(Guid id);
        Task AddAsync(SystemInfo systemInfo);
        Task UpdateAsync(SystemInfo systemInfo);
        Task DeleteAsync(Guid id);
    }
}