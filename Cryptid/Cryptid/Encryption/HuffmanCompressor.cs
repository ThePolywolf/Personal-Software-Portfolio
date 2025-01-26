using System.Collections;
using System.Security.Cryptography;
using System.Text;

namespace Cryptid.Encryption;

/// <summary>
/// A class to compress and decompress data using the huffman compression method
/// </summary>
public class HuffmanCompressor : ICompressor
{
    /// <summary>
    /// Creates a dictionary of bytes, and number of occurrences
    /// </summary>
    /// <param name="bytes">Bytes to count</param>
    /// <returns>Dictionary of bytes and their count</returns>
    public static Dictionary<byte, int> GetByteCounts(byte[] bytes)
    {
        var byteCounts = new Dictionary<byte, int>();
        
        foreach (var b in bytes)
            if (!byteCounts.TryAdd(b, 1))
                byteCounts[b]++;
        
        return byteCounts;
    }

    /// <summary>
    /// Inserts a new node into the stack while maintaining the stack ordering
    /// </summary>
    /// <param name="node">New node to insert</param>
    /// <param name="orderedStack">Empty stack, or stack ordered by occurrences (low to high)</param>
    public static void OrderInStack(HuffmanNode node, ref Stack<HuffmanNode> orderedStack)
    {
        if (orderedStack.Count == 0)
        {
            orderedStack.Push(node);
            return;
        }
        
        var offStack = new Stack<HuffmanNode>();
            
        while (orderedStack.Count > 0 && node.Weight > orderedStack.Peek().Weight)
            offStack.Push(orderedStack.Pop());
            
        orderedStack.Push(node);
            
        while (offStack.Count > 0)
            orderedStack.Push(offStack.Pop());
    }

    /// <summary>
    /// Creates a Huffman encryption tree based on node occurrence counts
    /// </summary>
    /// <param name="byteCounts">Dictionary of byte patterns and the counts of their occurrences</param>
    /// <returns>A huffman encoding tree</returns>
    public static HuffmanNode CreateTree(ref Dictionary<byte, int> byteCounts)
    {
        // Create huffman nodes sorted in a stack of lowest to highest occurrences
        var nodes = new Stack<HuffmanNode>();
        foreach (var kvp in byteCounts)
            OrderInStack(new HuffmanNode(kvp.Key, kvp.Value), ref nodes);

        // collapse all nodes into a single tree
        while (nodes.Count > 1)
        {
            var node = HuffmanNode.Connection(nodes.Pop(), nodes.Pop());
            OrderInStack(node, ref nodes);
        }

        return nodes.Pop();
    }

    /// <summary>
    /// Forces the message to be encrypted with Huffman Compression if the message is not empty
    /// </summary>
    /// <param name="bytes">Message to compress</param>
    /// <returns>A HUFF or NONE encryption of the given bytes</returns>
    public byte[] ForceEncrypt(byte[] bytes)
    {
        var byteCounts = GetByteCounts(bytes);

        if (byteCounts.Count == 0)
            return EncryptNone();

        var tree = CreateTree(ref byteCounts);
        var encoding = tree.GetEncoding();
        
        // calculate the ending size
        var encodedDataBitLength = byteCounts.Sum(kvp => kvp.Value * encoding[kvp.Key].Length);
        var encodedDataLength = encodedDataBitLength / 8 + (encodedDataBitLength % 8 == 0 ? 0 : 1);
        var messagePadding = encodedDataLength * 8 - encodedDataBitLength;
        var header = tree.GetHeader(messagePadding);

        var endEncodingLength = header.Length + encodedDataLength;

        return EncryptHuff(bytes, header, endEncodingLength, messagePadding, ref encoding);
    }
    
    /// <summary>
    /// Compresses a message represented as a byte[]
    /// </summary>
    /// <param name="bytes">Message to compress/encrypt</param>
    /// <returns>Encrypted/Compressed message</returns>
    public byte[] Encrypt(byte[] bytes)
    {
        var startSize = bytes.Length;
        
        var byteCounts = GetByteCounts(bytes);

        if (byteCounts.Count == 0)
            return EncryptNone();

        if (byteCounts.Count == 1)
        {
            var (b, count) = byteCounts.First();
            return EncryptSameBytes(b, count);
        }

        var tree = CreateTree(ref byteCounts);
        var encoding = tree.GetEncoding();
        
        // calculate the ending size
        var encodedDataBitLength = byteCounts.Sum(kvp => kvp.Value * encoding[kvp.Key].Length);
        var encodedDataLength = encodedDataBitLength / 8 + (encodedDataBitLength % 8 == 0 ? 0 : 1);
        var messagePadding = encodedDataLength * 8 - encodedDataBitLength;
        var header = tree.GetHeader(messagePadding);

        var endEncodingLength = header.Length + encodedDataLength;

        if (endEncodingLength >= startSize)
            return EncryptBase(bytes);

        return EncryptHuff(bytes, header, endEncodingLength, messagePadding, ref encoding);
    }

    /// <summary>
    /// Creates a NONE flag. Used when the message to encrypt is empty.
    /// </summary>
    /// <returns>byte[] representing the flag NONE</returns>
    private static byte[] EncryptNone()
    {
        return "NONE"u8.ToArray();
    }
    
