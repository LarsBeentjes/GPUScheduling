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

def hours_minutes_seconds(int):
    m, s = divmod(int, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    s = "%d %02d:%02d:%02d" % (d, h, m, s)
    return s


def main(stdscr):
    monitor_client = MonitorClient('/home/s1485873/monitor.socket')

    while True:
        stdscr.clear()
        stdscr.addstr('This is the GPU overview board\n\n')
        for proc in monitor_client.get_process_data():
            stdscr.addstr('User: {}\nLogged in: {}\nFull name: {}\nProccess' 
            'name: {}\nprocess Processing time: {}\nGraphics card: {} \n\n'
            .format(proc['username'], proc['logged_in'],proc['fullname'], 
            proc['process_name'], hours_minutes_seconds(int(float(time.time())
            - float(proc['proc_birth']))), proc['gpu_name']))
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

