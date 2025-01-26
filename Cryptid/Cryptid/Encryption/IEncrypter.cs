namespace Cryptid.Encryption;

public interface IEncrypter
{
    public byte[] Encrypt(byte[] bytes);
    
    public byte[] Decrypt(byte[] cipherText);
}