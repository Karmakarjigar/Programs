using System;

namespace math
{
    internal class Program
    {
        static void Main(string[] args)
        {
            int a, b;
            Console.Write("Write first number: ");
            a = Convert.ToInt32(Console.ReadLine());

            Console.Write("Write Second number: ");
            b = Convert.ToInt32(Console.ReadLine());

            // Arithmatic Operation
            int add = a + b;
            int sub = a - b;
            int div = a / b;
            int multi = a * b;

            Console.WriteLine("Addition of " + a + " + " + b + ": " + add);
            Console.WriteLine("Subtraction of " + a + " - " + b + ": " + sub);
            Console.WriteLine("Division of " + a + " / " + b + ": " + div);
            Console.WriteLine("Multiplication of " + a + " * " + b + ": " + multi);
        }
    }
}
