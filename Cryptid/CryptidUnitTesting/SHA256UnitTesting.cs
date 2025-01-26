using Cryptid.Encryption;

namespace CryptidUnitTesting;

public class SHA256UnitTesting
{
    [Theory]
    [InlineData("100010", 4, "0000010")]
    public void SHA256_ShiftRight(string testString, int shift, string expectedString)
    {
        var test = new bool[testString.Length];
        for (var i = 0; i < testString.Length; i++)
        {
            test[i] = testString[i] == '1';
        }
        
        var expected = new bool[expectedString.Length];
        for (var i = 0; i < expectedString.Length; i++)
        {
            expected[i] = expectedString[i] == '1';
        }
        
        var sha256 = new SHA256();
        sha256.ShiftRight(ref test, shift);
        
        Assert.Equal(test, expected);
    }
}