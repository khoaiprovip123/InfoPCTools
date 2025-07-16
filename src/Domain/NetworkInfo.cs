using System;

namespace InfoPCTools.Domain
{
    public class NetworkInfo : BaseEntity
    {
        public string AdapterName { get; set; }
        public string ConnectionType { get; set; }
        public string IPv4Address { get; set; }
        public string IPv6Address { get; set; }
        public long BytesSent { get; set; }
        public long BytesReceived { get; set; }
        public DateTime CaptureDate { get; set; }
    }
}