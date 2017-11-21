import socket
import json


class UnexpectedConnectionEnd(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return 'Connection ended prematurely'


class MonitorClient:
    def __init__(self, socket_addr):
        self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection.connect(socket_addr)

    def __send_command(self, command):
        raw_data = bytes(command + '\n', 'ascii')

        bytes_send = 0
        while bytes_send < len(raw_data):
            bytes_send += self.connection.send(raw_data[bytes_send:])

    def __recv_msg(self):
        # receive message length
        msg_length = ''
        char = None
        while char != ' ':
            char = str(self.connection.recv(1), 'ascii')
            if len(char) == '':
                raise UnexpectedConnectionEnd()
            msg_length += char

        msg_length = int(msg_length)

        # recv actual message
        bytes_recvd = 0
        data = bytes()
        while bytes_recvd < msg_length:
            recvd_data = self.connection.recv(msg_length - bytes_recvd)
            if len(recvd_data) == 0:
                raise UnexpectedConnectionEnd()
            data += recvd_data
            bytes_recvd += len(recvd_data)

        # read tailing new line
        if len(self.connection.recv(1)) != 1:
            raise UnexpectedConnectionEnd()

        message = str(data, 'ascii')
        return json.loads(message)

    def get_process_data(self):
        self.__send_command('GET_PROCESS_DATA')
        return self.__recv_msg()

    def get_gpu_data(self):
        self.__send_command('GET_GPU_DATA')
        return self.__recv_msg()

    def get_time_data(self):
        self.__send_command('GET_TIME_DATA')
        return self.__recv_msg()

