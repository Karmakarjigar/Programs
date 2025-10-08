using System;

namespace Loop1
{
    internal class Program
    {
        static void Main(string[] args)
        {
            int i = 0;
            for(i = 1; i <= 10; i++)
            {
                Console.WriteLine("*");
            }
            Console.WriteLine("--------------------");
            i = 1;

            while(i < 10)
            {
                Console.WriteLine("+");
                i++;    
            }
            Console.WriteLine("--------------------");
            i = 1;
            do
            {
                Console.WriteLine("-");
                i++;
            } while (i < 10);
        }
    }
}
