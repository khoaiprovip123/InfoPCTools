using InfoPCTools.Domain;
using System;
using System.Linq;

namespace InfoPCTools.Infrastructure.Data
{
    public static class SeedData
    {
        public static void Initialize(ApplicationDbContext context)
        {
            context.Database.EnsureCreated();

            if (context.SystemInfos.Any())
            {
                return;   // DB has been seeded
            }

            context.SystemInfos.AddRange(
                new SystemInfo
                {
                    OSName = "Windows 10 Pro",
                    OSVersion = "10.0.19045",
                    CPUName = "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                    NumberOfCores = 8,
                    NumberOfLogicalProcessors = 16,
                    TotalPhysicalMemory = 16 * 1024 * 1024 * 1024, // 16 GB
                    ComputerName = "MYPC",
                    UserName = "User",
                    CaptureDate = DateTime.Now
                }
            );
            context.SaveChanges();
        }
    }
}