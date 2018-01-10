#!/usr/bin/env python3

import curses
import time
import json
import sys
from curses import wrapper

sys.path.insert(0, '../monitor_client')
from MonitorClient import MonitorClient

def time_epilapsed(delta_time):
    m, s = divmod(delta_time, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    s = "%d %02d:%02d:%02d" % (d, h, m, s)
    return s

def textmid(s,width):
    return int((width/2)-(len(s)/2))

def draw_screen(screen, pad, monitor_client, pad_pos):
    height, width = screen.getmaxyx()
    pad.clear()
    #screen.clear()

    # draw banner
    welcome_text = [
        'Welcome to the GPU-monitor viewboard',
        'Here you can see all the users for Duranium',
        'Their processes and time of use as well as the videocard in use',
        ''
    ]
    for line_nr, line in enumerate(welcome_text):
        screen.addstr(line_nr, textmid(line,width), line)

    # draw procesess
    for proc in monitor_client.get_process_data():
        for j in range (5,width-5):
            pad.addstr('-')
        pad.addstr('\n\n')
        pad.addstr('User: ' + proc['fullname'] + ' ' + 'Student ID:' +proc['uid'].split(',')[0]+'\n',curses.color_pair(1))
        pad.addstr('Process name: ' + proc['process_name'] + ' ' + 'GPU in use: ' + proc['gpu_name']+'\n',curses.color_pair(2))
        pad.addstr('Elapsed time: '+ 'time: ' + time_epilapsed(int(float(time.time()))-float(proc['proc_birth'])) + '\n\n',curses.color_pair(3))

        pad.refresh(pad_pos,0,5,5,(height-5),width-5)
        screen.refresh()

def main (self):
    monitor_client = MonitorClient('/tmp/monitor.socket')

    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_WHITE,curses.COLOR_RED)
    self.timeout(100)

    height, width = self.getmaxyx()
    pad = curses.newpad((len(monitor_client.get_process_data())+10)*7,width)
    pad_pos = 0;
    pad.refresh(0,0,5,5,height-5,width-5)
    while True:
        key = self.getch()
        if key == curses.KEY_DOWN:
            if pad_pos <= ((len(monitor_client.get_process_data())*7)+10)-height :
                pad_pos += 1
        elif key == curses.KEY_UP:
            if pad_pos >= 0:
                pad_pos -= 1
        draw_screen(self, pad, monitor_client, pad_pos)


try:
    wrapper(main)
except KeyboardInterrupt:
    print('bye.')