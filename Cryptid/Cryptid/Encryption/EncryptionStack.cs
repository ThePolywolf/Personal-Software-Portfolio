using System.Text;

namespace Cryptid.Encryption;

/// <summary>
/// An encryption stack that compresses and encrypts plain text
/// </summary>
/// <param name="compressionSequence">A compression sequence; Each compression occurs in order</param>
/// <param name="encryptionSequence">An encryption sequence; Each encryption occurs in order</param>
/// <param name="byteStringConverter">Optional final encryption into a specified format. If null, converts into a UTF8 string</param>
public class EncryptionStack(ICompressor[] compressionSequence, IEncrypter[] encryptionSequence, IByteStringConverter? byteStringConverter)
{
    public string Encrypt(string plainText)
    {
        var bytes = Encoding.UTF8.GetBytes(plainText);

        bytes = compressionSequence.Aggregate(bytes, (current, compressor) => compressor.Encrypt(current));

        bytes = encryptionSequence.Aggregate(bytes, (current, encryptor) => encryptor.Decrypt(current));
        
        return byteStringConverter?.ToString(bytes) ?? Encoding.UTF8.GetString(bytes);
    }

    public string Decrypt(string cipherText)
    {
        var bytes = byteStringConverter?.ToBytes(cipherText) ?? [];
        
        bytes = encryptionSequence.Reverse().Aggregate(bytes, (current, encryptor) => encryptor.Decrypt(current));

        bytes = compressionSequence.Reverse().Aggregate(bytes, (current, compressor) => compressor.Decrypt(current));

        return Encoding.UTF8.GetString(bytes);
    }
}