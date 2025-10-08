using System;

namespace String_Function
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string a = "Gello";
            Console.WriteLine(a.Length);
            Console.WriteLine(a.ToUpper());
            Console.WriteLine(a.ToLower());
            // There are two method to do Concatinatiom
            //1.
            Console.WriteLine("Normal using plus: "+ a + "World");
            //2.
            Console.WriteLine("String Concatination: "+ string.Concat(a , "World"));
            // Both the code give same result
            // String interpolation
            Console.Write("Enter Your name: ");
            string name = Console.ReadLine();

            Console.WriteLine($"Nice To meet you {name}. Hpw can i help you");

            string b = "Hello World!";
            Console.WriteLine(b[0]);
            Console.WriteLine(b[1]);

        }
    }
}
