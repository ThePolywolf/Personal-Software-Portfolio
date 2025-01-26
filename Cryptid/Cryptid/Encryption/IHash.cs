namespace Cryptid.Encryption;

public interface IHash
{
    public byte[] Encrypt(byte[] data);
}