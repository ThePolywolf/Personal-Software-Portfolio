using System.ComponentModel;

namespace Cryptid.Encryption;

/// <summary>
/// A class to easily build an encryption stack using the builder pattern
/// </summary>
public class EncryptionStackBuilder()
{
    private readonly List<ICompressor> _compressors = [];
    private readonly List<IEncrypter> _encryptors = [];

    private bool _hasBeenSet = false;
    
    private IByteStringConverter? _byteStringConverter = null;

    /// <summary>
    /// Adds a compressor to the encryption stack
    /// </summary>
    /// <param name="compressor">Compressor to add</param>
    /// <returns>Current EncryptionStackBuilder instance.</returns>
    public EncryptionStackBuilder AddCompressor(ICompressor compressor)
    {
        _compressors.Add(compressor);
        return this;
    }

    /// <summary>
    /// Adds multiple compressors to the EncryptionStack
    /// </summary>
    /// <param name="compressors">All compressors to add</param>
    /// <returns>Current EncryptionStackBuilder instance.</returns>
    public EncryptionStackBuilder AddCompressors(params ICompressor[] compressors)
    {
        if (compressors is null || compressors.Length == 0)
        {
            throw new ArgumentNullException(nameof(compressors));
        }
        
        _compressors.AddRange(compressors);
        return this;
    }

    /// <summary>
    /// Adds an encrypter to the encryption stack
    /// </summary>
    /// <param name="encryptor">Encryptor to add</param>
    /// <returns>Current EncryptionStackBuilder instance.</returns>
    public EncryptionStackBuilder AddEncryptor(IEncrypter encryptor)
    {
        _encryptors.Add(encryptor);
        return this;
    }

    /// <summary>
    /// Adds multiple encryptors to the EncryptionStack
    /// </summary>
    /// <param name="encryptors">All encryptors to add</param>
    /// <returns>Current EncryptionStackBuilder instance.</returns>
    public EncryptionStackBuilder AddEncryptors(params IEncrypter[] encryptors)
    {
        if (encryptors is null || encryptors.Length == 0)
        {
            throw new ArgumentNullException(nameof(encryptors));
        }
        
        _encryptors.AddRange(encryptors);
        return this;
    }

    /// <summary>
    /// Sets the Byte-to-String conversion method
    /// </summary>
    /// <param name="byteStringConverter">Byte-String conversion method</param>
    /// <returns>Current EncryptionStackBuilder instance.</returns>
    public EncryptionStackBuilder SetByteStringConverter(IByteStringConverter byteStringConverter)
    {
        if (_hasBeenSet)
        {
            throw new WarningException("The byteStringConverter has already been set.");
        }
        
        _hasBeenSet = true;
        
        _byteStringConverter = byteStringConverter;
        return this;
    }

    /// <summary>
    /// Returns the built EncryptionStack
    /// </summary>
    /// <returns>Completed EncryptionStack</returns>
    public EncryptionStack Build()
    {
        if (_compressors.Count == 0) throw new InvalidOperationException("No compressors have been set.");
        if (_encryptors.Count == 0) throw new InvalidOperationException("No encryptors have been set.");
        
        return new EncryptionStack(_compressors.ToArray(), _encryptors.ToArray(), _byteStringConverter);
    }
}