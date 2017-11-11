import threading
import json
import logging


class ConnectionHandler(threading.Thread):
    def __init__(self, gpu_monitor, client_conn, client_addr):
        threading.Thread.__init__(self)

        self.gpu_monitor = gpu_monitor
        self.client_conn = client_conn
        self.client_addr = client_addr

        self.start()


    def __recv_cmd(self):
        MAXCMDLEN = 40
        command = ''
        while True:
            char = str(self.client_conn.recv(1), 'ascii')
            #  closed
            if char == '':
                return None

            if char == '\n':
                break

            command += char

            if len(command) > MAXCMDLEN:
                return ''

        return command


    def __send_message(self, message):
        raw_data = bytes(str(len(message)) + ' ' + message + '\n', 'ascii')

        send_bytes = 0
        while send_bytes < len(raw_data):
            send_bytes += self.client_conn.send(raw_data[send_bytes:])


    def __send_process_data(self):
        pdata = self.gpu_monitor.get_process_data()
        json_str = json.dumps(pdata)
        self.__send_message(json_str)


    def __send_gpu_data(self):
        pdata = self.gpu_monitor.get_gpu_data()
        json_str = json.dumps(pdata)
        self.__send_message(json_str)


    def run(self):
        logging.info('New connection opened id: ' + str(self.ident))

        while True:
            command = self.__recv_cmd()
            if command is None:
                break

            # function map?
            if command == 'GET_PROCESS_DATA':
                self.__send_process_data()
            elif command == 'GET_GPU_DATA':
                self.__send_gpu_data()
            else:
                logging.warning('Invalid cmd received')
                break

        self.client_conn.close()
        logging.info('Connection closed id: ' + str(self.ident))

