#!/bin/python3

import subprocess
import xml.etree.ElementTree as ET
import pwd
import socket


def get_uid_from_pid(pid):
    filename = '/proc/' + pid + '/status'
    with open(filename) as f:
        for line in f:
            line = line.rstrip()
            segments = line.split()
            if segments[0] == 'Uid:':
                return ','.join(segments[1:])


def get_username_fullname(uid):
    user = pwd.getpwuid(int(uid.split(',')[0]))
    return [user.pw_name, user.pw_gecos]


def get_logged_in(username):
    users = subprocess.Popen(['/usr/bin/users'], stdout=subprocess.PIPE)
    data = str(users.stdout.read(), 'UTF-8')
    segments = data.split()
    if username in segments:
        return 'true'
    else:
        return 'false'


def get_proc_birth(pid):
    filename = '/proc/' + pid + '/stat'
    with open(filename) as f:
        line = f.read()
        line = line.rstrip()
        segments = line.split(maxsplit=1)[1]
        segments = segments.split(')')[1]
        segments = segments.lstrip()
        segments = segments.split()
        return segments[19]  # 22th element, but we cut the first two


def parse_process_info(process_info, gpu):
    result = {}

    result['pid'] = process_info.find('pid').text
    result['process_name'] = process_info.find('process_name').text
    result['used_memory'] = process_info.find('used_memory').text
    result['gpu_id'] = gpu.attrib['id']
    result['gpu_name'] = gpu.find('product_name').text
    result['uid'] = get_uid_from_pid(result['pid'])
    result['username'], result['fullname'] = get_username_fullname(result['uid'])
    result['logged_in'] = get_logged_in(result['username'])
    result['proc_birth'] = get_proc_birth(result['pid'])

    return result


def get_gpu_data():
    result = []

    nvidia_smi  = subprocess.Popen(['/usr/bin/nvidia-smi', '-x', '-q'], stdout=subprocess.PIPE)
    data = nvidia_smi.stdout.read()
    data = str(data, 'UTF-8')
    root = ET.fromstring(data)
    for gpu in root.iter('gpu'):
        for process in gpu.iter('processes'):
            for process_info in process:
                result.append(parse_process_info(process_info, gpu))

    return result


def main():
    '''
    sock_addr = '/home/s1485873/monitor.socket'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(sock_addr)
    sock.listen(10)

    while True:
        client_conn, client_addr = sock.accept()
        c = None
        s = ''
        while c != '\n':
            c = str(client_conn.recv(1), 'UTF-8')
            s += c
        print(s)
    client_conn.close()
    '''

    print(get_gpu_data())


if __name__ == '__main__':
    main()

