import sys

from config import init_config
from logger import init_logger
from logger import get_logger
from application import Application
from vd_exception import VDException


def setup():
    try:
        init_config(sys.argv[1])
        init_logger()
    except VDException as e:
        print('While setting up: "{}"'.format(str(e)))
        return False
    return True


def main():
    if len(sys.argv) != 2:
        print('usage: {} [configfile]'.format(sys.argv[0]))
        return

    if not setup():
        return

    try:
        app = Application()
    except VDException as e:
        print('Failed to create Application "{}"'.format(str(e)))
        return

    logger = get_logger()

    logger.msg('Mail client is now running')
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    logger.msg('Mail client shutting doen')


if __name__ == '__main__':
    main()
