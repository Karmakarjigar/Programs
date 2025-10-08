using System;

namespace SwitchAndCase
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.Write("Enter your age: ");
            int age = Convert.ToInt32(Console.ReadLine());

            switch(age)
            {
                case 18:
                    Console.WriteLine("You are 18 wait for 1 year");
                    break;

                case 20:
                    Console.WriteLine("You are Drive");
                    break;

                default:
                    Console.WriteLine("Enjoy You can anything");
                    break;
            }
        }
    }
}
