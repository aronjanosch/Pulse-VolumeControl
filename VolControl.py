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
stage1 = datetime.time(1, 0, 0)
end = datetime.time(2, 0, 0)
reset = datetime.time(10, 0, 0)

tracker = 100

ntp_client = ntplib.NTPClient()


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--state', default="go",
                    help='run state (default: normal run)')
parser.add_argument('--volume_s1', default=90, type=int,
                    help='s1 volume (default: 90)')
parser.add_argument('--volume_min', default=80, type=int,
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
    if ntp_client == None:
        return datetime.datetime.now().time()
    try:
        response = ntp_client.request('0.de.pool.ntp.org')
        time = datetime.datetime.fromtimestamp(response.tx_time).time()
    except Exception as ntpe:
        print(ntpe)
        time = datetime.datetime.now().time()
        print('Could not sync with time server')
    return time

def ntp_time():
    pass

def init_check(args):   
    time_now = get_ntptime(ntp_client)
    global tracker
    if time_in_range(start, stage1, time_now):
        tracker = args.volume_s1
        set_vol(tracker)
    elif time_in_range(stage1, end, time_now):
        tracker = args.volume_min
        set_vol(tracker)
    elif time_in_range(end, reset, time_now):
        tracker = 0
        set_vol(tracker)
    else:
        tracker = 100
        set_vol(tracker)
    sleep(64)

def main(args):
    global tracker 
    set_vol(tracker)

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
            
        if cmd == "check_time_stage1":
            print(time_in_range(stage1, end, get_ntptime(ntp_client)))

        if cmd == "tracker":
            print(tracker)
        
        if cmd == "quit":
            break
    

    while args.state == "go":
        time_now = get_ntptime(ntp_client)
        if time_in_range(start, stage1, time_now):

            if int(get_vol()) > args.volume_s1:
                tracker = tracker - 1
                set_vol(tracker)
                print("VolControl Active \n lowering Volume \n sleeping for 64 seconds")
                sleep(64)

            if tracker < args.volume_s1:
                tracker = args.volume_s1
                set_vol(tracker)
                
            if int(get_vol()) <= args.volume_s1:
                print("Threshold reached")
                sleep(64)
                
        elif time_in_range(stage1, end, time_now):

            if int(get_vol()) > args.volume_min:
                tracker = tracker - 1
                set_vol(tracker)
                print("VolControl Active \n lowering Volume \n sleeping for 64 seconds")
                sleep(64)

            if tracker < args.volume_min:
                tracker = args.volume_min
                set_vol(tracker)
                
            if int(get_vol()) <= args.volume_min:
                print("Threshold reached")
                sleep(64)
        elif time_in_range(end, reset, time_now):
            set_vol(0)
            sleep(64)

        else:
            tracker = 100
            print("Inactive")
            sleep(64)


if __name__ == "__main__":
    print("Starting Volume Control...")
    sleep(64)
    args = parser.parse_args()
    init_check(args)
    main(args)


