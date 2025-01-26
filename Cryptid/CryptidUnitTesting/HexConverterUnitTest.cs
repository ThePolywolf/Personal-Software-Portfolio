using System.Text;
using Cryptid.Encryption;

namespace CryptidUnitTesting;

public class HexConverterUnitTest
{
    [Fact]
    public void HexConverterUnitTest_Bidirectional()
    {
        const string test = "Test string";
        var converter = new HexConverter();
        
        var testBytes = Encoding.ASCII.GetBytes(test);
        var encoding = converter.ToString(testBytes);
        var decoding = converter.ToBytes(encoding);
        
        Assert.Equal(testBytes, decoding);
    }

    [Theory]
    [InlineData("af24", true)]  // basic test
    [InlineData("f24", true)]   // test with non-even input
    [InlineData("AF24", false)] // no capitals
    [InlineData("hgk0", false)] // non-allowed characters
    [InlineData("", true)]      // empty
    public void HexConverterUnitTest_ToBytes(string test, bool shouldPass)
    {
        var converter = new HexConverter();

        bool passed;
        try
        {
            converter.ToBytes(test);
            passed = true;
        }
        catch (Exception _)
        {
            passed = false;
        }
        
        Assert.Equal(shouldPass, passed);
    }

    [Fact]
    public void HexConverterUnitTest_ToBytesPrependingZero()
    {
        var converter = new HexConverter();
        const string testHex1 = "0f13a7";
        const string testHex2 = "f13a7";
        
        var bytes1 = converter.ToBytes(testHex1);
        var bytes2 = converter.ToBytes(testHex2);
        
        Assert.Equal(bytes1, bytes2);
    }
}