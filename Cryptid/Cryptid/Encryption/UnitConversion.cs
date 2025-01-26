namespace Cryptid.Encryption;

public static class Convert
{
    /// <summary>
    /// Converts a boolean array into a byte array. Back-fills the array with zeros
    /// </summary>
    /// <param name="binary">Binary to convert</param>
    /// <returns>Byte representation of the binary</returns>
    private static byte[] BinaryToBytes(bool[] binary)
    {
        var output = new byte[binary.Length / 8 + (binary.Length % 8 == 0 ? 0 : 1)];
        byte currentByte = 0;
        var byteIndex = 0;
        var bitIndex = 0;

        foreach (var b in binary)
        {
            currentByte = (byte)(currentByte * 2 + (b ? 1 : 0));
            bitIndex++;

            if (bitIndex < 7)
                continue;

            output[byteIndex] = currentByte;

            currentByte = 0;
            bitIndex = 0;
            byteIndex++;
        }

        if (currentByte == 0)
            return output;

        while (bitIndex < 7)
        {
            currentByte *= 2;
            bitIndex++;
        }
        
        output[byteIndex] = currentByte;
        return output;
    }
}