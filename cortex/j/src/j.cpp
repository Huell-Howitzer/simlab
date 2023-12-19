#include <iostream>
#include <chrono>
#include <thread>
#include <cstdlib>

int main() {
    const char* env_var_name = "MY_ENV_VAR"; // Change this to your environment variable name

    int delay_ms = 1000; // Set the delay to 1000 milliseconds (1 second)

    while (true) {
        // Get the environment variable value
        const char* env_var_value = std::getenv(env_var_name);

        if (env_var_value) {
            std::cout << "Environment variable '" << env_var_name << "' has the value: " << env_var_value << std::endl;
        } else {
            std::cerr << "Environment variable '" << env_var_name << "' is not set." << std::endl;
        }

        // Sleep for the specified delay in milliseconds
        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    }

    return 0;
}

