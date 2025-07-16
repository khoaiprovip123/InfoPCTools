using System;

namespace InfoPCTools.Domain
{
    public class HardwareInfo : BaseEntity
    {
        public string DeviceType { get; set; }
        public string Manufacturer { get; set; }
        public string Model { get; set; }
        public string SerialNumber { get; set; }
        public DateTime CaptureDate { get; set; }
    }
}