using System;

namespace If_else
{
    internal class Program
    {
        static void Main(string[] args)
        {
            /*int age;
            Console.Write("Enter your age: ");
            age = Convert.ToInt32(Console.ReadLine());

            if(age == 18)
            {
                Console.WriteLine("You are valid to drive");
            }
            else if(age > 20)
            {
                Console.WriteLine("You cannot Drive");
            }*/
            int input;
            try
            {
                Console.Write("Enter an Numeber");
                input = Convert.ToInt32(Console.ReadLine());

                if (input >= 0)
                {
                    Console.WriteLine($"{input}is an Positive");
                }
                else if (input < 0)
                {
                    Console.WriteLine($"{input} is an Negative");
                }
                else
                {
                    Console.WriteLine("You inputed Zero");
                }
            }
            catch(FormatException)
            {
                Console.WriteLine("Invalid input only numbers");

            }



        }
    }
}
