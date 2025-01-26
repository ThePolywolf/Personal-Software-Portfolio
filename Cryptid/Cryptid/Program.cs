using System.Text;
using Cryptid.Encryption;

namespace Cryptid;

class Program
{
    private enum ActionTypes
    {
        Encrypt,
        Decrypt
    }
    
    static void Main(string[] args)
    {
        Console.WriteLine("Booting up Cryptid");
        
        MainWithArgs(args);
    }

    private static void MainWithArgs(string[] args)
    {
        if (args.Length < 1 || args[0] == "--help")
        {
            Console.WriteLine("Usage: Cryptid [<action>] [<file path>]");
            return;
        }

        if (args[0].ToLower() == "manual")
        {
            MainManualInput();
            return;
        }

        var action = args[0].ToLower() switch
        {
            "encrypt" => ActionTypes.Encrypt,
            "decrypt" => ActionTypes.Decrypt,
            _ => throw new ArgumentException()
        };
        
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: Cryptid [<action>] [<file path>]");
            return;
        }

        var fileName = args[1];
        if (!File.Exists(fileName))
        {
            Console.WriteLine($"File {fileName} does not exist");
            return;
        }
        
        var fileContents = File.ReadAllText(fileName);
        byte[] byteArray;

        var compressor = new HuffmanCompressor();
        if (action == ActionTypes.Encrypt)
        {
            byteArray = Encoding.UTF8.GetBytes(fileContents);
            var encryption= compressor.Encrypt(byteArray);
            var encryptionString = Convert.ToBase64String(encryption);
            var encryptedFileName = $"{fileName}_{DateTime.Now:yyMMdd_HHmmss}.enc";
            File.WriteAllText(encryptedFileName, encryptionString);
            
            Console.WriteLine($"Encrypted file => {encryptedFileName}");
        }
        
        if (action == ActionTypes.Decrypt)
        {
            byteArray = Convert.FromBase64String(fileContents);
            var decryption = compressor.Decrypt(byteArray);
            var decryptionString = Encoding.UTF8.GetString(decryption);
            var decryptedFileName = $"{fileName}_{DateTime.Now:yyMMdd_HHmmss}.dec";
            File.WriteAllText(decryptedFileName, decryptionString);
            
            Console.WriteLine($"Decrypted file => {decryptedFileName}");
        }
    }

    private static void MainManualInput()
    {
        Console.Write("Enter some text: ");
       
        var input = Console.ReadLine();
        var comp = new HuffmanCompressor();

        if (input is null)
            throw new Exception();
        
        Console.WriteLine("Encrypt? (y/n)");
        if (Console.ReadLine()?.ToLower() is "y")
        {
            var encryption = comp.ForceEncrypt(Encoding.UTF8.GetBytes(input));
            Console.WriteLine(Convert.ToBase64String(encryption));
        }
        else
        {
            var decryption = comp.Decrypt(Convert.FromBase64String(input));
            Console.WriteLine(Encoding.UTF8.GetString(decryption));
        }
    }
}