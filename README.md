
# LTESniffer - An Open-source LTE Downlink/Uplink Eavesdropper

**LTESniffer** is An Open-source LTE Downlink/Uplink Eavesdropper 

It first decodes the Physical Downlink Control Channel (PDCCH) to obtain the Downlink Control Informations (DCIs) and Radio Network Temporary Identifiers (RNTIs) of all active users. Using decoded DCIs and RNTIs, LTESniffer further decodes the Physical Downlink Shared Channel (PDSCH) and Physical Uplink Shared Channel (PUSCH) to retrieve uplink and downlink data traffic.

LTESniffer supports an API with three functions for security applications and research. Many LTE security research assumes
a passive sniffer that can capture privacy-related packets on the air. However, non of the current open-source sniffers satisfy their requirements as they cannot decode protocol packets in PDSCH and PUSCH. We developed a proof-of-concept security API that supports three tasks that were proposed by previous works: 1) Identity mapping, 2) IMSI collecting, and 3) Capability profiling.

Please refer to our [paper][paper] for more details.

## LTESniffer in layman's terms
LTESniffer is a tool that can capture the LTE wireless messages that are sent between a cell tower and smartphones connected to it. LTESniffer supports capturing the messages in both directions, from the tower to the smartphones, and from the smartphones back to the cell tower.

LTESniffer **CANNOT DECRYPT** encrypted messages between the cell tower and smartphones. It can be used for analyzing unencrypted parts of the communication between the cell tower and smartphones. For example, for encrypted messages, it can allow the user to analyze unencrypted parts, such as headers in MAC and physical layers. However, those messages sent in plaintext can be completely analyzable. For example, the broadcast messages sent by the cell tower, or the messages at the beginning of the connection are completely visible.

## Ethical Consideration

The main purpose of LTESniffer is to support security and analysis research on the cellular network. Due to the collection of uplink-downlink user data, any use of LTESniffer must follow the local regulations on sniffing the LTE traffic. We are not responsible for any illegal purposes such as intentionally collecting user privacy-related information.

## Features
### New Update v2.1.0
- Supports recording IQ raw data of subframes to file. Please refer to `LTESniffer-record-subframe` branch and its [README][capture-readme] for more details.
- Supports offline decoding using recorded files ([README][capture-readme]).
- Enable API in the downlink mode (only apply for identity collecting and mapping API)
### New Update v2.0.0
- Supports two USRP B-series for uplink sniffing mode. Please refer to `LTESniffer-multi-usrp` branch and its [README][multi-readme] for more details.
- Fixed some bugs.

LTESniffer is implemented on top of [FALCON][falcon] with the help of [srsRAN][srsran] library. LTESniffer supports:
- Real-time decoding LTE uplink-downlink control-data channels: PDCCH, PDSCH, PUSCH
- LTE Advanced and LTE Advanced Pro, up to 256QAM in both uplink and downlink
- DCI formats: 0, 1A, 1, 1B, 1C, 2, 2A, 2B
- Transmission modes: 1, 2, 3, 4
- FDD only (Note: try with TDD, it is working)
- Maximum 20 MHz base station. 
- Automatically detect maximum UL/DL modulation schemes of smartphones (64QAM/256QAM on DL and 16QAM/64QAM/256QAM on UL)
- Automatically detect physical layer configuration per UE.
- LTE Security API: RNTI-TMSI mapping, IMSI collecting, UECapability Profiling.

## Hardware and Software Requirement
### OS Requirement
Currently, LTESniffer works stably on Ubuntu 18.04/20.04/22.04.

### Hardware Requirement
Achieving real-time decoding of LTE traffic requires a high-performance CPU with multiple physical cores, especially during peak hours when the base station has many active users. LTESniffer successfully achieved real-time decoding when deployed on an Intel i7-9700K PC, decoding traffic from a base station with 150 active users.

