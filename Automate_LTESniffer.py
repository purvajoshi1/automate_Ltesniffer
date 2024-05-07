import subprocess
import shutil
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
from dateutil import parser


class NoPacketsCapturedError(Exception):
    pass


def acquire_data_and_save_pcap(iteration):
    command = '/home/purva/lte-B210/build/src/LTESniffer -A 1 -W 6 -f 1870e6 -C -m 0 -a "num_recv_frames=512"'
    source_pcap_template = "/home/purva/Videos/test/Automate_LTE/ltesniffer_dl_mode.pcap"
    destination_directory = "/home/purva/Videos/test_B210/"
    current_time = time.strftime("%Y-%m-%d.%H-%M")

    subprocess.run(['gnome-terminal', '--', 'bash', '-c', f'sudo {command}; exec bash'])

    time.sleep(40)   #1 hour sniffing

    subprocess.run(['pkill', '-f', f'sudo {command}'])

    destination_pcap = f"{destination_directory}B210_DL_Voda_B3_{current_time}.pcap"
    shutil.move(source_pcap_template, destination_pcap)

    return destination_pcap


def convert_pcap_to_json(pcap_file):
    output_json_file = f"{pcap_file}.json"
    subprocess.run(['tshark', '-r', pcap_file, '-T', 'json'], stdout=open(output_json_file, 'w'))
    return output_json_file


def extract_tmsi_to_csv(json_file, iteration):
    time_tmsi_dict = {}

    with open(json_file, 'rt') as myfile:
        timestamp = None
        tmsi_values = []

        for myline in myfile:
            timestamp_match = myline.find('"frame.time": "')
            if timestamp_match != -1:
                if timestamp is not None and tmsi_values:
                    time_tmsi_dict[timestamp] = {"values": tmsi_values.copy(), "count": len(tmsi_values)}

                timestamp_start = timestamp_match + len('"frame.time": "')
                timestamp_end = myline.find('"', timestamp_start)
                timestamp_full = myline[timestamp_start:timestamp_end]
                timestamp_parsed = parser.parse(timestamp_full)
                timestamp = timestamp_parsed.strftime('%b %d, %Y %H:%M:%S.%f')[:-3]
                tmsi_values = []

            tmsi_match = myline.find('"lte-rrc.m_TMSI": "')
            if tmsi_match != -1:
                tmsi_start = tmsi_match + len('"lte-rrc.m_TMSI": "')
                tmsi_end = myline.find('"', tmsi_start)
                tmsi_value = myline[tmsi_start:tmsi_end]
                tmsi_values.append(tmsi_value)

        if timestamp is not None and tmsi_values:
            time_tmsi_dict[timestamp] = {"values": tmsi_values.copy(), "count": len(tmsi_values)}

    csv_file_path = f"{json_file}_TMSI_{iteration}.csv"
    with open(csv_file_path, 'w', newline='') as output_csv_file:
        csv_writer = csv.writer(output_csv_file)
        if time_tmsi_dict:  # Check if the dictionary is not empty
            max_count = max(len(data["values"]) for data in time_tmsi_dict.values())
        else:
            max_count = 0
        header_row = ["frame.time", "m_TMSI_count"] + [f"lte-rrc.m_TMSI_{i}" for i in range(1, max_count + 1)]
        csv_writer.writerow(header_row)

        for timestamp, data in time_tmsi_dict.items():
            tmsi_values = data["values"]
            count = data["count"]
            row_data = [f'"{timestamp}"', count] + [f'"{tmsi}"' for tmsi in tmsi_values]
            csv_writer.writerow(row_data)

    return csv_file_path

def merge_csv_files(csv_files):
    merged_df = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)
    return merged_df

# Number of iterations and pcap files
num_iterations = 2
pcap_files = []
csv_files = []

try:
    for iteration in range(1, num_iterations + 1):
        print(f"Iteration {iteration}:")

        pcap_file = acquire_data_and_save_pcap(iteration)
        pcap_files.append(pcap_file)

        json_file = convert_pcap_to_json(pcap_file)

        csv_file = extract_tmsi_to_csv(json_file, iteration)  # Update this line
        csv_files.append(csv_file)

        time.sleep(10)  # 5 min time delay


except Exception as e:
    print(f"An error occurred: {e}")

else:
    print("No CSV files to merge and plot.")
