using Cryptid.Encryption;

namespace CryptidUnitTesting;

public class UnitConversionUnitTesting
{
    [Fact]
    public void UnitConversionUnitTesting_BinaryToBytes()
    {
        var test1 = new[] { false, false, false, false, true, false, false, false };
        var test2 = new[] { false, false, false, true };
        var test3 = new[] { false, false, false, false, true, false, false, false, false };
        var expected1 = new byte[] { 8 };
        var expected2 = new byte[] { 16 };
        var expected3 = new byte[] { 8, 0 };
        
        var encryption1 = UnitConversion.BinaryToBytes(test1);
        var encryption2 = UnitConversion.BinaryToBytes(test2);
        var encryption3 = UnitConversion.BinaryToBytes(test3);
        
        Assert.Equal(expected1, encryption1);
        Assert.Equal(expected2, encryption2);
        Assert.Equal(expected3, encryption3);
    }

    [Fact]
    public void UnitConversionUnitTesting_Transitivity()
    {
        var test = new byte[] { 0, 255, 255, 0, 43, 0 };
        
        var encryption = UnitConversion.BytesToBinary(test);
        var decryption = UnitConversion.BinaryToBytes(encryption);
        
        Assert.Equal(test, decryption);
    }
}