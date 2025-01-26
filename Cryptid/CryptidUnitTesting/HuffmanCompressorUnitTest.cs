using System.Text;
using Cryptid.Encryption;

namespace CryptidUnitTesting;

public class HuffmanCompressorUnitTest
{
    [Theory]
    [InlineData("ddddddddddddddd")]
    [InlineData("")]
    [InlineData("rgb")]
    public void HuffmanCompressorUnitTest_Transitivity(string test)
    {
        var testBytes = Encoding.UTF8.GetBytes(test);
        var compressor = new HuffmanCompressor();
        
        var encodedValue = compressor.Encrypt(testBytes);
        var decodedValue = compressor.Decrypt(encodedValue);
        
        Assert.Equal(testBytes, decodedValue);
    }

    [Fact]
    public void HuffmanCompressorUnitTest_LargeCompression()
    {
        const char regularCharacter = 'c';
        const int regularCount = 500;
        const int testSize = 100000;
        const int minRange = 0x20;
        const int maxRange = 0xD7FF;
        
        var random = new Random(1000);
        var sb = new StringBuilder();
        for (var i = 0; i < regularCount; i++)
            sb.Append(regularCharacter);
        for (var i = 0; i < testSize; i++)
            sb.Append((char)random.Next(minRange, maxRange + 1));
        
        var testDocument = sb.ToString();
        var testBytes = Encoding.UTF8.GetBytes(testDocument);
        var compressor = new HuffmanCompressor();
        
        var encodedValue = compressor.Encrypt(testBytes);
        var decodedValue = compressor.Decrypt(encodedValue);
        
        Assert.Equal(testBytes, decodedValue);
    }

    [Fact]
    public void HuffmanCompressorUnitTest_StrictCompression()
    {
        var testStringBytes = "test string"u8.ToArray();
        var compressor = new HuffmanCompressor();
        
        var encodedValue = compressor.ForceEncrypt(testStringBytes);
        var decodedValue = compressor.Decrypt(encodedValue);
        
        Assert.Equal(testStringBytes, decodedValue);
    }

    [Fact]
    public void HuffmanNodeUnitTest_LosslessHeaderCompression()
    {
        var tree = HuffmanNode.Connection(
            HuffmanNode.Connection(
                new HuffmanNode(32, 3),
                HuffmanNode.Connection(
                    new HuffmanNode(50, 1),
                    new HuffmanNode(56, 1)
                )
            ),
            new HuffmanNode(16, 50)
        );

        const byte fakePadding = 7;
        var header = tree.GetHeader(fakePadding);

        var decodedTree = HuffmanNode.TreeFromHeader(ref header, out _, out var fakePaddingOut);
        
        Assert.Equal(header, decodedTree.GetHeader(fakePadding));
        Assert.Equal(fakePadding, fakePaddingOut);
    }
}