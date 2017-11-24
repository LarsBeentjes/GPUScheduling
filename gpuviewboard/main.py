#!/bin/python3

import curses
import time
import sys

sys.path.insert(0, '../monitor_client')
from MonitorClient import MonitorClient

def main(stdscr):
    monitor_client = MonitorClient('/home/s1485873/monitor.socket')

    while True:
        stdscr.clear()
        stdscr.addstr('This is the GPU overview board\n\n')
        for proc in monitor_client.get_process_data():
            stdscr.addstr('user {0}  {0} proc {1}\n'.format(proc['fullname'], proc['process_name']))
            
        stdscr.refresh()
        time.sleep(1.0)


if __name__ == '__main__':
    scr = curses.initscr()
    try:
        main(scr)
    finally:
        curses.endwin()
