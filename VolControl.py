#!/usr/bin/python3
# Imports
import re
from subprocess import call, check_output
import datetime
from time import sleep, strftime, localtime
import ntplib
import argparse

# Variables
start = datetime.time(0, 0, 0)
end = datetime.time(10, 0, 0)

ntp_client = ntplib.NTPClient()


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--state', default="go",
                    help='run state (default: normal run)')
parser.add_argument('--volume', default=80, type=int,
                    help='min volume (default: 80)')




def set_vol(amount):
    """Controls the volume via amixer call
    Parameters:
    amount (int): Amount in % 
    operator (String): + or -
    """
    call(["amixer", "-D", "pulse", "sset", "Master", str(amount) + "%"])


def get_vol():
    o = check_output("amixer -D pulse sget Master", universal_newlines=True, shell=True)
    out = re.search(r"\d*%", o)
    return out.group().replace('%', '')


def time_in_range(start, end, current):
    return start <= current <= end

def get_ntptime(ntp_client):
    try:
        response = ntp_client.request('0.de.pool.ntp.org')
        time = datetime.datetime.fromtimestamp(response.tx_time).time()
    except ntplib.NTPException as ntpe:
        print(ntpe)
        time = datetime.datetime.now().time()
        print('Could not sync with time server')
    return time

def ntp_time():
    pass

def main(args):

    tracker=100

    while args.state == "test":
        cmd =input("command:")
        
        if  cmd == "get_vol":
            print(get_vol())

        if cmd == "set_vol":
            if time_in_range(start, end, datetime.datetime.now().time()):

                if int(get_vol()) > args.volume:
                    tracker = tracker - 1
                    set_vol(tracker)
                    print("sleep for 15 secs")
                    sleep(15)
                    print("woke up")

            else:
                tracker = 100

        if cmd == "check_time":
            print(time_in_range(start, end, get_ntptime(ntp_client)))

        if cmd == "tracker":
            print(tracker)
        
        if cmd == "quit":
            break
    

    while args.state == "go":
        if time_in_range(start, end, get_ntptime(ntp_client)):

            if int(get_vol()) > args.volume:
                tracker = tracker - 1
                set_vol(tracker)
                print("VolControl Active \n lowering Volume \n sleeping for 64 seconds")
                sleep(64)

            if tracker < args.volume:
                tracker = args.volume

        else:
            tracker = 100
            print("Inactive")
            sleep(64)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)


