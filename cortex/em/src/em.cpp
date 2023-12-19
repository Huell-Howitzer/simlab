#include <iostream>
#include <chrono>
#include <thread>

void spin(int delay_ms) {
    while (true) {
        // Your spin logic here
        std::cout << "Spinning..." << std::endl;

        // Sleep for the specified delay in milliseconds
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    }
}

int main() {
    int delay_ms = 1000; // Set the delay to 1000 milliseconds (1 second)

    // Start the spin function with the specified delay
    spin(delay_ms);

    return 0;
}
