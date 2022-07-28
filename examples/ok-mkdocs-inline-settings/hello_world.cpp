#include <iostream>

int main() {
  /** md file=main.md trim=2 stop="end-here"
  # Hello world
  
  This is the main function for hello world.
  It outputs "Hello World!" to the screen.

  end-here
  This shouldn't show up!
  **/
    std::cout << "Hello World!";
    return 0;
}
