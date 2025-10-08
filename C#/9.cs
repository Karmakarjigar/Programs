using System;

namespace Function
{
    internal class Program
    {
        //static void greet()
        //{
        //    Console.WriteLine("Hello Brother!");
        //}
        //static void greet(string name)
        //{
        //    Console.WriteLine($"Hello {name}!");
        //}

        static int average(int a, int b,int c)
        {
            int sum = a + b + c;
            int avg = sum / 3;
            return avg;
        }
        static void Main(string[] args)
        {
            //Console.Write("Enter your name: ");
            //string name = Console.ReadLine();
            //string name1 = name.ToLower();
            //greet(name1);

            int a, b, c;
            Console.Write("Enter first number: ");
            a = Convert.ToInt32(Console.ReadLine());

            Console.Write("Enter Second number: ");
            b = Convert.ToInt32(Console.ReadLine());

            Console.Write("Enter Third number: ");
            c = Convert.ToInt32(Console.ReadLine());

            Console.WriteLine(average(a, b, c));

        }
    }
}
