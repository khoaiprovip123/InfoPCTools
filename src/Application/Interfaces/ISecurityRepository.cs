using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Interfaces
{
    public interface ISecurityRepository
    {
        Task<SecurityInfo> GetByIdAsync(Guid id);
        Task AddAsync(SecurityInfo securityInfo);
        Task UpdateAsync(SecurityInfo securityInfo);
        Task DeleteAsync(Guid id);
    }
}