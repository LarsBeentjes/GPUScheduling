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
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    return False

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
        intervals = {}
        pids = set()
        data = monitor_client.get_process_data()
        counted = Counter(data['pid'])			#I'm reasonably sure the monitor client returns a dictionary and that this should work.
							#But not entirely certain. Can someone check this?
							#Here for efficiency.					
        try:
            with open(OwnPath + 'Rules', 'r') as Rulesfile:
                for line in Rulesfile:
                    bool ruleapplies = False	#The only time this doesn't happen is if the group is invalid or it's not a valid rule.
                    bool thisisexcept = False
                    helptext = line.split()
                    helptext2 = helptext
                    if(len(helptext) < 7):	
                        continue	#Thusly, is not a valid rule.
                    if(is_int(helptext[2]) and is_int(helptext[3]) and is_int(helptext[4]) and is_int(helptext[6])):
                        if(helptext[0] == 'EXCEPT'):
                            thisisexcept = True
                        with open(OwnPath + 'Groups', 'r') as Groupsfile:
                            for grouplines in Groupsfile:
                                grouphelp = grouplines.split()
                                if(grouphelp[0] == helptext[1]): #The group name matches
                                    ruleapplies = True
                                    helptext2 = grouphelp
                                    break
                                else:
                                    continue
                    else:
                        continue #Also checking if a valid rule.
                    if(ruleapplies):
                        for proc in data:
                            if((not thisisexcept and (proc['username'] in helptext2)) or (thisisexcept and (proc['username'] not in helptext2))): #Checks if the username is in the group the rule applies to.
                                sec_running = time.time() - float(proc['proc_birth'])											#Or not in the group in case of an EXCEPT.
                                if((counted[proc['pid']] >= helptext[2]) and (sec_running > helptext[1])):
                                    violations[proc['pid']] = (helptext[6], proc['username'], proc['fullname'], host, helptext[5])
                                    intervals[proc['pid']] = helptext[4]
        except IOError as e:
            print(e)
            print('Rules file or Groups file does not exist. Creating empty Rules/Groups file.') #Also split this up?
            f = open(OwnPath + 'Rules', 'w+')
            f.close();
            f = open(OwnPath + 'Groups', 'w+')
            f.write('EMPTYGROUP\n')				#Empty group should always be in it.
            f.close();    
            
        if not violations:
            print("There have been no violations")
        else:
            print("violations detected!")
            for pid in violations:
                user = violations[pid][1]
                last_seconds = 0
                firstnotification = True
                if user in notified: 
                    last_seconds = (notified[user] - time.time())
                    firstnotification = False
                if ((last_seconds > intervals[pid]) or firstnotification): #Note current setup means the user will not be sent multiple mails if they violate multiple rules. Keep?
                    if not exception(user): #Is this really necessary with rules as they are?
                        mailer.sendamail(*violations[pid])
                        print(user + " has been notified.")
                        print("last notification was " + str(last_hours) + " ago.")
                        notified[user] = time.time()
        
        time.sleep(10.0)
        
if __name__ == '__main__':
    main()