**The following hardware is recommended**
- Intel i7 CPU with at least 8 physical cores
- At least 16Gb RAM
- 256 Gb SSD storage
### SDR
LTESniffer requires different SDR for its uplink and downlink sniffing modes.

To sniff only downlink traffic from the base station, LTESniffer is compatible with most SDRs that are supported by the srsRAN library (for example, USRP or BladeRF). The SDR should be connected to the PC via a USB 3.0 port. Also, it should be equipped with GPSDO and two RX antennas to decode downlink messages in transmission modes 3 and 4.

On the other hand, to sniff uplink traffic from smartphones to base stations, LTESniffer needs to listen to two different frequencies (Uplink and Downlink) concurrently. To solve this problem, LTESniffer supports two options:
- Using a single USRP X310 and USRP N310. USRP X310 has two Local Oscillators (LOs) for 2 RX channels, which can turn each RX channel to a distinct Uplink/Downlink frequency. To use this option, please refer to the `main` branch of LTESniffer.
- Using 2 USRP B-Series. LTESniffer utilizes 2 USRP B-series (B210/B200) for uplink and downlink separately. It achieves synchronization between 2 USRPs by using GPSDO for clock source and time reference. To use this option, please refer to the `LTESniffer-multi-usrp` branch of LTESniffer and its [README][multi-readme].

## Installation
**Important note: To avoid unexpected errors, please follow the following steps on Ubuntu 18.04/20.04/22.04.**

**Dependencies**
- **Important dependency**: [UHD][uhd] library version >= 4.0 must be installed in advance (recommend building from source). The following steps can be used on Ubuntu 18.04. Refer to UHD Manual for full installation guidance. 

