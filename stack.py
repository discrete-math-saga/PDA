# %%
from collections import deque
from typing import TypeVar, Generic, Sequence

T = TypeVar("T")


class Stack(Generic[T]):
    """
    Stack class
    """

    def __init__(self, data = None):  # Constructor
        self.elements: deque[T] = deque()
        if data is not None:
            if isinstance(data, 'Stack'):
                self.elements = deque(data.elements)
            elif isinstance(data, Sequence):
                for e in data:
                    self.push(e)
            else:
                raise ValueError("Invalid data type")
            
    def is_empty(self) -> bool:  # Return True if no element
        return len(self.elements) == 0

    def push(self, e: T) -> None:  # Add an element
        self.elements.append(e)

    def pop(self) -> T:  # Take out an element. The element is removed
        return self.elements.pop()

    def peek(self) -> T:  # Inspect the top element
        return self.elements[-1]

    def size(self) -> int:  # Return the number of elements
        return len(self.elements)

    def __str__(self) -> str:  # Return the string representation of the stack
        return f'[{",".join(map(str, self.elements))}]'
    
    def reversed(self) -> 'Stack[T]':
        """
        Return the reversed stack
        """
        new_stack:Stack[T] = Stack()
        for e in self.elements:
            new_stack.push(e)
        return new_stack


def palindrome(inputStr: str) -> bool:
    """
    return true if inputStr is palindrome
    recursive method
    """
    if len(inputStr) <= 1:
        return True
    if inputStr[0] != inputStr[-1]:
        return False
    return palindrome(inputStr[1:-1])


def palindrome2(inputStr: str) -> bool:
    """
    return true if inputStr is palindrome
    non-recursive method
    """
    myStack: Stack[str] = Stack()
    n: int = len(inputStr)
    m: int = n // 2
    for i in range(m):  # Push the first half onto the stack
        myStack.push(inputStr[i])
    if n % 2 != 0:  # If the length is odd
        m += 1
    for j in range(m, n):  # Compare the second half with the stack
        c: str = myStack.pop()
        if c != inputStr[j]:
            return False
    return True



def testing_stack()->None:
    myStack: Stack[str] = Stack()
    myStack.push("a")
    myStack.push("b")
    myStack.push("b")
    print(myStack)
    print(myStack.peek())

    myStack.pop()
    myStack.pop()
    print(myStack)


def test_palindrome()->None:
    s = "100001"
    palindrome(s)

if __name__ == "__main__":
    testing_stack()
    test_palindrome()