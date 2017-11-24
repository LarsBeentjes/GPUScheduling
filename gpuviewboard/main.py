#!/bin/python3

import curses
import time
import sys
import json

sys.path.insert(0, '../monitor_client')
from MonitorClient import MonitorClient

def uptime():                                                                                                        
    uptime = 0.0
    with open('/proc/uptime') as fp:
        line = fp.readline()
        segments = line.split()
        uptime = float(segments[0])
    return uptime

def main(stdscr):
    monitor_client = MonitorClient('/home/s1485873/monitor.socket')

    while True:
        stdscr.clear()
        stdscr.addstr('This is the GPU overview board\n\n')
        for proc in monitor_client.get_process_data():
            stdscr.addstr('user: {}\nfull name: {}\nproccess name: {}\nprocess time: {}\n\n'.format(proc['username'],
                proc['fullname'], proc['process_name'],
                time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(float(proc['proc_birth'])))))
            #De tijd is nog een beetje van slag omdat De Jonckheere daar lugubere dingen mee heeft gedaan
            #De tijd is getraumatiseerd zou je kunnen zeggen
        stdscr.refresh()
        time.sleep(1.0)


if __name__ == '__main__':
    scr = curses.initscr()
    try:
        main(scr)
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()

