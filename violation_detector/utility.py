import re
import time


def is_student(username):
    return bool(re.match('^s[0-9]+$', username))


def get_timestring():
    return time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
