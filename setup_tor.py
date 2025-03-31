import subprocess
import re
import os

def generate_tor_confs(start_conf, n):
    if not os.path.exists("./tor_confs"):
        os.mkdir("tor_confs")
    for port in range(start_conf, start_conf + n * 2, 2):
        with open(f"tor_confs/{port}.conf", "w") as fout:
            fout.write(f"SocksPort {port}\nControlPort {port+1}\nDataDirectory ./tor_confs/{port}")

def start_tor_confs():
    try:
        if not os.path.exists("tor_confs"):
            generate_tor_confs(9050, 100)

        if not os.path.exists("tor_confs"):
            print("The 'tor_confs' directory does not exist.")
            return

        tor_processes = []

        for conf in os.listdir("tor_confs"):
            if conf.endswith(".conf"):
                conf_path = os.path.join("tor_confs", conf)
                print(f"Starting Tor with config: {conf_path}")
                tor_process = subprocess.Popen(["tor", "-f", conf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                tor_processes.append(tor_process)
                print(f"Successfully started Tor with {conf_path}")

            else:
                print(f"Skipping non-.conf file: {conf}")

    except Exception as e:
        print(f"Error starting Tor processes: {e}")

def stop_all_tor_processes():
    try:
        result = subprocess.run("ps aux | grep ' [t]or' | awk '{print $2}'", shell=True, capture_output=True, text=True)
        if result.stdout:
            tor_pids = result.stdout.strip().split('\n')
            for pid in tor_pids:
                pid = pid.strip()
                if pid:
                    print(f"Stopping Tor process with PID: {pid}")
                    subprocess.run(f"kill -9 {pid}", shell=True)
            print("All Tor processes stopped.")
        else:
            print("No Tor processes found.")
    
    except Exception as e:
        print(f"Error stopping Tor processes: {e}")

def get_open_tor_ports():
    """
    Retrieve all open Tor-related ports dynamically.
    Typically, Tor uses ports like 9050, 9051, 9052, etc. for SOCKS and control.
    """

    def extract_tor_ports(data):
        """
        Extracts the port numbers from the provided data.

        :param data: The raw data containing the list of tor processes.
        :return: A list of port numbers as strings.
        """
        tor_ports = []
        
        # Define regex pattern to match tor_confs/(port).conf
        pattern = r"tor_confs/(\d+)\.conf"
        
        # Split the data into lines and search for the pattern
        for line in data.splitlines():
            match = re.search(pattern, line)
            if match:
                tor_ports.append(int(match.group(1)))  # Extract only the port number
        
        return tor_ports



    try:
        # Use ps aux to find Tor-related processes
        result = subprocess.run("ps aux | grep tor_confs", shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error finding Tor-related processes.")
            return []

        tor_ports = extract_tor_ports(result.stdout)
        return tor_ports
    except Exception as e:
        print(f"Error retrieving Tor ports: {e}")
        return []