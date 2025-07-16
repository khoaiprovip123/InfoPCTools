using InfoPCTools.Domain;
using System.Threading.Tasks;

namespace InfoPCTools.Application.Services
{
    public interface ISystemInfoService
    {
        Task<SystemInfo> GetSystemInfoAsync();
    }
}