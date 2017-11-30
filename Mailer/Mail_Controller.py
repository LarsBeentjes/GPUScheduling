#!/bin/python3

from Mailer import Mailer
import time
import socket
import sys
from collections import Counter
from MonitorClient import MonitorClient

OwnPath = sys.path[0] + '/'			#Note change this to be compatible with where the program is actually invoked.
						#Is supposed to point to Mailer directory.
						#sys.path[0] points to where the program is initially called.
						#So if monitor is where the program is ultimately started.
						#Then it points to the monitor directory.
						#And we need to add /../Mailer/

def exception(user):
    try:
        with open(OwnPath + 'exceptions', 'r') as file:
            for line in file:
                if user == line:
                    return True
                    break
    except IOError as e:
        print(e)
        print('exeptions does not exist. Creating empty exeptions file.')
        f = open(OwnPath + 'exceptions', 'w+')
        f.close();
    return False

def main():
    monitor_client = MonitorClient('/home/s1485873/monitor.socket')	#Probably also needs to be changed, but not sure how.
    mailer = Mailer()
    host = socket.gethostname().split('.',1)[0]
    
    notified = {}
    while True:
        violations = {}
        pids = set()
        data = monitor_client.get_process_data()
        counted = Counter(data['pid'])			#I'm reasonably sure the monitor client returns a dictionary and that this should work.
							#But not entirely certain. Can someone check this?
							#Here for efficiency.					
        try:
            with open(OwnPath + 'Rules', 'r') as Rulesfile:
                for line in Rulesfile:
                    bool ruleapplies = False
                    bool isitall = False
                    helptext = line.split()
                    helptext2 = helptext
                    if(len(helptext) < 6):	#Thusly, might be a valid rule.
                        continue
                    if(isinstance(helptext[1], int) and isinstance(helptext[2], int) and isinstance(helptext[3], int) and isinstance(helptext[5], int)):
                        if(helptext[0] == 'ALL'):
                            isitall = True
                        else:
                            with open(OwnPath + 'Groups', 'r') as Groupsfile:
                                for grouplines in Groupsfile:
                                    grouphelp = grouplines.split()
                                    if(grouphelp[0] == helptext[0]): #The group name matches
                                        ruleapplies = True
                                        helptext2 = grouphelp
                                        break
                                    else:
                                        continue
                    else:
                        continue #Also checking if a valid rule.
                    if(ruleapplies or isitall):
                        for proc in data:
                            if((proc['username'] in helptext2) or isitall): #Checks if the username is in the group the rule applies to.
                                sec_running = time.time() - float(proc['proc_birth'])
                                if((counted[proc['pid']] >= helptext[2]) and (sec_running > helptext[1])):
                                    violations[proc['pid']] = (helptext[5], proc['username'], proc['fullname'], host, helptext[4])
                                    #TODO: Do something here to save interval for this proc pid.
        except IOError as e:
            print(e)
            print('Rules file or Groups file does not exist. Creating empty Rules/Groups file.') #Also split this up?
            f = open(OwnPath + 'Rules', 'w+')
            f.close();
            f = open(OwnPath + 'Groups', 'w+')
            f.close();    
            
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
