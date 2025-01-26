namespace Cryptid.Encryption;

public class EncryptionStack(ICompressor[] compressionSequence, IEncrypter[] encryptionSequence, IByteStringConverter? byteStringConverter)
{
    private readonly ICompressor[] _compressionSequence = compressionSequence;
    
    private readonly IEncrypter[] _encryptionSequence = encryptionSequence;
    
    private readonly IByteStringConverter? _byteStringConverter = byteStringConverter;

    public string Encrypt(string plainText)
    {
        // plainText to byte[]
        
        var bytes = Array.Empty<byte>();

        foreach (var compressor in _compressionSequence)
        {
            bytes = compressor.Encrypt(bytes);
        }

        foreach (var encrypter in _encryptionSequence)
        {
            bytes = encrypter.Encrypt(bytes);
        }
        
        // todo: null byte convertor to standard string
        return _byteStringConverter?.ToString(bytes) ?? "";
    }

    public string Decrypt(string cipherText)
    {
        var bytes = _byteStringConverter?.ToBytes(cipherText) ?? [];
        
        foreach (var encrypter in _encryptionSequence.Reverse())
        {
            bytes = encrypter.Decrypt(bytes);
        }
        
        foreach (var compressor in _compressionSequence.Reverse())
        {
            bytes = compressor.Decrypt(bytes);
        }

        // bytes back into string
        return "";
    }
}