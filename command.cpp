#include <iostream>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <ctime>
#include <iomanip>
#include <sstream>
#include <cstdio>

std::string getCurrentTimeString() {
    // Get current time
    std::time_t now = std::time(nullptr);

    // Convert to local time
    std::tm localTime = *std::localtime(&now);

    // Format the time string
    std::stringstream ss;
    ss << std::put_time(&localTime, "%Y-%m-%d_%H-%M-%S");
    return ss.str();
}

int main() {
    // Define the command to execute
    std::string command = "/home/purva/lte-B210/build/src/LTESniffer -A 1 -W 6 -f 1820e6 -C -m 0 -a \"num_recv_frames=512\"";

    // Destination directory for .pcap files
    std::string destination_directory = "/home/purva/Videos/test_B210/";

    // Iterate 2 times
    for(int i = 1; i <= 2; ++i) {
        // Execute the command with a timeout of 30 seconds
        std::string timeout_command = "timeout 120s " + command;
        std::system(timeout_command.c_str());

        // Move the file
        std::string source = "/home/purva/vs-code/ltesniffer_dl_mode.pcap";

        // Generate destination .pcap file name with current time string
        std::string current_time_str = getCurrentTimeString();
        std::string destination_pcap = destination_directory + "B210_DL_" + current_time_str + ".pcap";

        if (std::rename(source.c_str(), destination_pcap.c_str()) == 0) {
            std::cout << "File " << i << " moved successfully to " << destination_pcap << std::endl;
        } else {
            std::cerr << "Error moving file " << i << "!" << std::endl;
        }

        // Add a 10-second buffer time between iterations
        if (i < 2) {
            std::this_thread::sleep_for(std::chrono::seconds(20));
        }
    }

    // Terminate the terminal
    std::system("kill -9 $$");

    return 0;
}
