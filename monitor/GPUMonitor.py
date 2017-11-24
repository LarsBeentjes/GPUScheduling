import logging
import os
import pwd
import subprocess
import threading
import time
import xml.etree.ElementTree as ET


def get_boot_time():
    with open('/proc/stat') as fp:
        for line in fp:
            segments = line.split()
            if segments[0] == 'btime':
                return float(segments[1])

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

        birth = float(segments[19])  # 22th element, but we cut the first two
        birth /= os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        return str(get_boot_time() + birth)

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

def parse_gpu_info(gpu):
    result = {}

    result['id'] = gpu.attrib['id']
    result['name'] = gpu.find('product_name').text
    result['memory_usage'] = gpu.find('fb_memory_usage').find('used').text
    result['memory_total'] = gpu.find('fb_memory_usage').find('total').text
    result['gpu_utilization'] = gpu.find('utilization').find('gpu_util').text
    result['mem_utilization'] =  gpu.find('utilization').find('memory_util').text

    return result


class GPUMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
        self.process_data = []
        self.gpu_data = []
        self.time_data = 0.0

        self.running_condition = threading.Condition()
        self.running = True

        self.start()

    def __interruptable_wait(self):
        WAIT_TIME = 10.0  # seconds

        self.running_condition.acquire()
        self.running_condition.wait(WAIT_TIME)
        result = self.running
        self.running_condition.release()

        return result

    def __poll(self):
        result_process = []
        result_gpu = []

        nvidia_smi  = subprocess.Popen(['/usr/bin/nvidia-smi', '-x', '-q'], stdout=subprocess.PIPE)
        data = nvidia_smi.stdout.read()
        data = str(data, 'UTF-8')
        root = ET.fromstring(data)
        for gpu in root.iter('gpu'):
            for process in gpu.iter('processes'):
                result_gpu.append(parse_gpu_info(gpu))
                for process_info in process:
                    try:
                        result_process.append(parse_process_info(process_info, gpu))
                    except FileNotFoundError as e:
                        logging.debug('Process ended while looking up state')
                        logging.debug(str(e))
                    except Exception as e:
                        logging.warning('Unknown error while looking up state')
                        logging.warning(e, exc_info=True)


        with self.lock:
            self.process_data = result_process
            self.gpu_data = result_gpu
            self.time_data = time.time()

    def run(self):
        while self.__interruptable_wait():
            try:
                self.__poll()
            except Exception as e:
                logging.warning("Unexpected exception happened while polling for data")
                logging.warning(e, exc_info=True)

    def close(self):
        self.running_condition.acquire()
        self.running = False
        self.running_condition.notifyAll()
        self.running_condition.release()

        self.join()

    def get_process_data(self):
        result = []
        with self.lock:
            result = self.process_data
        return result

    def get_gpu_data(self):
        result = []
        with self.lock:
            result = self.gpu_data
        return result

    def get_time_data(self):
        result = {}
        with self.lock:
            result['last'] = self.time_data
        return result

