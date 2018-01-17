#!/bin/python3

import socket
import logging
import os
import threading
import stat

from GPUMonitor import GPUMonitor
from ConnectionHandler import ConnectionHandler


SOCKET_ADDR = '/tmp/monitor.socket'


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('GPU monitor is starting up')

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(SOCKET_ADDR)
        os.chmod(SOCKET_ADDR, stat.S_IROTH | stat.S_IWOTH | stat.S_IRGRP |
                stat.S_IWGRP | stat.S_IRUSR | stat.S_IWUSR)
        sock.listen(10)
    except Exception as e:
        logging.error('Failed to setup socket: {}'.format(str(e)))
        logging.info('Try removing "{}" if no other instance of the monitor is running'.format(SOCKET_ADDR))
        return

    gpu_monitor = GPUMonitor()

    logging.info('Waiting for connections')
    try:
        while True:
            client_conn, client_addr = sock.accept()
            client_worker = ConnectionHandler(gpu_monitor,
                    client_conn, client_addr)
    except KeyboardInterrupt:
        logging.info('shutting down monitor')

    os.remove(SOCKET_ADDR)
    sock.close()
    gpu_monitor.close()

    #  there are only connetion threads left, wait for them to close before
    # closing the main thread
    logging.info('Waiting for active connections to close')
    for thread in threading.enumerate():
        if thread.isDaemon():
            thread.join()


if __name__ == '__main__':
    main()

