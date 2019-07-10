import os, sys
from multiprocessing import *
import time
from datetime import datetime
from vncdotool import api
import argparse

# Dozer VNC Scraper v0.1
# (c) 2019 JrdBrdDev

# Setup command line args
parser = argparse.ArgumentParser(description="Open/Unsafe VNC Web Scraper", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-input", help="IP list file", default="iplist.txt", metavar="FILE")
parser.add_argument("-pass_file", help="Password list file", default="passwords.txt", metavar="FILE")
parser.add_argument("-proc_count", help="Multithreaded process count", type=int, default=50, metavar="COUNT")
parser.add_argument("-connect_timeout", help="VNC connection timeout in seconds", type=int, default=15, metavar="T")
parser.add_argument("-screen_timeout", help="Screenshot attempt timeout in seconds", type=int, default=120, metavar="T")
parser.add_argument("--no_screenshots", help="Disable server screenshots", action="store_true")
parser.add_argument("--no_passwords", help="Disable basic password checks", action="store_true")
parser.add_argument("--verbose", help="Enable verbose logging", action="store_true")
args = parser.parse_args()

# Parse input args
ip_file = args.input
password_file = args.pass_file
proc_count = args.proc_count
connection_timeout = args.connect_timeout
screenshot_timeout = args.screen_timeout
take_screenshots = not args.no_screenshots
try_passwords = not args.no_passwords
verbose_logging = args.verbose

# Screencapture attempt function
# WILL RETURN AS FOLLOWS:
# {
#   "status": "success" OR "password_success" OR "no_screen" OR "no_screen_pass" OR "no_password" OR "failed",
#   "taken": time taken in seconds (float)
# }
def screencapture(ip):
    status = "failed"
    start_time = datetime.now()

    timestr = time.strftime("%Y%m%d-%H%M%S")
    screenshot_filename = ip + "_" + timestr + ".png"

    try:
        # Test unprotected connection
        client = api.connect(ip)
        client.timeout = connection_timeout
        client.connectionMade()
        print(f"Connection has been established to unprotected IP {ip}")
        
    end_time = datetime.now()
    return_dict = { "status": status, "taken": (start_time - end_time).total_seconds() }
    return return_dict

# MAIN PROCESS BELOW

# Define file urls
timestring = time.strftime("%Y-%m-%d_%H:%M:%S")
valid_ipfile = f"./results/{timestring}/validips.txt"
password_ipfile = f"./results/{timestring}/passwordips.txt"

# Create required variables
if not os.path.exists(ip_file):
    print(f"IP file \"{ip_file}\" does not exist, aborting...")
    sys.exit(1)
else:
    vncservers = [line.strip() for line in open(ip_file)]
    if len(vncservers) == 0:
        print(f"IP file \"{ip_file}\" is empty, aborting...")
        sys.exit(1)

screenshot_path = os.getcwd().replace('\\', '/') + "/results/screenshots/"
if not os.path.exists(screenshot_path):
    print("Screenshot output folder does not exist, creating...")
    os.makedirs(screenshot_path)

# Create optional variables
if try_passwords:
    if not os.path.exists(password_file):
        print(f"Password file \"{password_file}\" does not exist, continuing without password attempts")
        try_passwords = False
    else:
        passwords = [line.strip() for line in open(password_file)]
        if len(passwords) == 0:
            print(f"Password file \"{password_file}\" is empty, continuing without password attempts")
            try_passwords = False

# Process handler
if __name__ == "__main__":
    process_pool = Pool(processes=proc_count)
    result_list = process_pool.map(screencapture, vncservers)

    passed_amt = 0          # Successful connection & screenshot, unprotected
    password_amt = 0        # Successful connection & screenshot, protected
    no_screen_amt = 0       # Successful connection, failed screenshot, unprotected
    no_screen_amt_pass = 0  # Successful connection, failed screenshot, protected
    no_password_amt = 0     # Unsuccessful connection, password failed
    failed_amt = 0          # Unsuccessful connection, timed out

    for result in result_list:
        if result["status"] == "success":
            passed_amt += 1
        elif result["status"] == "password_success":
            password_amt += 1
        elif result["status"] == "no_screen":
            no_screen_amt += 1
        elif result["status"] == "no_screen_pass":
            no_screen_amt_pass += 1
        elif result["status"] == "no_password":
            no_password_amt += 1
        elif result["status"] == "failed":
            failed_amt += 1

    print(f"Connection to {passed_amt + no_screen_amt} unprotected servers were successful, and {passed_amt} were screenshotted")
    print(f"Connection to {password_amt + no_screen_amt_pass} password-protected servers were successful, and {password_amt} were screenshotted")
    print(f"Connection to {no_password_amt} password-protected servers failed on all passwords in the dict")
    print(f"Connection to {failed_amt} servers could not be established")