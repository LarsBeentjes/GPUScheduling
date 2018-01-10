#!/bin/python3

import math
import sys
import time

sys.path.insert(0, '../../monitor_client')
from MonitorClient import MonitorClient


def tabber_de_tab(string):
    TABWIDTH = 30
    if len(string) >= 20:
        string = string[:TABWIDTH - 4]
        string += '...'

    return string + (' ' * (TABWIDTH - len(string)))


def stertjes(string):
    if len(string) >= 80:
        return string

    pre = 40 - math.ceil(len(string) / 2)
    post = 40 - math.floor(len(string) / 2)

    return ('*' * pre) + string + ('*' * post)


def main():
    SOCKET_ADDR = '/tmp/monitor.socket'

    monitor_client = MonitorClient(SOCKET_ADDR)

    print(stertjes('LAST UPDATE'))
    last_ts = time.localtime(monitor_client.get_time_data()['last'])
    time_string = time.strftime('%H:%M:%S %d-%m-%Y (hh:mm:ss dd:mm:yyyy localtime)', last_ts)
    print(time_string)

    print(stertjes('CARDS'))
    for gpu in monitor_client.get_gpu_data():
        output = tabber_de_tab(gpu['name'])
        #output += tabber_de_tab(gpu['id'])
        output += tabber_de_tab(gpu['minor_number'])
        output += tabber_de_tab(gpu['gpu_utilization'])
        print(output)

    print(stertjes('PROCESSES'))
    for process in monitor_client.get_process_data():
        output = tabber_de_tab(process['fullname'])
        output += tabber_de_tab(process['process_name'])
        output += tabber_de_tab(process['gpu_minor_number'])
        print(output)

    print(stertjes(''))

if __name__ == '__main__':
    main()
