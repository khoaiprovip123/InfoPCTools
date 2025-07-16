using InfoPCTools.Application.Interfaces;
using InfoPCTools.Domain;
using InfoPCTools.Infrastructure.Data;

namespace InfoPCTools.Infrastructure.Repositories
{
    public class SystemInfoRepository : BaseRepository<SystemInfo>, ISystemInfoRepository
    {
        public SystemInfoRepository(ApplicationDbContext context) : base(context)
        {
        }
    }
}