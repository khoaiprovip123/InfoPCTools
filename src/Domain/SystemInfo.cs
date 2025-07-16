using System;

namespace InfoPCTools.Domain
{
    public class SystemInfo : BaseEntity
    {
        public string OSName { get; set; }
        public string OSVersion { get; set; }
        public string CPUName { get; set; }
        public int NumberOfCores { get; set; }
        public int NumberOfLogicalProcessors { get; set; }
        public long TotalPhysicalMemory { get; set; }
        public string ComputerName { get; set; }
        public string UserName { get; set; }
        public DateTime CaptureDate { get; set; }

        public bool IsValid()
        {
            return !string.IsNullOrWhiteSpace(OSName);
        }
    }
}