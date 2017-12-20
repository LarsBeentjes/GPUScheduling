#!/usr/bin/env python3

import curses
import time
import json
import sys
from curses import wrapper

sys.path.insert(0, '../monitor_client')
from MonitorClient import MonitorClient

def time_epilapsed(int):
    m, s = divmod(int, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    
    s = "%d %02d:%02d:%02d" % (d, h, m, s)
    return s

def textmid(s,width):
	return int((width/2)-(len(s)/2))

def main (self):
	monitor_client = MonitorClient('/home/s1485873/monitor.socket')

	curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
	curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
	curses.init_pair(3,curses.COLOR_WHITE,curses.COLOR_RED)
	self.refresh()

	height,width = self.getmaxyx()
	s = 'Welcome to the GPU-monitor viewboard'
	d = 'Here you can see all the users for Duranium'
	a = 'Their processes and time of use as well as the videocard in use'
	w = 'Press [ENTER] to continue'
	self.addstr(0,textmid(s,width),s + '\n\n')
	self.addstr(1,textmid(d,width),d + '\n\n')
	self.addstr(2,textmid(a,width),a + '\n\n')
	self.addstr(3,textmid(w,width),w + '\n\n')

	pad = curses.newpad((len(monitor_client.get_process_data())+10)*7,width)
	pad_pos = 0;
	pad.refresh(0,0,5,5,height-5,width-5)
	while True:
		for proc in monitor_client.get_process_data():
			try:
				for j in range (5,width-5):
					pad.addstr('-')
				pad.addstr('\n\n')
				pad.addstr('User: ' + proc['fullname'] + ' ' + 'Student ID:' +proc['uid']+'\n',curses.color_pair(1))
				pad.addstr('Process name: ' + proc['process_name'] + ' ' + 'GPU in use: ' + proc['gpu_name']+'\n',curses.color_pair(2))
				pad.addstr('Elapsed time: '+ 'time: ' + time_epilapsed(int(float(time.time()))-float(proc['proc_birth'])) + '\n\n',curses.color_pair(3))
			except curses.error:
				pass
		key = self.getch()
		if key == curses.KEY_DOWN:
			if pad_pos <= ((len(monitor_client.get_process_data())*7)+10)-height :
				pad_pos += 1
			pad.refresh(pad_pos,0,5,5,(height-5),width-5)
		elif key == curses.KEY_UP:
			if pad_pos >= 0:
				pad_pos -= 1
			pad.refresh(pad_pos,0,5,5,(height-5),width-5)
		pad.refresh(pad_pos,0,5,5,(height-5),width-5)


wrapper(main)

