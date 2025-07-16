using Microsoft.EntityFrameworkCore;
using InfoPCTools.Domain;

namespace InfoPCTools.Infrastructure.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        // Add DbSets for your entities here
        public DbSet<SystemInfo> SystemInfos { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            // Configure your entities here
        }
    }
}