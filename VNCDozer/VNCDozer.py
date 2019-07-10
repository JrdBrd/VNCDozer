import os
from multiprocessing import *
import time
from datetime import datetime
from vncdotool import api
import argparse

# Dozer VNC Scraper v0.1
# (c) 2019 JrdBrdDev

# Setup command line args
parser = argparse.ArgumentParser(description="Open/Unsafe VNC Web Scraper", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-input", help="IP list input file", default="iplist.txt", metavar="FILE")
parser.add_argument("-port", help="VNC server port", type=int, default=5900)
parser.add_argument("-proc_count", help="Multithreaded process count", type=int, default=50, metavar="COUNT")
parser.add_argument("-connect_timeout", help="VNC connection timeout in seconds", type=int, default=15, metavar="T")
parser.add_argument("-screen_timeout", help="Screenshot attempt timeout in seconds", type=int, default=120, metavar="T")
parser.add_argument("--no_screenshots", help="Disable server screenshots", action="store_true")
parser.add_argument("--no_passwords", help="Disable basic password checks", action="store_true")
args = parser.parse_args()

##print(args)

# Parse input args
ip_file = args.input
vncport = str(args.port)
proc_count = args.proc_count
connection_timeout = args.connect_timeout
screenshot_timeout = args.screen_timeout
take_screenshots = not args.no_screenshots
try_passwords = not args.no_passwords

# Define file urls
timestring = time.strftime("%Y-%m-%d_%H:%M:%S")
password_file = "./passwords.txt"
valid_ipfile = f"./results/{timestring}/validips.txt"
password_ipfile = f"./results/{timestring}/passwordips.txt"

# Create optional variables
if try_passwords:
    passwords = [line.strip for line in open(password_file)]

print(valid_ipfile)