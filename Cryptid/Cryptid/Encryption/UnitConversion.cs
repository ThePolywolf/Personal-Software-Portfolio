using System.Collections;

namespace Cryptid.Encryption;

public static class UnitConversion
{
    /// <summary>
    /// Converts a boolean array into a byte array. Back-fills the array with zeros
    /// </summary>
    /// <param name="binary">Binary to convert</param>
    /// <returns>Byte representation of the binary</returns>
    public static byte[] BinaryToBytes(bool[] binary)
    {
        var output = new byte[binary.Length / 8 + (binary.Length % 8 == 0 ? 0 : 1)];
        byte currentByte = 0;
        var byteIndex = 0;
        var bitIndex = 0;

        foreach (var b in binary)
        {
            currentByte = (byte)(currentByte * 2 + (b ? 1 : 0));
            bitIndex++;

            if (bitIndex < 8)
                continue;

            output[byteIndex] = currentByte;

            currentByte = 0;
            bitIndex = 0;
            byteIndex++;
        }

        if (currentByte == 0)
            return output;

        while (bitIndex < 8)
        {
            currentByte *= 2;
            bitIndex++;
        }
        
        output[byteIndex] = currentByte;
        return output;
    }

    /// <summary>
    /// Converts a byte array to a boolean array.
    /// </summary>
    /// <param name="bytes">Bytes to convert</param>
    /// <returns>Binary representation of the bytes as a boolean array</returns>
    public static bool[] BytesToBinary(byte[] bytes)
    {
        var output = new bool[bytes.Length * 8];

        var bitIndex = 0;
        foreach (var b in bytes)
        {
            var currentBoolByte = new Stack<bool>();

            var remainder = b;
            for (var i = 0; i < 8; i++)
            {
                currentBoolByte.Push(remainder % 2 == 1);
                remainder /= 2;
            }
            
            currentBoolByte.ToArray().CopyTo(output, bitIndex);
            bitIndex += 8;
        }
        
        return output;
    }

    /// <summary>
    /// Convert a BitArray into a single integer value
    /// </summary>
    /// <param name="bitArray">Bits to calculate from</param>
    /// <returns>Integer value of bits</returns>
    public static int BitArrayToInt(BitArray bitArray)
    {
        var value = 0;
        for (var i = 0; i < bitArray.Length; i++)
            value = value * 2 + (bitArray[i] ? 1 : 0);
        return value;
    }
}