using System;

namespace InfoPCTools.Domain
{
    public class BackupInfo : BaseEntity
    {
        public string BackupLocation { get; set; }
        public DateTime LastBackupDate { get; set; }
        public long BackupSize { get; set; }
        public bool IsScheduled { get; set; }
        public string ScheduleFrequency { get; set; }
        public DateTime CaptureDate { get; set; }
    }
}