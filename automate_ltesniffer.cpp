#include <cstdlib>
#include <iostream>
#include <string>

int main() {
    // Define the command to execute automate_ltesniffer
    std::string ltesniffer_command = "./automate_ltesniffer";

    // Execute the command
    int return_code = std::system(ltesniffer_command.c_str());

    // Check if the command executed successfully
    if (return_code == 0) {
        std::cout << "automate_ltesniffer executed successfully." << std::endl;
    } else {
        std::cerr << "Error executing automate_ltesniffer." << std::endl;
    }

    return 0;
}
