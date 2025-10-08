#include <iostream>

#define SIZE 5

class stack
{
public:
	int arr[SIZE], top;

	stack()
	{
		top = -1;
	}

	void push(int x)
	{
		if (top >= 4)
		{
			std::cout << "Stack Overflow" << "\n";
		}
		else
		{
			arr[++top] = x;
		}
	}
	void pop()
	{
		if (top == -1)
		{
			std::cout << "################# Stack Empty #################";
		}
		else
		{
			std::cout << "\nPopped Value: " << arr[top] << "\n";
			arr[top] = 0;
			top--;
		}
	}
	void display()
	{
		int i;
		for (i = 0; i <= top; i++)
		{
			std::cout << arr[i] << "\n";
		}
	}
};

int main()
{
	stack obj1;
	int choice, i, x;

	do
	{
		std::cout << "\n-------------------------\n";
		std::cout << "1. Push\n2. Pop\n3. Display\n4. Exit\nEnter your choice: ";
		std::cin >> choice;
		switch (choice)
		{
			case 1:
				for (i = 0; i < SIZE; i++)
				{
					std::cout << "Enter Value: ";
					std::cin >> x;
					obj1.push(x);
				}
				break;

			case 2:
				obj1.pop();
				break;

			case 3:
				obj1.display();
				break;

			case 4:
				std::cout << "Exit";
				break;
		}

	} while (choice != 4);
	
	std::cout << "\n";
	return 0;
}