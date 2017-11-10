#!/bin/python3

import subprocess
import xml.etree.ElementTree as ET
import pwd
import socket
import threading
import copy
import time
import json
import logging


class GPUMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
        self.process_data = []
        self.gpu_data = []
        self.running = True

        self.start()

    def get_uid_from_pid(self, pid):
        filename = '/proc/' + pid + '/status'
        with open(filename) as f:
            for line in f:
                line = line.rstrip()
                segments = line.split()
                if segments[0] == 'Uid:':
                    return ','.join(segments[1:])


    def get_username_fullname(self, uid):
        user = pwd.getpwuid(int(uid.split(',')[0]))
        return [user.pw_name, user.pw_gecos]


    def get_logged_in(self, username):
        users = subprocess.Popen(['/usr/bin/users'], stdout=subprocess.PIPE)
        data = str(users.stdout.read(), 'UTF-8')
        segments = data.split()
        if username in segments:
            return 'true'
        else:
            return 'false'


    def get_proc_birth(self, pid):
        filename = '/proc/' + pid + '/stat'
        with open(filename) as f:
            line = f.read()
            line = line.rstrip()
            segments = line.split(maxsplit=1)[1]
            segments = segments.split(')')[1]
            segments = segments.lstrip()
            segments = segments.split()
            return segments[19]  # 22th element, but we cut the first two


    def parse_process_info(self, process_info, gpu):
        result = {}

        result['pid'] = process_info.find('pid').text
        result['process_name'] = process_info.find('process_name').text
        result['used_memory'] = process_info.find('used_memory').text
        result['gpu_id'] = gpu.attrib['id']
        result['gpu_name'] = gpu.find('product_name').text
        result['uid'] = self.get_uid_from_pid(result['pid'])
        result['username'], result['fullname'] = self.get_username_fullname(result['uid'])
        result['logged_in'] = self.get_logged_in(result['username'])
        result['proc_birth'] = self.get_proc_birth(result['pid'])

        return result


    def run(self):
        running = True
        while running:
            result = []

            nvidia_smi  = subprocess.Popen(['/usr/bin/nvidia-smi', '-x', '-q'], stdout=subprocess.PIPE)
            data = nvidia_smi.stdout.read()
            data = str(data, 'UTF-8')
            root = ET.fromstring(data)
            for gpu in root.iter('gpu'):
                for process in gpu.iter('processes'):
                    for process_info in process:
                        result.append(self.parse_process_info(process_info, gpu))

            with self.lock:
                # TODO is deepcopy necessary
                logging.debug('New \'schmiie\' is now available')
                self.process_data = copy.deepcopy(result)
                running = self.running

            # TODO define constant somewhere
            time.sleep(10)

    # public
    def close(self):
        with self.lock:
            self.running = False
        self.join()

    # public
    def get_process_data(self):
        '''
        with self.lock:
            return self.process_data
        '''
        tmp = []
        with self.lock:
            tmp = self.process_data
        return tmp
    
    # public
    def get_gpu_data(self):
        tmp = []
        with self.lock:
            tmp = self.gpu_data
        return tmp


class ConnectionHandler(threading.Thread):
    def __init__(self, gpu_monitor, client_conn, client_addr):
        threading.Thread.__init__(self)

        self.gpu_monitor = gpu_monitor
        self.client_conn = client_conn
        self.client_addr = client_addr

        self.start()


    def recvcmd(self):
        # TODO return None only one connection close
        MAXCMDLEN = 40
        command = ''
        while True:
            char = str(self.client_conn.recv(1), 'ascii')
            # closed
            if char == '':
                return None

            if char == '\n':
                break

            command += char

            if len(command) > MAXCMDLEN:
                return ''

        return command


    def send_string(self, string):
        raw_data = bytes(str(len(string)) + ' ' + string + '\n', 'ascii')

        send_bytes = 0
        while send_bytes < len(raw_data):
            send_bytes += self.client_conn.send(raw_data[send_bytes:])


    def send_process_data(self):
        pdata = self.gpu_monitor.get_process_data()
        json_str = json.dumps(pdata)
        self.send_string(json_str)


    def send_gpu_data(self):
        pdata = self.gpu_monitor.get_gpu_data()
        json_str = json.dumps(pdata)
        self.send_string(json_str)


    def run(self):
        logging.info('New connection opened id: ' + str(self.ident))

        while True:
            command = self.recvcmd()
            if command is None:
                break

            # function map?
            if command == 'GET_PROCESS_DATA':
                self.send_process_data()
            elif command == 'GET_GPU_DATA':
                self.send_gpu_data()
            else:
                logging.warning('Invalid cmd received')
                break

        self.client_conn.close()
        logging.info('Connection closed id: ' + str(self.ident))


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('GPU monitor is starting up')

    gpu_monitor = GPUMonitor()

    sock_addr = '/home/s1485873/monitor.socket'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(sock_addr)
    sock.listen(10)

    logging.info('Waiting for connections')
    try:
        while True:
            client_conn, client_addr = sock.accept()
            client_worker = ConnectionHandler(gpu_monitor, client_conn, client_addr)
    except KeyboardInterrupt:
        logging.info('shutting down monitor')
        gpu_monitor.close()


if __name__ == '__main__':
    main()