UHD dependencies:
```bash
sudo apt update
sudo apt-get install autoconf automake build-essential ccache cmake cpufrequtils doxygen ethtool \
g++ git inetutils-tools libboost-all-dev libncurses5 libncurses5-dev libusb-1.0-0 libusb-1.0-0-dev \
libusb-dev python3-dev python3-mako python3-numpy python3-requests python3-scipy python3-setuptools \
python3-ruamel.yaml
```
Clone and build UHD from source (make sure that the current branch is higher than 4.0)
```bash
git clone https://github.com/EttusResearch/uhd.git
cd <uhd-repo-path>/host
mkdir build
cd build
cmake ../
make -j 4
make test
sudo make install
sudo ldconfig
```
Download firmwares for USRPs:
```bash
sudo uhd_images_downloader
```
We use a [10Gb card](https://www.ettus.com/all-products/10gige-kit/) to connect USRP X310 to PC, refer to UHD Manual [[1]](https://files.ettus.com/manual/page_usrp_x3x0.html), [[2]](https://files.ettus.com/manual/page_usrp_x3x0_config.html) to configure USRP X310 and 10Gb card interface. For USRP B210, it should be connected to PC via a USB 3.0 port.

Test the connection and firmware (for USRP X310 only):
```bash
sudo sysctl -w net.core.rmem_max=33554432
sudo sysctl -w net.core.wmem_max=33554432
sudo ifconfig <10Gb card interface> mtu 9000
sudo uhd_usrp_probe
```

- srsRAN dependencies:
```bash
sudo apt-get install build-essential git cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev
```

- LTESniffer dependencies:
```bash
sudo apt-get install libglib2.0-dev libudev-dev libcurl4-gnutls-dev libboost-all-dev qtdeclarative5-dev libqt5charts5-dev
```

**Build LTESniffer from source:**
```bash
git clone https://github.com/SysSec-KAIST/LTESniffer.git
cd LTESniffer
mkdir build
cd build
cmake ../
make -j 4 (use 4 threads)
```
**Build automate_LTESniffer:**
```bash
Download pycharm community from "https://www.jetbrains.com/pycharm/download/?section=windows"
Download "Automate_LTESniffer.py" and add to the folder of pycharm
Or open using pycharm community
Change the following according to your usage (We acquired the data for 48 hours with individual frequency bands and operators):

command = '/home/purva/lte-B210/build/src/LTESniffer -A 1 -W 6 -f 1870e6 -C -m 0 -a "num_recv_frames=512"'
source_pcap_template = "/home/purva/Videos/test/Automate_LTE/ltesniffer_dl_mode.pcap"
destination_directory = "/home/purva/Videos/test_B210/"

time.sleep(3600)   #1 hour sniffing

destination_pcap = f"{destination_directory}B210_DL_{current_time}.pcap"

# Number of iterations and pcap files
num_iterations = 48 #48 hour data acquisition
```

**Build automate_LTESniffer from application:**
```bash
Download the "automate_ltesniffer" file and start in the terminal with the following command:

./automate_ltesniffer

for change in the command line, you can download "command.cpp" file and write in the terminal:
nano command.cpp
---> Modify following lines as per your application:
 // Define the command to execute
    std::string command = "/home/purva/lte-B210/build/src/LTESniffer -A 1 -W 6 -f 1870e6 -C -m 0 -a \"num_recv_frames=512\"";
 // Destination directory for .pcap files
    std::string destination_directory = "/home/purva/Videos/test_B210/";
 // Iterate 2 times ## change this according to the number of iterations for example 48 hours will give 48 iterations
    for(int i = 1; i <= 2; ++i) {
        // Execute the command with a timeout of 3600 seconds
        std::string timeout_command = "timeout 3600s " + command; ### change time in seconds as per the requirements.
        std::system(timeout_command.c_str());

        // Move the file
        std::string source = "/home/purva/vs-code/ltesniffer_dl_mode.pcap"; #change the directory path 
---> Ctrl+x to exit and save the file.
g++ -o automate_ltesniffer command.cpp -pthread
chmod +x automate_ltesniffer
./automate_ltesniffer

```
## Credits
We sincerely appreciate the [FALCON][falcon], [LTESniffer](https://github.com/SysSec-KAIST/LTESniffer) and [SRS team][srsran] for making their great software available.

Note: We would like to mention that LTESniffer and its code were developed by Hoang D. Tuan and their Laboratory team from SysSec-KAIST, Korea. We appreciate the time, help and efforts from **Hoang D Tuan**. 


## Approach and methodology:
We only modified as per our configurations of hardware which are USRP B210 and USRP N310. Also, we use **Downlink LTESniffer** for 48-hour downlink data acquisition and specific data extraction from JSON file to CSV file for traffic analysis between mobile phones and cellular towers. We also gathered LTE-TDD traffic with 24-hour data acquisition. We also created a C++ file to run the command and save downlink .PCAP file, which can be changed or modified according to specific use or applications. By evaluating 48-hour data acquisition in downlink mode, one can analyze the traffic patterns between mobile phones (UEs) which are commercial cellular SIM cards and base stations (mobile towers). There are two limitations in uplink sniffing for a longer time, in non-working hours any specific mobile should be placed near to antenna or ltesniffer, so we did not try or develop the same method for uplink sniffer. 

[falcon]: https://github.com/falkenber9/falcon
[srsran]: https://github.com/srsran/srsRAN_4G
[uhd]:    https://github.com/EttusResearch/uhd
[paper]:  https://syssec.kaist.ac.kr/pub/2023/wisec2023_tuan.pdf
[pcap]:   pcap_file_example/README.md
[app]:    https://play.google.com/store/apps/details?id=make.more.r2d2.cellular_z&hl=en&gl=US&pli=1
[watching]: https://syssec.kaist.ac.kr/pub/2022/sec22summer_bae.pdf
[multi-readme]: https://github.com/SysSec-KAIST/LTESniffer/tree/LTESniffer-multi-usrp
[capture-readme]: https://github.com/SysSec-KAIST/LTESniffer/tree/LTESniffer-record-subframe
[cellular77]: https://github.com/cellular777
[Cemaxecuter]: https://www.youtube.com/@cemaxecuter7783
