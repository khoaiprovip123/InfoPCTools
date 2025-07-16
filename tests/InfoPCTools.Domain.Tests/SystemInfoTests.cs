using InfoPCTools.Domain;
using Xunit;

namespace InfoPCTools.Domain.Tests
{
    public class SystemInfoTests
    {
        [Fact]
        public void IsValid_ShouldReturnTrue_WhenOSNameIsProvided()
        {
            // Arrange
            var systemInfo = new SystemInfo { OSName = "Windows 10" };

            // Act
            var isValid = systemInfo.IsValid();

            // Assert
            Assert.True(isValid);
        }

        [Fact]
        public void IsValid_ShouldReturnFalse_WhenOSNameIsNull()
        {
            // Arrange
            var systemInfo = new SystemInfo { OSName = null };

            // Act
            var isValid = systemInfo.IsValid();

            // Assert
            Assert.False(isValid);
        }

        [Fact]
        public void IsValid_ShouldReturnFalse_WhenOSNameIsEmpty()
        {
            // Arrange
            var systemInfo = new SystemInfo { OSName = string.Empty };

            // Act
            var isValid = systemInfo.IsValid();

            // Assert
            Assert.False(isValid);
        }

        [Fact]
        public void IsValid_ShouldReturnFalse_WhenOSNameIsWhitespace()
        {
            // Arrange
            var systemInfo = new SystemInfo { OSName = " " };

            // Act
            var isValid = systemInfo.IsValid();

            // Assert
            Assert.False(isValid);
        }
    }
}