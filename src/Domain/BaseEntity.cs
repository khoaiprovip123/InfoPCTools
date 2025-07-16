using System;

namespace InfoPCTools.Domain
{
    public abstract class BaseEntity : IEntity
    {
        public Guid Id { get; set; }

        protected BaseEntity()
        {
            Id = Guid.NewGuid();
        }
    }
}