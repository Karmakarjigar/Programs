// i other player class code

using System;

namespace OOPs_Programminh
{
    internal class Player
    {
        public string name = "Jigar";
        public int health = 48;
    }
}

// main class

using System;

namespace OOPs_Programminh
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Player jay = new Player();
            Console.WriteLine(jay.health);
        }
    }
}
