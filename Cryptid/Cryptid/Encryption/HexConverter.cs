using System.Text;

namespace Cryptid.Encryption;

/// <summary>
/// Converts between a HEX formatted string and a byte[]
/// </summary>
public class HexConverter() : IByteStringConverter
{
    private const string HexTokens = "0123456789abcdef";
    
    private readonly Dictionary<char, byte> _hexValues = HexTokens.ToArray().ToDictionary(token => token, token => (byte)HexTokens.IndexOf(token));

    /// <summary>
    /// Converts a char representing a HEX value into a 2-bit value
    /// </summary>
    /// <param name="hexChar">Single HEX character</param>
    /// <returns>2-bit value between 0 and 15</returns>
    /// <exception cref="FormatException">hexChar is not a supported HEX character</exception>
    private byte HexByte(char hexChar)
    {
        if (_hexValues.TryGetValue(hexChar, out var b))
            return b;
        
        throw new FormatException($"Invalid hex character '{hexChar}'");
    }

    /// <summary>
    /// Converts a string in HEX format into a byte[]
    /// </summary>
    /// <param name="text">A string in HEX format</param>
    /// <returns>byte representation of the hex string</returns>
    public byte[] ToBytes(string text)
    {
        // prepend a 0 if the total length is odd
        if (text.Length % 2 == 1)
            text = $"0{text}";
        
        var bytes = new byte[text.Length / 2];

        for (var i = 0; i < text.Length; i += 2)
            bytes[i / 2] = (byte)(16 * HexByte(text[i]) + HexByte(text[i + 1]));
        
        return bytes;
    }

    /// <summary>
    /// Converts a byte[] into a string representation of their HEX format
    /// </summary>
    /// <param name="bytes">All bytes</param>
    /// <returns>A HEX representation of the bytes as a string</returns>
    public string ToString(byte[] bytes)
    {
        if (bytes.Length == 0)
            return string.Empty;
        
        var sb = new StringBuilder();

        foreach (var b in bytes)
            sb.Append(HexTokens[b / 16]).Append(HexTokens[b % 16]);
        
        return sb.ToString();
    }
}