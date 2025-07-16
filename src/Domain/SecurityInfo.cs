using System;

namespace InfoPCTools.Domain
{
    public class SecurityInfo : BaseEntity
    {
        public bool FirewallEnabled { get; set; }
        public bool AntivirusEnabled { get; set; }
        public bool WindowsDefenderEnabled { get; set; }
        public DateTime LastScanDate { get; set; }
        public int VulnerabilitiesFound { get; set; }
        public DateTime CaptureDate { get; set; }
    }
}