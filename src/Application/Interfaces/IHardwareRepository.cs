using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Interfaces
{
    public interface IHardwareRepository
    {
        Task<HardwareInfo> GetByIdAsync(Guid id);
        Task AddAsync(HardwareInfo hardwareInfo);
        Task UpdateAsync(HardwareInfo hardwareInfo);
        Task DeleteAsync(Guid id);
    }
}