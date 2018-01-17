#!/bin/python3

import math
import sys
import time
import socket

from MonitorClient import MonitorClient

SOCKET_ADDR = '/tmp/monitor.socket'

def print_help():
    help_text = '''\
--help, -h      Print this message

To kill one of your processes use 'kill [pid]' or if this does
not work 'kill -9 [pid]'.

If you want to keep the view board updating automatically try:
'watch -n 1 gpuview'.

If you want to keep terminal clutter to a minimum try:
'gpuview | less'
'''
    print(help_text, end='')


def find_gpu(gpus, gpu_id):
    for gpu in gpus:
        if gpu['id'] == gpu_id:
            return gpu
    return None


def is_gpu_available(gpu_id, processes):
    for proc in processes:
        if gpu_id == proc['gpu_id']:
            return False
    return True


def hms_time(time_seconds):
    t = round(time_seconds)
    seconds = t % 60
    t //= 60
    minutes = t % 60
    t //= 60
    hours = t

    return '{}:{:0>2}:{:0>2}'.format(hours, minutes, seconds)



def print_gpu(state, gpu, name, utilization, ram):
    print('{:<10} {:<4} {:<20} {:<13} {}'.format(state, gpu, name, utilization, ram))


def print_user(fullname, username, minor_number, utilization, pid, runtime, proc_name):
    fullname_width = 15
    proc_name_width = 31 - fullname_width
    print('{:<{}} {:<10} {:<4} {:<13} {:<7} {:<9} {}'.format(fullname[:fullname_width],
        fullname_width, username, minor_number, utilization, pid, runtime, proc_name[:proc_name_width]))


def main():
    if len(sys.argv) > 1:
        print_help()
        return

    monitor_client = MonitorClient(SOCKET_ADDR)

    last_ts = time.localtime(monitor_client.get_time_data()['last'])
    time_string = time.strftime('%H:%M:%S %d-%m-%Y', last_ts)
    print("Server: {} ({})".format(socket.gethostname(), time_string))

    gpus = monitor_client.get_gpu_data()
    processes = monitor_client.get_process_data()

    print('{:*^80}'.format('GPUS'))
    print_gpu('State', 'GPU', 'Name', 'Utilization', 'RAM')
    for gpu in gpus:
        if is_gpu_available(gpu['id'], processes):
            state = 'Available'
        else:
            state = 'In use'
        print_gpu(state, gpu['minor_number'], gpu['name'],
                gpu['gpu_utilization'], gpu['mem_utilization'])

    print('{:*^80}'.format('PROCESSES'))
    print_user('Fullname', 'username', 'GPU', 'Utilization', 'PID', 'Runtime', 'command')
    for proc in processes:
        gpu = find_gpu(gpus, proc['gpu_id'])
        runtime = hms_time(time.time() - float(proc['proc_birth']))
        print_user(proc['fullname'], proc['username'], gpu['minor_number'],
                gpu['gpu_utilization'], proc['pid'], runtime, proc['process_name'])
    print('{:*^80}'.format(''))


if __name__ == '__main__':
    main()
