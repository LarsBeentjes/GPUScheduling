import subprocess
import xml.etree.ElementTree as ET
import pwd
import threading
import time
import logging


class GPUMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
        self.process_data = []
        self.gpu_data = []

        self.running_condition = threading.Condition()
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


    def parse_gpu_info(self, gpu):
        result = {}

        result['id'] = gpu.attrib['id']
        result['name'] = gpu.find('product_name').text
        result['memory_usage'] = gpu.find('fb_memory_usage').find('used').text
        result['memory_total'] = gpu.find('fb_memory_usage').find('total').text
        result['gpu_utilization'] = gpu.find('utilization').find('gpu_util').text
        result['mem_utilization'] =  gpu.find('utilization').find('memory_util').text

        return result


    def interruptableWait(self):
        WAIT_TIME = 10.0  # seconds

        self.running_condition.acquire()
        self.running_condition.wait(WAIT_TIME)
        result = self.running
        self.running_condition.release()

        return result


    def run(self):
        while self.interruptableWait():
            result_process = []
            result_gpu = []

            nvidia_smi  = subprocess.Popen(['/usr/bin/nvidia-smi', '-x', '-q'], stdout=subprocess.PIPE)
            data = nvidia_smi.stdout.read()
            data = str(data, 'UTF-8')
            root = ET.fromstring(data)
            for gpu in root.iter('gpu'):
                for process in gpu.iter('processes'):
                    result_gpu.append(self.parse_gpu_info(gpu))
                    for process_info in process:
                        result_process.append(self.parse_process_info(process_info, gpu))

            with self.lock:
                logging.debug('New \'schmiie\' is now available')
                self.process_data = result_process
                self.gpu_data = result_gpu


    # public
    def close(self):
        self.running_condition.acquire()
        self.running = False
        self.running_condition.notifyAll()
        self.running_condition.release()

        self.join()


    # public
    def get_process_data(self):
        result = []
        with self.lock:
            result = self.process_data
        return result


    # public
    def get_gpu_data(self):
        result = []
        with self.lock:
            result = self.gpu_data
        return result

