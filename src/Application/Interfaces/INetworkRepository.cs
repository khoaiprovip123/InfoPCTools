using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Interfaces
{
    public interface INetworkRepository
    {
        Task<NetworkInfo> GetByIdAsync(Guid id);
        Task AddAsync(NetworkInfo networkInfo);
        Task UpdateAsync(NetworkInfo networkInfo);
        Task DeleteAsync(Guid id);
    }
}