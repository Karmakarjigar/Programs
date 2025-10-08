using System;
namespace input;
internal class Input
{
    static void Main(String[] args)
    {
        Console.Write("Enter Your Number: ");
        int a = Convert.ToInt32(Console.ReadLine());
        Console.WriteLine("Your Number: " + a);

        Console.Write("Enter Your Name: ");
        String a = Console.ReadLine()!;
        Console.WriteLine("Your Name: " + a);
    }
}