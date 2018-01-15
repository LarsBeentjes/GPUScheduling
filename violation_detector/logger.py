import time

from config import get_config
from utility import get_timestring
from vd_exception import VDException

LOGGER = None


def init_logger():
    global LOGGER
    if LOGGER is not None:
        raise VDException('Logger can only be initialized once')

    config = get_config()
    LOGGER = Logger(config.get('logfile'), config.get('dup_log_to_stdout'))


def get_logger():
    if LOGGER is None:
        raise VDException('Logger not initialzed')

    return LOGGER


class Logger:
    def __init__(self, logfile, to_stdout):
        self.m_logfile = open(logfile, 'a')
        self.m_to_stdout = to_stdout


    def msg(self, msg):
        timestr = get_timestring()
        complete_msg = '[{}] {}\n'.format(timestr, msg)
        if self.m_to_stdout:
            print(complete_msg, end='')
        self.m_logfile.write(complete_msg)

