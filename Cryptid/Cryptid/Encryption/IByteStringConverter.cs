namespace Cryptid.Encryption;

public interface IByteStringConverter
{
    public byte[] ToBytes(string value);
    
    public string ToString(byte[] bytes);
}