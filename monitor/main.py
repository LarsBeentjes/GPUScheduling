#!/bin/python3

import socket
import logging
import os
import threading
import stat

from GPUMonitor import GPUMonitor
from ConnectionHandler import ConnectionHandler


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('GPU monitor is starting up')

    gpu_monitor = GPUMonitor()

    sock_addr = '/tmp/monitor.socket'
    try:
        os.unlink(sock_addr)
    except:
        pass
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(sock_addr)
    os.chmod(sock_addr, stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    sock.listen(10)

    logging.info('Waiting for connections')
    try:
        while True:
            client_conn, client_addr = sock.accept()
            client_worker = ConnectionHandler(gpu_monitor, client_conn, client_addr)
    except KeyboardInterrupt:
        logging.info('shutting down monitor')

    sock.close()
    gpu_monitor.close()

    #  there are only connetion threads left, wait for them to close before closing the
    #  main thread
    logging.info('Waiting for active connections to close')
    for thread in threading.enumerate():
        if thread.isDaemon():
            thread.join()


if __name__ == '__main__':
    main()

