using System.Collections;

namespace Cryptid.Encryption;

/// <summary>
/// An encoding node in a Huffman tree
/// </summary>
public class HuffmanNode
{
    public int Weight { get; }

    private readonly HuffmanNode? _node0;
    private readonly HuffmanNode? _node1;

    private readonly byte? _value;
    public bool IsLeaf() => _value is not null;

    public byte GetValue()
    {
        if (_value is null) throw new NullReferenceException(nameof(_value));
        return _value.Value;
    }
    
    /// <summary>
    /// Creates a new Huffman leaf
    /// </summary>
    /// <param name="value">Output byte</param>
    /// <param name="weight">Leaf weight</param>
    public HuffmanNode(byte value, int weight = 0)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(weight, nameof(weight));
        
        Weight = weight;
        _value = value;
        
        _node0 = null;
        _node1 = null;
    }

    /// <summary>
    /// Creates a Huffman connection node
    /// </summary>
    /// <param name="node0">Encoding 0 branch node</param>
    /// <param name="node1">Encoding 1 branch node</param>
    private HuffmanNode(HuffmanNode node0, HuffmanNode node1)
    {
        _node0 = node0;
        _node1 = node1;
        Weight = node0.Weight + node1.Weight;
        
        _value = null;
    }

    /// <summary>
    /// Creates a Huffman connection node
    /// </summary>
    /// <param name="node0">Encoding 0 node</param>
    /// <param name="node1">Encoding 1 node</param>
    /// <returns>Returns new huffman connection node</returns>
    public static HuffmanNode Connection(HuffmanNode node0, HuffmanNode node1)
    {
        // This is separate from an alternate constructor to force the user to explicitly create a connection instead of a leaf
        
        return new HuffmanNode(node0, node1);
    }

    /// <summary>
    /// Gets the node along the 0 branch
    /// </summary>
    /// <returns>Node down branch 0</returns>
    /// <exception cref="NullReferenceException">Node 0 is null</exception>
    public HuffmanNode Branch0()
    {
        if (_node0 is null) throw new NullReferenceException(nameof(_node0));
        return _node0;
    }

    /// <summary>
    /// Gets the node along the 1 branch
    /// </summary>
    /// <returns>Node down branch 1</returns>
    /// <exception cref="NullReferenceException">Node 1 is null</exception>
    public HuffmanNode Branch1()
    {
        if (_node1 is null) throw new NullReferenceException(nameof(_node1));
        return _node1;
    }

    /// <summary>
    /// Creates an encoding dictionary to convert bytes into BitArrays
    /// </summary>
    /// <returns>A dictionary of encodings with a byte as a key, and a BitArray encoding as a value</returns>
    public Dictionary<byte, BitArray> GetEncoding()
    {
        var result = new Dictionary<byte, BitArray>();
        GetEncoding(ref result, new Stack<bool>());
        return result;
    }

    /// <summary>
    /// An internal method to get the tree encoding
    /// </summary>
    /// <param name="dict">Reference dictionary of encodings</param>
    /// <param name="prefix">Stack of prefix values for an encoding</param>
    private void GetEncoding(ref Dictionary<byte, BitArray> dict, Stack<bool> prefix)
    {
        // returns the output encoded as the prefix if relevant
        if (_value is not null)
        {
            dict[_value.Value] = new BitArray(prefix.ToArray().Reverse().ToArray());
            return;
        }
        
        // if there is no output, it means there are two branches (0 and 1) for encodings
        if (_node0 is null) ArgumentNullException.ThrowIfNull(_node0);
        if (_node1 is null) ArgumentNullException.ThrowIfNull(_node1);
        
        // get encodings from branches
        prefix.Push(false);
        _node0.GetEncoding(ref dict, prefix);
        prefix.Pop();
        
        prefix.Push(true);
        _node1.GetEncoding(ref dict, prefix);
        prefix.Pop();
    }

    /// <summary>
    /// Creates a DFS list of bytes encoded in the huffman tree.
    /// The order the nodes appear is identical to the order that leaves are created in the TreeEncoding
    /// </summary>
    /// <returns>A list of encoded bytes in the tree</returns>
    private List<byte> EncodedByteOrder()
    {
        if (_value is not null)
            return [_value.Value];
        
        if (_node0 is null) ArgumentNullException.ThrowIfNull(_node0);
        if (_node1 is null) ArgumentNullException.ThrowIfNull(_node1);
        
        var result = _node0.EncodedByteOrder();
        result.AddRange(_node1.EncodedByteOrder());

        return result;
    }

    /// <summary>
    /// Creates a DFS encoding of the Huffman encoding tree
    /// </summary>
    /// <returns>A bool list representing a pattern to create the tree</returns>
    private List<bool> TreeEncoding()
    {
        if (_value is not null)
            return [false];
        
        if (_node0 is null) ArgumentNullException.ThrowIfNull(_node0);
        if (_node1 is null) ArgumentNullException.ThrowIfNull(_node1);

        var result = new List<bool>();
        result.Add(true);
        result.AddRange(_node0.TreeEncoding());
        result.Add(true);
        result.AddRange(_node1.TreeEncoding());
        result.Add(false);
        
        // WARNING: tree will always result in 1 extra _goBack pattern, make sure to account for it when decoding
        // TODO use as an exit pattern for tree completion?

        return result;
    }

    /// <summary>
    /// Returns the binary header of the huffman tree for reconstruction when decoding the file
    /// </summary>
    /// <param name="messagePadding">Bit-padding of message</param>
    /// <returns>Completed Huffman binary file header</returns>
    public byte[] GetHeader(int messagePadding)
    {
        var headerLength = 0;
        
        // Message
        var messageEncoding = "HUFF"u8.ToArray();
        headerLength += messageEncoding.Length;
        
        // All encoded bytes
        var encodedBytes = EncodedByteOrder().ToArray();
        headerLength += encodedBytes.Length;
        
        var totalEncoded = (byte)(encodedBytes.Length);  // 1-256 encoded => 0-255 byte
        headerLength += 1;
        
        // Tree encoding
        var treeEncoding = TreeEncoding().ToArray();
        var headerPadding = treeEncoding.Length % 8 == 0 ? 0 : 8 - treeEncoding.Length % 8;
        
        headerLength += treeEncoding.Length / 8 + (treeEncoding.Length % 8 == 0 ? 0 : 1);
        
        // Padding marker
        var padding = (byte)(headerPadding * 16 + messagePadding);
        headerLength += 1;
        
        // create header
        var header = new byte[headerLength];

        messageEncoding.CopyTo(header, 0);
        header[4] = padding;
        header[5] = totalEncoded;
        encodedBytes.CopyTo(header, 6);
        UnitConversion.BinaryToBytes(treeEncoding).CopyTo(header, 6 + encodedBytes.Length);

        return header;
    }

    private enum TreeBranch
    {
        Left,
        Right
    }

    private enum TreeAction
    {
        Add,
        Back
    }

    /// <summary>
    /// Converts a file header into a huffman tree
    /// </summary>
    /// <param name="header">Huffman encoding byte[] that includes an encoded header</param>
    /// <param name="bytePickupIndex">What index the header ends at in the given byte[] header</param>
    /// <param name="bitPadding">how many bytes are padding the encoded content</param>
    /// <returns>Root of the huffman encoding tree</returns>
    public static HuffmanNode TreeFromHeader(ref byte[] header, out int bytePickupIndex, out int bitPadding)
    {
        // skip message
        var byteIndex = 4;
        
        // Padding
        var paddingGroup = header[byteIndex++];
        var messagePadding = paddingGroup % 16;
        var headingPadding = paddingGroup / 16;
        
        // Encoded bytes
        var encodedByteCount = header[byteIndex++];
        var encodedBytes = new Queue<byte>();
        while (byteIndex - 6 < encodedByteCount)
            encodedBytes.Enqueue(header[byteIndex++]);
        
        var lastAction = TreeAction.Add;
        var sides = new Stack<TreeBranch>();
        var leftNodes = new Stack<HuffmanNode>();
        HuffmanNode? rightNode = null;
        var done = false;
        
        // Decode and reconstruct huffman tree from 1-bit flags
        while (!done)
        {
            foreach (var actionBool in UnitConversion.BytesToBinary([ header[byteIndex++] ]))
            {
                var action = actionBool ? TreeAction.Add : TreeAction.Back;
                
                if (action == TreeAction.Add)
                {
                    sides.Push(lastAction == TreeAction.Add ? TreeBranch.Left : TreeBranch.Right);
                    lastAction = action;
                    continue;
                }

                // Action == Back
                if (sides.Count == 0)
                {
                    if (rightNode is null) throw new NullReferenceException();
                    rightNode = Connection(leftNodes.Pop(), rightNode);
                    done = true;
                    break;
                }
                
                var side = sides.Pop();
                
                if (lastAction == TreeAction.Add)
                {
                    if (side == TreeBranch.Left)
                        leftNodes.Push(new HuffmanNode(encodedBytes.Dequeue()));
                    else
                        rightNode = new HuffmanNode(encodedBytes.Dequeue());

                    lastAction = action;
                    continue;
                }
                
                // lastAction == Back
                if (rightNode is null) throw new NullReferenceException(nameof(rightNode));
                
                var newNode = Connection(leftNodes.Pop(), rightNode);
                if (side == TreeBranch.Left)
                    leftNodes.Push(newNode);
                else
                    rightNode = newNode;
            
                lastAction = action;
            }
        }
        
        // get numeric -> character encoding
        if (rightNode is null) throw new NullReferenceException(nameof(rightNode));

        bytePickupIndex = byteIndex;
        bitPadding = messagePadding;
        return rightNode;
    }
}