#!/bin/python3

from Mailer_v2 import Mailer
import time
import socket
import sys
sys.path.insert(0, 'SE/GPUScheduling-master/monitor_client')
from MonitorClient import MonitorClient

def exception(user):
    try:
        with open('/home/s1309773/SE/GPUScheduling-master/Mailer/exceptions', 'r') as file:
            for line in file:
                if user == line:
                    return True
                    break
    except IOError as e:
        print(e)
        print('exeptions does not exist. Creating empty exeptions file.')
        f = open('/home/s1309773/SE/GPUScheduling-master/Mailer/exceptions', 'w+')
        f.close();
    return False

def main():
    monitor_client = MonitorClient('/home/s1485873/monitor.socket')
    mailer = Mailer()
    host = socket.gethostname().split('.',1)[0]
    
    notified = {}
    while True:
        violations = {}
        pids = set()
        for proc in monitor_client.get_process_data():
            # Process running on multiple devices
            if proc['pid'] in pids: 
                violations[proc['pid']] = (1, proc['username'], proc['fullname'], host) 
            else:
                pids.add(proc['pid'])
            sec_running = time.time() - float(proc['proc_birth'])
            
            # Process running for a long period of time
            if sec_running > 3600:
                violations[proc['pid']] = (2, proc['username'], proc['fullname'], host)
            
            
        if not violations:
            print("There have been no violations")
        else:
            print("violations detected!")
        for pid in violations:
            user = violations[pid][1]
            last_hours = 999
            if user in notified: 
                last_hours = (notified[user] - time.time())/3600
            if last_hours > 24:
                if not exception(user):
                    if user == 's1309773': 
                        mailer.sendamail(*violations[pid])
                        print(user + " has been notified.")
                        print("last notification was " + str(last_hours) + " ago.")
                    notified[user] = time.time()
        
        time.sleep(10.0)
        
if __name__ == '__main__':
    main()