    /// <summary>
    /// Creates a compressed encryption of identical bytes. Used when the message to encrypt is composed of n-copies of a single character
    /// </summary>
    /// <param name="b">Identical byte</param>
    /// <param name="count">Copies of the byte</param>
    /// <returns>Compressed encryption</returns>
    private static byte[] EncryptSameBytes(byte b, int count)
    {
        var binaryCount = new Stack<bool>();

        var currentCount = count;
        while (currentCount != 0)
        {
            binaryCount.Push(currentCount % 2 == 1);
            currentCount /= 2;
        }
            
        var padding = binaryCount.Count % 8 == 0 ? 0 : 8 - binaryCount.Count % 8;
        for (var i = 0; i < padding; i++)
            binaryCount.Push(false);
            
        var message = "SAME"u8.ToArray();
        var result = new byte[5 + binaryCount.Count / 8];

        message.CopyTo(result, 0);
        result[4] = b;
        UnitConversion.BinaryToBytes(binaryCount.ToArray()).CopyTo(result, 5);

        return result;
    }

    /// <summary>
    /// 'Encrypts' the base file by prepending a flag BASE. Used when encrypting the original message would result in a larger file size
    /// </summary>
    /// <param name="bytes">Original message</param>
    /// <returns>a byte[] representing the union of BASE-flag and the original message</returns>
    private static byte[] EncryptBase(byte[] bytes)
    {
        var result = new byte[bytes.Length + 4];
        var messageEncoding = "BASE"u8.ToArray();

        for (var i = 0; i < 4; i++)
            result[i] = messageEncoding[i];
            
        bytes.CopyTo(result, 4);
        return result;
    }

    /// <summary>
    /// Creates a huffman encryption of a message.
    /// </summary>
    /// <param name="bytes">Message to encrypt</param>
    /// <param name="header">Huffman decryption header</param>
    /// <param name="endEncodingLength">Ending byte count of the encryption</param>
    /// <param name="messagePadding">message padding (for whole-byte end result)</param>
    /// <param name="encoding">byte-encoding pattern matches</param>
    /// <returns>An encryption/compression of the original bytes</returns>
    private static byte[] EncryptHuff(byte[] bytes, byte[] header, int endEncodingLength, int messagePadding, ref Dictionary<byte, BitArray> encoding)
    {
        // initialize results
        var result = new byte[endEncodingLength];
        header.CopyTo(result, 0);
        
        // encode message in 1-byte chunks
        var currentByte = new bool[8];
        var bitIndex = messagePadding;      // add the message padding to first byte
        var byteIndex = header.Length;
        
        foreach (var b in bytes)
        {
            var code = encoding[b];

            for (var i = 0; i < code.Length; i++)
            {
                currentByte[bitIndex++] = code[i];

                if (bitIndex < 8) continue;
                
                result[byteIndex++] = UnitConversion.BinaryToBytes(currentByte)[0];
                bitIndex = 0;
            }
        }
        
        return result;
    }
    
    /// <summary>
    /// Decrypts the given cipher
    /// </summary>
    /// <param name="cipherText">Message to decrypt</param>
    /// <returns>Decrypted message</returns>
    /// <exception cref="ArgumentException">File can't be decrypted since the file flag was unrecognized</exception>
    public byte[] Decrypt(byte[] cipherText)
    {
        var note = Encoding.UTF8.GetString(cipherText[new Range(0, 4)]);

        return note switch
        {
            "NONE" => DecryptNone(),
            "SAME" => DecryptSame(cipherText[new Range(4, cipherText.Length)]),
            "BASE" => DecryptBase(cipherText[new Range(4, cipherText.Length)]),
            "HUFF" => DecryptHuff(cipherText),
            _ => throw new ArgumentException($"This file can't be decrypted.")
        };
    }

    /// <summary>
    /// Decrypts NONE flag; empty message
    /// </summary>
    /// <returns>Decrypted message, which is always an empty byte[]</returns>
    private static byte[] DecryptNone()
    {
        return [];
    }

    /// <summary>
    /// Decrypts SAME flag; message was n-copies of the same character
    /// </summary>
    /// <param name="cipherText">Encrypted message representing the character to copy, and how many copies to use</param>
    /// <returns>Decrypted message</returns>
    private static byte[] DecryptSame(byte[] cipherText)
    {
        var bytePattern = cipherText[0];

        var copyBytes = cipherText[new Range(1, cipherText.Length)];
        var copies = copyBytes.Aggregate(0, (current, b) => current * 256 + b);
        
        var result = new byte[copies];
        Array.Fill(result, bytePattern);
        return result;
    }

    /// <summary>
    /// Decrypts BASE flag; base file was not encrypted 
    /// </summary>
    /// <param name="cipherText">Base file</param>
    /// <returns>Base file (returns cipherText)</returns>
    private static byte[] DecryptBase(byte[] cipherText)
    {
        return cipherText;
    }

    /// <summary>
    /// Decrypts HUFF flag; File was huffman encoded
    /// </summary>
    /// <param name="cipherText">Encrypted message</param>
    /// <returns>Decrypted message</returns>
    private static byte[] DecryptHuff(byte[] cipherText)
    {
        var tree = HuffmanNode.TreeFromHeader(ref cipherText, out var byteIndex, out var bitIndex);
        
        var result = new List<byte>();
        var currentNode = tree;
        var currentByte = UnitConversion.BytesToBinary([ cipherText[byteIndex++] ]);

        while (byteIndex < cipherText.Length + 1)
        {
            currentNode = (currentByte[bitIndex] ? 1 : 0) switch
            {
                0 => currentNode.Branch0(),
                1 => currentNode.Branch1()
            };

            if (currentNode.IsLeaf())
            {
                var val = currentNode.GetValue();
                result.Add(val);
                currentNode = tree;
            }

            bitIndex++;
            if (bitIndex < 8) continue;
            
            bitIndex = 0;
            if (byteIndex >= cipherText.Length) break;
            currentByte = UnitConversion.BytesToBinary([cipherText[byteIndex++]]);
        }

        return result.ToArray();
    }
}